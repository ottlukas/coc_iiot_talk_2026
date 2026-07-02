"""
Parser for AsciiDoc files to extract slide notes, headings, and image references.
"""

import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Tuple, Any
from . config import ImageReference

# Regex patterns for image references
PATTERNS = {
    "macro_double": re.compile(r"image::([^\[]+)\["),
    "macro_single": re.compile(r"(?<!:)image:(?!:)([^\[]+)\["),
    "img_src": re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE),
    "data_src": re.compile(r"data-src=[\"']([^\"']+)[\"']", re.IGNORECASE),
    "bg_image_attr": re.compile(r"background-image=[\"']([^\"']+)[\"']", re.IGNORECASE),
    "doc_attr_bg": re.compile(r"^\s*:\S*background-image\S*:\s*(.+)$", re.MULTILINE),
}

def parse_images_from_adoc(adoc_content: str) -> List[ImageReference]:
    """
    Parse AsciiDoc content for all image references.
    Returns a list of ImageReference objects.
    """
    img_refs = []
    lines = adoc_content.splitlines()

    for idx, line in enumerate(lines, start=1):
        # Check standard macros and tags line by line
        for key in ["macro_double", "macro_single", "img_src", "data_src", "bg_image_attr"]:
            for match in PATTERNS[key].finditer(line):
                ref_path = match.group(1).strip().lstrip(":")
                img_refs.append(ImageReference(
                    ref_path=ref_path,
                    line_number=idx,
                    context_line=line.strip()
                ))

    # Check document-level attributes (can span lines, but we search globally)
    for match in PATTERNS["doc_attr_bg"].finditer(adoc_content):
        ref_path = match.group(1).strip()
        # Find line number roughly
        pos = match.start()
        line_num = adoc_content[:pos].count("\n") + 1
        img_refs.append(ImageReference(
            ref_path=ref_path,
            line_number=line_num,
            context_line=match.group(0).strip()
        ))

    return img_refs

