#!/usr/bin/env python3
"""
Create non-English CK3 localization folders/files from the English source.

- Duplicates every .yml under localization/english into each target language folder.
- Renames filenames suffix (_english.yml -> _<lang>.yml).
- Rewrites the header key on the first non-empty line (e.g., l_english: -> l_spanish:).
- Writes files with UTF-8 BOM and Windows line endings (CRLF) which CK3 expects.
- Skips copying if destination file already exists unless --overwrite is provided.

Usage:
  py create_localizations.py
  py create_localizations.py --src localization/english --langs spanish german french --overwrite
"""

from __future__ import annotations
from pathlib import Path
import argparse

DEFAULT_SRC = Path("localization/english")
DEFAULT_LANGS = ["spanish","french","german","korean","polish","russian","simp_chinese"]

HEADER_MAP = {
    "english": "l_english",
    "spanish": "l_spanish",
    "french": "l_french",
    "german": "l_german",
    "korean": "l_korean",
    "polish": "l_polish",
    "russian": "l_russian",
    "simp_chinese": "l_simp_chinese",
}

def find_yml_files(src_dir: Path):
    return [p for p in src_dir.rglob("*.yml") if p.is_file()]

def target_from_source(src_file: Path, src_dir: Path, lang: str) -> Path:
    rel = src_file.relative_to(src_dir)  # e.g., events/abc_english.yml
    name = rel.name
    if name.lower().endswith("_english.yml"):
        new_name = name[:-len("_english.yml")] + f"_{lang}.yml"
    else:
        new_name = f"{rel.stem}_{lang}.yml"
    return Path("localization") / lang / rel.parent / new_name

def rewrite_header_to_lang(text: str, lang: str) -> str:
    lines = text.splitlines()
    target_header = HEADER_MAP[lang] + ":"
    for i, line in enumerate(lines):
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        if raw.startswith("l_") and raw.endswith(":"):
            lines[i] = line.replace(raw, target_header, 1)
            break
        else:
            lines.insert(i, target_header)
            break
    else:
        lines.append(target_header)
    # Return with CRLF endings; file open uses newline='\r\n' to preserve
    return "\r\n".join(lines) + "\r\n"

def process_file(src_file: Path, dst_file: Path, lang: str, overwrite: bool = False) -> bool:
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    if dst_file.exists() and not overwrite:
        return False
    text = src_file.read_text(encoding="utf-8-sig")
    out = rewrite_header_to_lang(text, lang)
    with dst_file.open("w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write(out)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--langs", nargs="*", default=DEFAULT_LANGS)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    src_dir = args.src
    if not src_dir.exists():
        raise SystemExit(f"Source folder not found: {src_dir}")
    files = find_yml_files(src_dir)
    if not files:
        raise SystemExit(f"No .yml files found under {src_dir}")

    made = 0
    for src in files:
        for lang in args.langs:
            if lang not in HEADER_MAP:
                print(f"Skipping unknown language key: {lang}")
                continue
            dst = target_from_source(src, src_dir, lang)
            if process_file(src, dst, lang, overwrite=args.overwrite):
                made += 1
                print(f"Wrote {dst}")
    print(f"Done. Created/updated {made} files.")

if __name__ == "__main__":
    main()
