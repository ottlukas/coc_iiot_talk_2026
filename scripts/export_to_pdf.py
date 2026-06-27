#!/usr/bin/env python3
"""
DEPRECATED: Old Reveal.js PDF exporter.
Delegates to the new, stabilized export_presentation.py exporter.
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=======================================================================", file=sys.stderr)
    print("DEPRECATION WARNING: scripts/export_to_pdf.py is deprecated and will be removed.", file=sys.stderr)
    print("Please use the new and stable export_presentation.py script instead.", file=sys.stderr)
    print("Example: python export_presentation.py --source docs/presentation.adoc", file=sys.stderr)
    print("=======================================================================\n", file=sys.stderr)

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    new_exporter = root_dir / "export_presentation.py"

    # Translate arguments to the new script
    # Basic translation: if we have arguments, pass them or forward to new script.
    new_args = [sys.executable, str(new_exporter)]
    
    # Simple forward mapping:
    # If the user passed docs/presentation.adoc, we map to --source docs/presentation.adoc
    # If they passed --output docs/exports/presentation.pdf, we map to --output-dir docs/exports
    i = 1
    forward_args = []
    while i < len(sys.argv):
        arg = sys.argv[i]
        if not arg.startswith("-"):
            forward_args.extend(["--source", arg])
        elif arg in ("--output", "--slides-output"):
            if i + 1 < len(sys.argv):
                output_file = Path(sys.argv[i + 1])
                forward_args.extend(["--output-dir", str(output_file.parent)])
                i += 1
        elif arg == "--notes-output":
            if i + 1 < len(sys.argv):
                output_file = Path(sys.argv[i + 1])
                forward_args.extend(["--output-dir", str(output_file.parent)])
                i += 1
        elif arg == "--slides-only":
            # Running new pipeline will build both, but we can accept and warn or ignore
            pass
        elif arg == "--notes-only":
            pass
        else:
            # Pass along any unknown arguments
            forward_args.append(arg)
        i += 1

    new_args.extend(forward_args)

    logger_cmd = " ".join(new_args)
    print(f"Delegating to: {logger_cmd}\n", file=sys.stderr)

    try:
        res = subprocess.run(new_args)
        sys.exit(res.returncode)
    except Exception as e:
        print(f"Error executing new exporter: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
