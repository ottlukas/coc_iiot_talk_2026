"""
Prepares the build directory, compiles AsciiDoc to Reveal.js HTML via Docker, and handles styling post-processing.
"""

import logging
import os
import shutil
import stat
from pathlib import Path
from typing import List
from datetime import datetime
from . config import ExporterConfig, ImageReference
from . docker_utils import run_docker_command, format_docker_volume_path
from . asciidoc_parser import extract_images_dir, normalize_adoc_content

logger = logging.getLogger("exporter")

def prepare_build_directory(
    config: ExporterConfig,
    image_refs: List[ImageReference],
    build_dir: Path
) -> None:
    """
    Creates and populates the build directory with adoc source, custom css, docinfo, and images.
    If the build directory has permission issues, creates a timestamped backup and uses a fresh directory.
    """
    logger.info("Preparing clean build directory at: %s", build_dir)
    
    # 1. Clean and recreate build directory
    if build_dir.exists():
        # Helper to handle permission errors during deletion
        def handle_remove_error(func, path, exc_info):
            """Handle permission errors by attempting to change permissions and retry."""
            # Try to add write permissions and retry
            try:
                if os.path.isdir(path):
                    os.chmod(path, stat.S_IRWXU)  # Full owner permissions for directories
                else:
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)  # Write+read for files
                func(path)
                logger.debug("Removed after chmod: %s", path)
            except Exception as e:
                logger.warning("Could not remove %s: %s", path, str(e))
        
        def fix_permissions_recursive(path):
            """Recursively fix permissions before deletion."""
            try:
                for root, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        file_path = os.path.join(root, name)
                        try:
                            os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                        except Exception:
                            pass
                    for name in dirs:
                        dir_path = os.path.join(root, name)
                        try:
                            os.chmod(dir_path, stat.S_IRWXU)
                        except Exception:
                            pass
                # Fix root directory permissions
                os.chmod(path, stat.S_IRWXU)
            except Exception as e:
                logger.debug("Error fixing permissions recursively: %s", str(e))
        
        try:
            fix_permissions_recursive(build_dir)
            shutil.rmtree(build_dir, onerror=handle_remove_error)
        except Exception as e:
            logger.warning("Failed to remove build directory: %s. Attempting to clean contents instead.", str(e))
            # If full removal fails, try to clean just the key files we need
            try:
                for item in build_dir.iterdir():
                    if item.is_dir():
                        try:
                            shutil.rmtree(item, onerror=handle_remove_error)
                        except Exception:
                            logger.warning("Could not remove subdirectory: %s", item)
                    else:
                        try:
                            item.unlink()
                        except Exception:
                            logger.warning("Could not remove file: %s", item)
            except Exception as cleanup_error:
                logger.warning("Could not clean build directory contents: %s. Creating backup instead.", str(cleanup_error))
                # Last resort: backup the problematic directory
                backup_dir = build_dir.parent / f"presentation-export-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                try:
                    build_dir.rename(backup_dir)
                    logger.info("Backed up problematic build directory to: %s", backup_dir)
                except Exception as backup_error:
                    logger.error("Could not create backup: %s", backup_error)
                    raise RuntimeError(f"Cannot clean or backup build directory: {cleanup_error}") from backup_error
    
    build_dir.mkdir(parents=True, exist_ok=True)
    
    build_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copy and normalize source adoc file
    adoc_content = config.source_file.read_text(encoding="utf-8")
    imagesdir = extract_images_dir(adoc_content)
    normalized_content = normalize_adoc_content(adoc_content, imagesdir)
    
    build_adoc = build_dir / "presentation.adoc"
    build_adoc.write_text(normalized_content, encoding="utf-8")
    logger.debug("Wrote normalized presentation.adoc to build directory.")

    # 3. Copy docinfo.html if it exists next to source
    docinfo_src = config.source_file.parent / "docinfo.html"
    if docinfo_src.is_file():
        shutil.copy2(docinfo_src, build_dir / "docinfo.html")
        logger.debug("Copied docinfo.html to build directory.")

    # 4. Copy stylesheet to root of build directory
    if config.stylesheet_file.is_file():
        shutil.copy2(config.stylesheet_file, build_dir / "apache.css")
        logger.debug("Copied custom stylesheet to build directory as apache.css.")
    else:
        logger.warning("Custom stylesheet not found at %s", config.stylesheet_file)

    # 5. Create images directory and copy all referenced local images
    build_images_dir = build_dir / "images"
    build_images_dir.mkdir(parents=True, exist_ok=True)
    
    # Also copy all files from local images_dir just in case some are not matched by parse
    if config.images_dir.is_dir():
        for item in config.images_dir.iterdir():
            if item.is_file() and not item.name.startswith("."):
                shutil.copy2(item, build_images_dir / item.name)
        logger.debug("Copied base images from %s to build images directory.", config.images_dir)

    for ref in image_refs:
        if ref.is_valid and hasattr(ref, "resolved_path"):
            src_path = getattr(ref, "resolved_path")
            # Preserve subfolder structure if any, otherwise copy directly
            # For simplicity, copy directly to build_images_dir
            dest_path = build_images_dir / src_path.name
            try:
                shutil.copy2(src_path, dest_path)
                logger.debug("Copied validated image: %s -> %s", src_path.name, dest_path)
            except Exception as e:
                logger.error("Failed to copy image %s: %s", src_path.name, str(e))

