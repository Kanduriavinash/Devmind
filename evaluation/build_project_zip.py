"""Build a clean source-and-evidence distribution without local or academic artifacts."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist" / "devmind-project.zip"
INCLUDE_DIRS = (
    "src", "tests", "docs", "docker", "browser-extension", "datasets",
    "evaluation", "examples", "static", "audit", "research", "reports",
)
INCLUDE_FILES = (
    "README.md", "MANUAL.md", "ABOUT_PROJECT.md", "AGENTS.md", "pyproject.toml",
    "streamlit_app.py", ".env.example", ".gitignore",
)
EXCLUDED_PARTS = {
    ".venv", ".devmind", "__pycache__", ".pytest_cache", "node_modules",
    ".git", "devmind-report-draft", "superseded_provenance_checks",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_NAMES = {".env"}
EXCLUDED_REPORT_PREFIXES = ("devmind-report",)


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if path.name.startswith(EXCLUDED_REPORT_PREFIXES):
        return False
    # Academic papers, templates, and slide decks are prepared separately.
    if path.suffix.lower() in {".docx", ".pptx", ".pdf", ".tex", ".bib"}:
        return False
    return path.is_file()


def main() -> int:
    paths: set[Path] = {ROOT / item for item in INCLUDE_FILES if (ROOT / item).is_file()}
    for directory in INCLUDE_DIRS:
        base = ROOT / directory
        if base.exists():
            paths.update(path for path in base.rglob("*") if included(path))
    paths = {path for path in paths if included(path)}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(paths):
            archive.write(path, Path("DevMind") / path.relative_to(ROOT))
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    with zipfile.ZipFile(OUTPUT) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError(f"corrupt ZIP member: {bad_member}")
        members = archive.namelist()
    checksum = OUTPUT.with_suffix(OUTPUT.suffix + ".sha256")
    checksum.write_text(f"{digest}  {OUTPUT.name}\n", encoding="ascii")
    print(f"archive={OUTPUT}")
    print(f"files={len(members)} bytes={OUTPUT.stat().st_size} sha256={digest}")
    print(f"checksum={checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
