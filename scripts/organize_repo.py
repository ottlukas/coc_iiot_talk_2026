#!/usr/bin/env python3
"""Organize the coc_iiot_talk_2026 repository.
Moves Asciidoc files, RevealJS assets, and Docker Compose files into
structured directories while preserving Git history via `git mv`.
"""

import pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

def run(cmd):
    subprocess.run(cmd, cwd=ROOT, check=True)

def move(src: pathlib.Path, dst: pathlib.Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "mv", str(src), str(dst)])
    print(f"Moved {src} -> {dst}")

def main():
    # Asciidoc files
    for adoc in ROOT.rglob("*.adoc"):
        if "docs" not in adoc.parts:
            move(adoc, ROOT / "docs" / adoc.name)
    # RevealJS HTML output (common extensions)
    for html in ROOT.rglob("*.html"):
        if "presentations" not in html.parts:
            move(html, ROOT / "presentations" / html.name)
    # CSS/JS assets for presentations
    for asset in (ROOT / "open-source-manufacturing" / "assets").rglob("*.*"):
        rel = asset.relative_to(ROOT)
        if "presentations" not in rel.parts:
            move(asset, ROOT / "presentations" / "assets" / asset.name)
    # Images used in presentations
    for img in (ROOT / "open-source-manufacturing" / "images").rglob("*.*"):
        if "presentations" not in img.parts:
            move(img, ROOT / "presentations" / "assets" / img.name)
    # Docker compose files
    for compose in ROOT.glob("docker-compose*.yml"):
        name = compose.name.lower()
        if "dev" in name:
            target = ROOT / "docker" / "dev" / "docker-compose.yml"
        elif "staging" in name:
            target = ROOT / "docker" / "staging" / "docker-compose.yml"
        elif "prod" in name or "production" in name:
            target = ROOT / "docker" / "prod" / "docker-compose.yml"
        else:
            target = ROOT / "docker" / "dev" / "docker-compose.yml"
        move(compose, target)

if __name__ == "__main__":
    sys.exit(main())