def fetch_revealjs_assets(config: ExporterConfig, build_dir: Path) -> None:
    """
    Downloads and installs reveal.js assets into the build directory using a temporary Node container.
    """
    logger.info("Fetching reveal.js assets using a temporary Node Docker container...")
    vol_mount = f"{format_docker_volume_path(build_dir)}:/app"
    
    # Run npm install inside node container and copy assets out to /app/reveal.js
    cmd = [
        "docker", "run", "--rm",
        "-v", vol_mount,
        "-w", "/app",
        "node:20-slim",
        "sh", "-c",
        "npm install --no-audit --no-fund reveal.js@5.1.0 && "
        "mkdir -p reveal.js && "
        "cp -r node_modules/reveal.js/dist reveal.js/dist && "
        "cp -r node_modules/reveal.js/plugin reveal.js/plugin"
    ]
    
    exec_result = run_docker_command(cmd, timeout=config.timeout)
    config.output_dir.mkdir(parents=True, exist_ok=True)  # ensure logger / config paths exist
    
    if exec_result.exit_code != 0:
        logger.error("Failed to fetch reveal.js: %s", exec_result.stderr)
        raise RuntimeError("Failed to fetch reveal.js assets inside Node container.")
    
    logger.info("Successfully fetched and set up reveal.js assets.")

def compile_asciidoc_to_html(config: ExporterConfig, build_dir: Path) -> Path:
    """
    Runs the asciidoctor reveal.js compiler container against the build directory.
    Returns the Path to the compiled HTML file.
    """
    logger.info("Compiling AsciiDoc to Reveal.js HTML via docker-asciidoctor...")
    vol_mount = f"{format_docker_volume_path(build_dir)}:/documents"
    
    # We compile presentation.adoc to presentation.html
    cmd = [
        "docker", "run", "--rm",
        "-v", vol_mount,
        config.docker_image_asciidoctor,
        "asciidoctor-revealjs",
        "-a", "revealjs_theme=white",
        "-a", "revealjs_customtheme=apache.css",
        "-a", "imagesdir=images",
        "-a", "revealjsdir=reveal.js",
        "-o", "presentation.html",
        "presentation.adoc"
    ]
    
    exec_result = run_docker_command(cmd, timeout=config.timeout)
    # Save command details
    logger.debug("Asciidoctor compilation exit code: %d", exec_result.exit_code)
    
    # Also attach this execution to a global runner tracking if needed,
    # but the caller can extract it.
    if exec_result.exit_code != 0:
        logger.error("Asciidoctor compile failed: %s", exec_result.stderr)
        raise RuntimeError(f"Failed to compile AsciiDoc to HTML: {exec_result.stderr.strip()}")
        
    html_file = build_dir / "presentation.html"
    if not html_file.is_file():
        raise FileNotFoundError("Compiled HTML file presentation.html was not created in the build directory.")

    post_process_stylesheet(html_file)
    logger.info("AsciiDoc compilation successfully completed.")
    return html_file

def post_process_stylesheet(html_path: Path) -> None:
    """
    Inspects the compiled HTML and ensures apache.css is correctly linked.
    """
    logger.debug("Post-processing HTML for stylesheet references in: %s", html_path)
    html_content = html_path.read_text(encoding="utf-8")
    
    # Check if apache.css is linked in the HTML
    linked = "apache.css" in html_content
    
    if not linked:
        logger.warning("Custom theme stylesheet (apache.css) was not linked automatically. Injecting link fallback.")
        # Inject stylesheet before </head>
        fallback_link = '\n<link rel="stylesheet" href="apache.css" id="theme-fallback">\n'
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", f"{fallback_link}</head>")
        else:
            # Fallback if no head tag found
            html_content = html_content + fallback_link
        html_path.write_text(html_content, encoding="utf-8")
    else:
        logger.debug("Verified apache.css link is present in HTML.")
