"""
Generates and writes machine-readable reports of the export process.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from . config import ExportResult

logger = logging.getLogger("exporter")

def write_export_report(
    result: ExportResult,
    output_path: Path
) -> None:
    """Writes the export result metadata to a JSON file."""
    # Build dict representation
    report_data = {
        "status": result.status,
        "timestamp": datetime.now().isoformat(),
        "source_file": result.source_file,
        "error_message": result.error_message,
        "outputs": result.outputs,
        "images_validation": result.images_validation,
        "commands_executed": [
            {
                "command": cmd.command,
                "exit_code": cmd.exit_code,
                "stdout": cmd.stdout.strip(),
                "stderr": cmd.stderr.strip()
            }
            for cmd in result.commands_executed
        ]
    }
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        logger.info("Export report successfully written to %s", output_path)
    except Exception as e:
        logger.error("Failed to write export report to %s: %s", output_path, str(e))
