#!/usr/bin/env python3
"""
Refactored Docker-based presentation PDF exporter using Decktape.
Exposes a command-line interface and coordinates the export pipeline.
"""

import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from exporter.config import ExporterConfig, ExportResult
from exporter.docker_utils import check_docker_availability
from exporter.asciidoc_parser import (
    parse_images_from_adoc,
    validate_and_resolve_images,
    parse_slides_and_notes,
)
from exporter.html_builder import (
    prepare_build_directory,
    fetch_revealjs_assets,
    compile_asciidoc_to_html,
)
from exporter.http_server import TempHTTPServer, wait_for_server_healthy
from exporter.decktape_exporter import export_slides_with_decktape
from exporter.pdf_utils import generate_notes_pdf_handout
from exporter.reporting import write_export_report

# ROOT dir of the project
ROOT_DIR = Path(__file__).resolve().parent

# Define logger
logger = logging.getLogger("exporter")

def setup_logging(output_dir: Path, verbose: bool = False) -> None:
    """Sets up dual logging: stdout/stderr and file handler in output directory."""
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Remove existing handlers
    for h in list(logger.handlers):
        logger.removeHandler(h)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (write to output/export.log)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        log_file = output_dir / "export.log"
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        logger.debug("Logging initialized. Writing file log to %s", log_file)
    except Exception as e:
        print(f"WARNING: Could not create log file: {str(e)}", file=sys.stderr)

def resolve_path(path_str: str) -> Path:
    """
    Resolve input paths robustly.
    Checks:
    1. If absolute, return directly
    2. If relative to current directory, return that
    3. Otherwise, check relative to project root
    """
    p = Path(path_str)
    if p.is_absolute():
        return p.resolve()
    
    cwd_candidate = Path.cwd() / p
    if cwd_candidate.exists():
        return cwd_candidate.resolve()
        
    return (ROOT_DIR / p).resolve()

def validate_pdf_file(pdf_path: Path) -> None:
    """Verifies that a generated PDF exists and has a non-zero size."""
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Expected PDF output was not created: {pdf_path}")
    if pdf_path.stat().st_size == 0:
        raise ValueError(f"Generated PDF file is empty (0 bytes): {pdf_path}")

