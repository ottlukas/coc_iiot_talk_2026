"""
PDF post-processing utilities for interleaving speaker notes.
"""

import io
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
from exporter.config import ExporterConfig
from exporter.docker_utils import format_docker_volume_path, run_docker_command

logger = logging.getLogger("exporter")

# Self-contained python script template for notes generation & merging.
# This script is executed either on the host (if packages are available) or inside a python container.
NOTES_GENERATOR_SCRIPT = """
import io
import json
import sys
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    import pypdf
except ImportError as e:
    print(f"ERROR: Missing dependency: {str(e)}", file=sys.stderr)
    print("Please install reportlab and pypdf", file=sys.stderr)
    sys.exit(1)

def generate_single_notes_page(slide_num, title, notes, style_sheet) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    title_style = ParagraphStyle(
        'NotesTitle',
        parent=style_sheet['Heading2'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#7f1dba'),
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'NotesBody',
        parent=style_sheet['Normal'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'NotesBullet',
        parent=style_sheet['Normal'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=6
    )

    story = []
    header_text = f"Slide {slide_num}: {title or 'Untitled Slide'}"
    story.append(Paragraph(header_text, title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=15))
    
    if not notes.strip():
        story.append(Paragraph("<i>No speaker notes for this slide.</i>", body_style))
    else:
        paragraphs = notes.strip().split("\\n\\n")
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            lines = para.split("\\n")
            for line in lines:
                line_str = line.strip()
                if line_str.startswith("* ") or line_str.startswith("- "):
                    content = line_str[2:].strip()
                    story.append(Paragraph(f"&bull; {content}", bullet_style))
                else:
                    story.append(Paragraph(line_str, body_style))
            story.append(Spacer(1, 8))

    doc.build(story)
    return buf.getvalue()

def merge_slides_and_notes(
    slides_pdf_path: Path,
    notes_json_path: Path,
    output_pdf_path: Path,
    include_empty_notes: bool = False
):
    with open(notes_json_path, 'r', encoding='utf-8') as f:
        notes_data = json.load(f)

    reader = pypdf.PdfReader(slides_pdf_path)
    writer = pypdf.PdfWriter()
    style_sheet = getSampleStyleSheet()

    for idx, page in enumerate(reader.pages):
        slide_num = idx + 1
        writer.add_page(page)

        has_notes = False
        slide_title = ""
        slide_notes = ""
        
        if idx < len(notes_data):
            slide_title = notes_data[idx].get("title", "")
            slide_notes = notes_data[idx].get("notes", "")
            if slide_notes.strip():
                has_notes = True

        if has_notes or include_empty_notes:
            notes_bytes = generate_single_notes_page(slide_num, slide_title, slide_notes, style_sheet)
            notes_reader = pypdf.PdfReader(io.BytesIO(notes_bytes))
            for notes_page in notes_reader.pages:
                writer.add_page(notes_page)

    with open(output_pdf_path, 'wb') as f:
        writer.write(f)
    print(f"Interleaved PDF successfully written to {output_pdf_path}")

if __name__ == '__main__':
    merge_slides_and_notes(
        slides_pdf_path=Path("presentation.pdf"),
        notes_json_path=Path("notes.json"),
        output_pdf_path=Path("presentation-with-notes.pdf"),
        include_empty_notes=sys.argv[1].lower() == 'true' if len(sys.argv) > 1 else False
    )
"""

def generate_notes_pdf_handout(
    config: ExporterConfig,
    build_dir: Path,
    slides_pdf_path: Path,
    notes_data: List[Dict[str, Any]],
    output_filename: str = "presentation-with-notes.pdf"
) -> bool:
    """
    Orchestrates the creation of the speaker notes PDF by checking local availability
    and falling back to a Docker-based execution of the ReportLab/PyPDF compiler.
    """
    logger.info("Generating speaker notes handout PDF...")
    
    # 1. Write the notes data to JSON in the build directory
    notes_json = build_dir / "notes.json"
    with open(notes_json, "w", encoding="utf-8") as f:
        json.dump(notes_data, f, indent=2, ensure_ascii=False)
        
    # 2. Write the self-contained generator script in the build directory
    gen_script_path = build_dir / "generate_notes_handout.py"
    gen_script_path.write_text(NOTES_GENERATOR_SCRIPT, encoding="utf-8")

    # 3. Copy the slide-only PDF to the build directory as a local source
    shutil.copy2(slides_pdf_path, build_dir / "presentation.pdf")

    # 4. Check if reportlab and pypdf are available on the host
    has_host_deps = False
    try:
        import reportlab
        import pypdf
        has_host_deps = True
    except ImportError:
        pass

    if has_host_deps:
        logger.info("ReportLab and PyPDF are available on the host. Executing notes generation locally.")
        # Run using host Python
        cmd = [sys.executable, "generate_notes_handout.py", str(config.include_empty_notes)]
        try:
            res = subprocess.run(
                cmd,
                cwd=str(build_dir),
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug("Local notes generator stdout: %s", res.stdout)
        except subprocess.CalledProcessError as e:
            logger.error("Local speaker notes generation failed: %s", e.stderr)
            return False
    else:
        logger.info("ReportLab or PyPDF missing on the host. Running notes generation in python:3.10-slim container...")
        vol_mount = f"{format_docker_volume_path(build_dir)}:/app"
        
        # Install packages and run script inside Python container
        cmd = [
            "docker", "run", "--rm",
            "-v", vol_mount,
            "-w", "/app",
            "python:3.10-slim",
            "sh", "-c",
            f"pip install --quiet reportlab pypdf && python generate_notes_handout.py {str(config.include_empty_notes)}"
        ]
        
        exec_result = run_docker_command(cmd, timeout=config.timeout)
        if exec_result.exit_code != 0:
            logger.error("Container-based notes generation failed: %s", exec_result.stderr)
            return False
        logger.debug("Container notes generator stdout: %s", exec_result.stdout)

    # 5. Copy the generated PDF to the output directory
    built_pdf = build_dir / "presentation-with-notes.pdf"
    if built_pdf.is_file():
        config.output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built_pdf, config.output_dir / output_filename)
        logger.info("Speaker notes handout PDF generated successfully at %s", config.output_dir / output_filename)
        return True
    else:
        logger.error("Interleaved PDF was not found in the build directory after compilation.")
        return False