def extract_images_dir(adoc_content: str) -> str:
    """Extract the value of the :imagesdir: attribute, defaulting to '.' if not set."""
    match = re.search(r"^:imagesdir:\s*(.+)$", adoc_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "."

def validate_and_resolve_images(
    image_refs: List[ImageReference],
    source_file: Path,
    images_dir: Path
) -> Tuple[List[ImageReference], List[ImageReference]]:
    """
    Validate images, checking if they exist locally or remotely.
    Returns (valid_refs, missing_refs).
    """
    valid = []
    missing = []
    adoc_dir = source_file.parent.resolve()
    images_dir_resolved = images_dir.resolve()

    for ref in image_refs:
        path_str = ref.ref_path
        if path_str.startswith("http://") or path_str.startswith("https://"):
            # Remote URL validation
            try:
                req = urllib.request.Request(path_str, method="HEAD")
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status < 400:
                        ref.is_valid = True
                        valid.append(ref)
                    else:
                        ref.is_valid = False
                        ref.error_message = f"HTTP status {response.status}"
                        missing.append(ref)
            except Exception as e:
                # Retry with GET just in case HEAD is not allowed
                try:
                    with urllib.request.urlopen(path_str, timeout=5) as response:
                        if response.status < 400:
                            ref.is_valid = True
                            valid.append(ref)
                        else:
                            ref.is_valid = False
                            ref.error_message = f"HTTP status {response.status}"
                            missing.append(ref)
                except Exception as ex:
                    ref.is_valid = False
                    ref.error_message = str(ex)
                    missing.append(ref)
        else:
            # Local file validation
            # Try candidates:
            # 1. Direct path relative to adoc file parent
            # 2. Relative to the images directory
            # 3. Strip any leading '/' and search relative to project root
            clean_path = path_str.lstrip("/")
            candidates = [
                adoc_dir / path_str,
                images_dir_resolved / path_str,
                adoc_dir / clean_path,
                images_dir_resolved / clean_path,
                # also check if the path is relative but images dir prefix is already in it
                Path(clean_path)
            ]
            
            # If the user specified a path like "images/pic.png" and images_dir has name "images"
            if clean_path.startswith("images/") or clean_path.startswith("images\\"):
                sub_path = clean_path[len("images/"):].lstrip("\\/")
                candidates.append(images_dir_resolved / sub_path)
                candidates.append(adoc_dir / sub_path)

            found = False
            resolved_file_path = None
            for c in candidates:
                try:
                    if c.is_file():
                        found = True
                        resolved_file_path = c.resolve()
                        break
                except Exception:
                    continue

            if found:
                ref.is_valid = True
                # Store the resolved path inside the reference for ease of copy/use later
                ref.resolved_path = resolved_file_path  # type: ignore
                valid.append(ref)
            else:
                ref.is_valid = False
                ref.error_message = "File not found locally"
                missing.append(ref)

    return valid, missing

def normalize_adoc_content(adoc_content: str, imagesdir: str) -> str:
    """
    Normalize image references in AsciiDoc to strip redundant imagesdir prefixes.
    E.g. if imagesdir is "images", replaces "image::images/pic.png[]" with "image::pic.png[]".
    """
    if not imagesdir or imagesdir == ".":
        return adoc_content

    # Escape imagesdir for regex
    esc_dir = re.escape(imagesdir)
    prefix_pattern = rf"({esc_dir}[/\\])"

    # We replace references of the form:
    # - image::images/pic.png[] -> image::pic.png[]
    # - image:images/pic.png[] -> image:pic.png[]
    # - src="images/pic.png" -> src="pic.png"
    # - data-src="images/pic.png" -> data-src="pic.png"
    # - background-image="images/pic.png" -> background-image="pic.png"
    # - :title-slide-background-image: images/pic.png -> :title-slide-background-image: pic.png
    
    content = adoc_content
    # Macro double
    content = re.sub(rf"image::{prefix_pattern}", r"image::", content)
    # Macro single
    content = re.sub(rf"image:{prefix_pattern}", r"image:", content)
    # img src
    content = re.sub(rf"src=([\"']){prefix_pattern}", r"src=\1", content, flags=re.IGNORECASE)
    # data-src
    content = re.sub(rf"data-src=([\"']){prefix_pattern}", r"data-src=\1", content, flags=re.IGNORECASE)
    # background-image
    content = re.sub(rf"background-image=([\"']){prefix_pattern}", r"background-image=\1", content, flags=re.IGNORECASE)
    # doc-level attributes
    content = re.sub(rf"^(\s*):(title-slide-background-image|.*background-image.*):\s*{prefix_pattern}", r"\1:\2: ", content, flags=re.MULTILINE | re.IGNORECASE)

    return content

def parse_slides_and_notes(adoc_content: str) -> List[Dict[str, Any]]:
    """
    Extract slide titles and speaker notes.
    Returns a list of dicts: [{"title": "Slide Title", "notes": "notes content", "level": 2}]
    """
    slides = []
    lines = adoc_content.splitlines()

    current_slide = None
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()

        # Check for slide headings (level 1 to 4)
        match_heading = re.match(r"^(=+)\s+(.+)$", line)
        if match_heading:
            level = len(match_heading.group(1))
            title = match_heading.group(2).strip()
            
            # Clean up title formatting if it has attributes like [%notitle]
            # but usually they are just text.
            current_slide = {"title": title, "notes": "", "level": level}
            slides.append(current_slide)
            idx += 1
            continue

        # Check for [.notes] block
        if line == "[.notes]":
            notes_lines = []
            idx += 1
            if idx < len(lines) and lines[idx].strip() == "--":
                # Open block notes
                idx += 1  # consume "--"
                while idx < len(lines) and lines[idx].strip() != "--":
                    notes_lines.append(lines[idx])
                    idx += 1
                if idx < len(lines):
                    idx += 1  # consume closing "--"
            else:
                # Paragraph notes
                while idx < len(lines) and lines[idx].strip() != "":
                    notes_lines.append(lines[idx])
                    idx += 1
            
            # Associate these notes with the current slide if one has been defined
            if current_slide is not None:
                new_notes = "\n".join(notes_lines).strip()
                existing = current_slide["notes"]
                if existing:
                    current_slide["notes"] = existing + "\n\n" + new_notes
                else:
                    current_slide["notes"] = new_notes
            continue

        idx += 1

    return slides