def run_pipeline(config: ExporterConfig) -> ExportResult:
    """Runs the full export pipeline and returns details."""
    result = ExportResult(
        source_file=str(config.source_file.resolve()),
        status="failed"
    )

    try:
        # Step 1. Check Docker
        logger.info("Validating Docker daemon accessibility...")
        check_docker_availability()
        
        # Step 2. Validate input paths
        if not config.source_file.is_file():
            raise FileNotFoundError(f"Source file not found: {config.source_file}")
        if not config.images_dir.is_dir():
            raise FileNotFoundError(f"Images directory not found: {config.images_dir}")
        if not config.stylesheet_file.is_file():
            raise FileNotFoundError(f"Custom theme stylesheet not found: {config.stylesheet_file}")

        # Step 3. Parse and validate image references
        logger.info("Parsing and validating image references...")
        adoc_content = config.source_file.read_text(encoding="utf-8")
        all_img_refs = parse_images_from_adoc(adoc_content)
        
        valid_refs, missing_refs = validate_and_resolve_images(
            all_img_refs, config.source_file, config.images_dir
        )
        
        result.images_validation = {
            "total_images": len(all_img_refs),
            "missing_images": [
                {
                    "ref": ref.ref_path,
                    "line": ref.line_number,
                    "error": ref.error_message
                }
                for ref in missing_refs
            ],
            "warnings": []
        }

        if missing_refs:
            msg = f"Missing {len(missing_refs)} referenced image(s):"
            for ref in missing_refs:
                msg += f"\n  - Line {ref.line_number}: {ref.ref_path} ({ref.error_message})"
            
            if not config.ignore_missing_images:
                logger.error(msg)
                raise FileNotFoundError("Missing images validation failed. Aborting.")
            else:
                logger.warning(msg)
                result.images_validation["warnings"].append("Missing images ignored by flag.")

        # Step 4. Extract slide headings and notes
        logger.info("Parsing slide notes and headings...")
        notes_data = parse_slides_and_notes(adoc_content)
        logger.info("Successfully extracted notes for %d slides.", len(notes_data))

        # Step 5. Build directory preparation & Reveal.js fetching
        build_dir = ROOT_DIR / "build" / "presentation-export"
        prepare_build_directory(config, valid_refs, build_dir)
        fetch_revealjs_assets(config, build_dir)
        
        # Step 6. AsciiDoc to Reveal.js compile inside Docker
        compiled_html_path = compile_asciidoc_to_html(config, build_dir)
        
        # Copy compiled HTML to final output folder for debugging
        config.output_dir.mkdir(parents=True, exist_ok=True)
        debug_html_dest = config.output_dir / "presentation.html"
        shutil.copy2(compiled_html_path, debug_html_dest)
        result.outputs["presentation_html"] = str(debug_html_dest.resolve())
        logger.info("Saved presentation HTML for debugging at: %s", debug_html_dest)

        # Step 7. HTTP Serving and Decktape PDF Export
        slides_pdf_filename = "presentation.pdf"
        slides_pdf_path = config.output_dir / slides_pdf_filename
        
        with TempHTTPServer(build_dir) as server:
            wait_for_server_healthy(server.port, timeout=10.0)
            
            # Execute Decktape command
            cmd_result = export_slides_with_decktape(config, server.port, slides_pdf_filename)
            result.commands_executed.append(cmd_result)
            
            if cmd_result.exit_code != 0:
                raise RuntimeError(f"Decktape export failed: {cmd_result.stderr.strip()}")
                
        # Validate Slide-only PDF
        validate_pdf_file(slides_pdf_path)
        result.outputs["presentation_pdf"] = str(slides_pdf_path.resolve())

        # Step 8. Notes hand-out generation & PDF merging
        notes_pdf_filename = "presentation-with-notes.pdf"
        notes_pdf_path = config.output_dir / notes_pdf_filename
        
        success = generate_notes_pdf_handout(
            config=config,
            build_dir=build_dir,
            slides_pdf_path=slides_pdf_path,
            notes_data=notes_data,
            output_filename=notes_pdf_filename
        )
        
        if success:
            validate_pdf_file(notes_pdf_path)
            result.outputs["presentation_with_notes_pdf"] = str(notes_pdf_path.resolve())
        else:
            raise RuntimeError("Interleaving slides and speaker notes failed.")

        # Complete result
        result.status = "success"
        logger.info("--- PRESENTATION EXPORT PIPELINE COMPLETED SUCCESSFULLY ---")

    except Exception as e:
        logger.exception("Exporter pipeline encountered an error:")
        result.status = "failed"
        result.error_message = str(e)

    # Clean up build directory if run completed successfully
    try:
        build_dir = ROOT_DIR / "build" / "presentation-export"
        if build_dir.is_dir() and result.status == "success":
            shutil.rmtree(build_dir)
            logger.debug("Cleaned up build directory.")
    except Exception as e:
        logger.warning("Failed to clean up build directory: %s", str(e))

    return result

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite and stabilize Reveal.js presentation PDF exporter using Decktape."
    )
    parser.add_argument(
        "--source",
        default="docs/presentation.adoc",
        help="Path to the source AsciiDoc presentation (default: docs/presentation.adoc)"
    )
    parser.add_argument(
        "--images-dir",
        default="docs/images",
        help="Path to presentation images directory (default: docs/images)"
    )
    parser.add_argument(
        "--stylesheet",
        default="docs/theme/apache.css",
        help="Path to custom theme stylesheet (default: docs/theme/apache.css)"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to write export outputs (default: output)"
    )
    parser.add_argument(
        "--docker-image-decktape",
        default="astefanutti/decktape",
        help="Docker image for Decktape (default: astefanutti/decktape)"
    )
    parser.add_argument(
        "--docker-image-asciidoctor",
        default="asciidoctor/docker-asciidoctor",
        help="Docker image for Asciidoctor (default: asciidoctor/docker-asciidoctor)"
    )
    parser.add_argument(
        "--size",
        default="1920x1080",
        help="Viewport size for slide rendering (default: 1920x1080)"
    )
    parser.add_argument(
        "--pause",
        type=int,
        default=1000,
        help="Millis to pause after slide loading in Decktape (default: 1000)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds for Docker command runs (default: 120)"
    )
    parser.add_argument(
        "--ignore-missing-images",
        action="store_true",
        help="Ignore missing referenced images and proceed with export"
    )
    parser.add_argument(
        "--include-empty-notes",
        action="store_true",
        help="Include blank/empty speaker note pages in combined handout PDF"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed debug logs"
    )
    
    args = parser.parse_args()

    # Resolve paths
    source_file = resolve_path(args.source)
    images_dir = resolve_path(args.images_dir)
    stylesheet_file = resolve_path(args.stylesheet)
    output_dir = resolve_path(args.output_dir)

    # Initialize logging
    setup_logging(output_dir, args.verbose)
    logger.info("Initializing Presentation Export Pipeline...")
    logger.info("Source file resolved: %s", source_file)
    logger.info("Images directory resolved: %s", images_dir)
    logger.info("Stylesheet resolved: %s", stylesheet_file)
    logger.info("Output directory resolved: %s", output_dir)

    # Build config
    config = ExporterConfig(
        source_file=source_file,
        images_dir=images_dir,
        stylesheet_file=stylesheet_file,
        output_dir=output_dir,
        docker_image_decktape=args.docker_image_decktape,
        docker_image_asciidoctor=args.docker_image_asciidoctor,
        viewport_size=args.size,
        decktape_pause=args.pause,
        timeout=args.timeout,
        ignore_missing_images=args.ignore_missing_images,
        include_empty_notes=args.include_empty_notes,
        verbose=args.verbose
    )

    # Run the pipeline
    result = run_pipeline(config)

    # Generate machine-readable JSON report
    report_json_path = output_dir / "export-report.json"
    result.outputs["export_report"] = str(report_json_path.resolve())
    result.outputs["export_log"] = str((output_dir / "export.log").resolve())
    write_export_report(result, report_json_path)

    if result.status == "success":
        logger.info("Export completed successfully.")
        return 0
    else:
        logger.error("Export pipeline failed: %s", result.error_message)
        return 1

if __name__ == "__main__":
    sys.exit(main())
