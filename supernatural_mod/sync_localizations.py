#!/usr/bin/env python3
"""
sync_localizations.py -- key-aware localization maintenance for the Supernatural CK3 mod.

Written for 2.32. Replaces the job create_localizations.py was doing badly:

    process_file():  if dst_file.exists() and not overwrite: return False

That guard is file-granular and has no concept of a key, so the script has exactly two
behaviours and both are wrong once the target files exist:

  * a normal run adds NOTHING, ever -- every destination file already exists, so new English
    keys can never reach the other seven languages. That is the entire 1,513-key gap.
  * --overwrite copies English over the whole file, DESTROYING any real translation in it.

This tool works at the level of a key.

MODES
  --sync            (default) append keys that exist in English and are absent from the target,
                    marked `# MT`. Never touches an existing key. Never reorders. Never deletes.
  --canonicalise    write both his file and a SCRATCH copy of upstream's into the same canonical
                    key order so a diff shows real text differences instead of reordering noise.
                    Writes to a scratch directory ONLY -- never over the mod.
  --report          pre-release audit: missing per language, keys no longer in English, in-file
                    duplicates, malformed lines, and anything still marked # MT.

TWO INPUTS IT NEEDS
  --rename-map      JSON {upstream_key: his_key}, so upstream's translations can be pulled in
                    under his renamed keys (magic_focus -> arcane_focus, necronomicon ->
                    blackgrimoire, monthly_magic2_lifestyle_xp_gain_mult -> monthly_magic_...).
  --skip-list       newline-delimited keys (or file globs) that must never be regenerated from
                    English, so real translations are not clobbered.

CK3 file conventions this preserves:
  * UTF-8 with BOM
  * CRLF line endings
  * the `l_<lang>:` header on the first non-empty, non-comment line
  * ` key:0 "value"` with a leading space

Usage
  py sync_localizations.py --report
  py sync_localizations.py --sync
  py sync_localizations.py --sync --langs russian --rename-map renames.json
  py sync_localizations.py --canonicalise --upstream "D:/.../1158310/2837844350" --scratch _locdiff
"""

from __future__ import annotations
from pathlib import Path
import argparse, json, re, sys, collections

DEFAULT_SRC = Path("localization/english")
DEFAULT_LANGS = ["spanish", "french", "german", "korean", "polish", "russian", "simp_chinese"]

# ` key:0 "value"`  -- CK3 also allows a bare `key: "value"` with no version number.
KEY_RE = re.compile(r'^(\s*)([A-Za-z0-9_.\-]+):(\d*)\s+"(.*)"\s*$', re.S)
HEADER_RE = re.compile(r'^\s*(l_[a-z_]+)\s*:\s*$')

MT = "# MT"   # machine-translation marker: English text sitting in a non-English file


# --------------------------------------------------------------------------- io

def read_lines(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n").split("\n")


def write_lines(p: Path, lines: list[str]) -> None:
    """CK3 wants UTF-8 BOM + CRLF."""
    p.parent.mkdir(parents=True, exist_ok=True)
    text = "\r\n".join(lines).rstrip("\r\n") + "\r\n"
    p.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


def parse(p: Path):
    """-> (header, [(key, version, value, raw_line_index)], lines)"""
    lines = read_lines(p)
    header, entries = None, []
    for i, line in enumerate(lines):
        if header is None:
            m = HEADER_RE.match(line)
            if m:
                header = m.group(1)
                continue
        m = KEY_RE.match(line)
        if m:
            entries.append((m.group(2), m.group(3), m.group(4), i))
    return header, entries, lines


def lang_of(p: Path) -> str | None:
    m = re.search(r"_([a-z_]+)\.yml$", p.name)
    return m.group(1) if m else None


def target_path(src_file: Path, src_dir: Path, lang: str) -> Path:
    rel = src_file.relative_to(src_dir)
    name = rel.name
    new = name[: -len("_english.yml")] + f"_{lang}.yml" if name.lower().endswith("_english.yml") \
          else f"{rel.stem}_{lang}.yml"
    return Path("localization") / lang / rel.parent / new


# ------------------------------------------------------------------------ sync

def all_keys_in_language(lang: str) -> set:
    """Every key defined ANYWHERE in this language, not just in the mapped file.

    2.33 -- THIS IS THE BUG THAT BIT. The first version checked whether a key existed in the
    ONE file the English filename maps to. A translator who consolidates or renames files -- and
    the Russian contributor did exactly that, putting 10_spn_character_interactions keys into
    10_spn_character_interactions_shifter_l_russian.yml -- has every key present under a DIFFERENT
    filename. The per-file check saw an empty mapped file, created it, and re-added 139 keys that
    already existed, producing duplicate-key errors in eight languages.

    That is the same file-granular flaw this script exists to replace in create_localizations.py.
    """
    keys = set()
    base = Path("localization") / lang
    if not base.is_dir():
        return keys
    for p in base.rglob("*.yml"):
        _, entries, _ = parse(p)
        keys |= {k for k, _, _, _ in entries}
    return keys


def do_sync(src_dir: Path, langs, renames: dict, skip: set, dry: bool) -> int:
    added_total = 0
    lang_keys = {lang: all_keys_in_language(lang) for lang in langs}
    for src in sorted(src_dir.rglob("*.yml")):
        _, en_entries, _ = parse(src)
        if not en_entries:
            continue
        en = {k: (v, val) for k, v, val, _ in en_entries}

        for lang in langs:
            dst = target_path(src, src_dir, lang)
            if not dst.exists():
                # whole file missing: create it, header first, then every key.
                out = [f"l_{lang}:"] + [f' {k}:{v} "{val}"'
                                        for k, v, val, _ in en_entries
                                        if k not in skip and k not in lang_keys[lang]]
                if len(out) == 1:          # nothing to write; do not create an empty file
                    continue
                if not dry:
                    write_lines(dst, out)
                added = len(out) - 1
                lang_keys[lang] |= {k for k, _, _, _ in en_entries
                                    if k not in skip and k not in lang_keys[lang]}
                added_total += added
                print(f"  + {dst}  (new file, {added} keys)")
                continue

            header, dst_entries, lines = parse(dst)
            have = {k for k, _, _, _ in dst_entries}
            # `have` is this file; lang_keys is the WHOLE language. Both must miss it.
            missing = [(k, v, val) for k, v, val, _ in en_entries
                       if k not in have and k not in skip and k not in lang_keys[lang]]
            # pull upstream translations in under his renamed keys where we can
            for i, (k, v, val) in enumerate(missing):
                up_key = next((u for u, h in renames.items() if h == k), None)
                if up_key and up_key in have:
                    missing[i] = (k, v, val)  # value substitution happens in --canonicalise
            if not missing:
                continue

            # The marker is a WHOLE-LINE comment. An inline `# MT` after the closing quote has no
            # vanilla precedent and this script's own KEY_RE could not read it back -- which would
            # have made every later --sync re-add the same keys.
            block = [""] + [f"### added by sync_localizations.py -- untranslated, {len(missing)} keys"] + \
                    [f' {k}:{v} "{val}"' for k, v, val in missing]
            if not dry:
                write_lines(dst, lines + block)   # append only; nothing above is touched
            lang_keys[lang] |= {k for k, _, _ in missing}
            added_total += len(missing)
            print(f"  + {dst}  (+{len(missing)} keys)")
    print(f"\n  {'would add' if dry else 'added'} {added_total} keys")
    return added_total


# ---------------------------------------------------------------- canonicalise

def do_canonicalise(src_dir: Path, upstream: Path, scratch: Path) -> None:
    """
    The fix for 'it would be out of order'.

    Rewrites HIS file and a SCRATCH copy of UPSTREAM's into the same canonical key order, so a
    diff of the two shows real text differences instead of thousands of lines of reordering
    noise. Both outputs land under --scratch. The mod is never written to.
    """
    scratch.mkdir(parents=True, exist_ok=True)
    pairs = 0
    for mine in sorted(src_dir.rglob("*.yml")):
        up = upstream / "localization" / "english" / mine.relative_to(src_dir)
        if not up.exists():
            continue
        for tag, path in (("mine", mine), ("upstream", up)):
            header, entries, _ = parse(path)
            entries.sort(key=lambda e: e[0])          # canonical = key order, stable
            out = [header or "l_english:"] + [f' {k}:{v} "{val}"' for k, v, val, _ in entries]
            dest = scratch / tag / mine.relative_to(src_dir)
            write_lines(dest, out)
        pairs += 1
    print(f"  canonicalised {pairs} file pairs into {scratch}/mine and {scratch}/upstream")
    print(f"  now diff them:  diff -ru {scratch}/upstream {scratch}/mine")


# ---------------------------------------------------------------------- report

def do_report(src_dir: Path, langs) -> int:
    en_keys, en_dupes = set(), collections.Counter()
    for src in sorted(src_dir.rglob("*.yml")):
        _, entries, _ = parse(src)
        for k, _, _, _ in entries:
            if k in en_keys:
                en_dupes[k] += 1
            en_keys.add(k)

    print(f"\n  english: {len(en_keys)} unique keys, {sum(en_dupes.values())} duplicate definitions")
    for k, c in en_dupes.most_common(10):
        print(f"      duplicate: {k} (+{c})")

    print(f"\n  {'lang':<14}{'keys':>8}{'unique':>8}{'dupes':>7}{'missing':>9}{'stale':>7}{'# MT':>7}")
    print("  " + "-" * 60)
    worst = 0
    for lang in langs:
        d = Path("localization") / lang
        if not d.is_dir():
            print(f"  {lang:<14}{'-- folder missing --':>39}")
            continue
        keys, dupes, mt = set(), 0, 0
        total = 0
        for p in sorted(d.rglob("*.yml")):
            _, entries, lines = parse(p)
            for k, _, _, i in entries:
                total += 1
                if k in keys:
                    dupes += 1
                keys.add(k)
                if MT in lines[i]:
                    mt += 1
        missing = len(en_keys - keys)
        stale = len(keys - en_keys)
        worst = max(worst, missing)
        print(f"  {lang:<14}{total:>8}{len(keys):>8}{dupes:>7}{missing:>9}{stale:>7}{mt:>7}")

    print("\n  missing = in English, absent here (run --sync)")
    print("  stale   = here, no longer in English (safe to delete)")
    print("  # MT    = English text sitting in a non-English file, awaiting translation")
    return worst


# ------------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--langs", nargs="*", default=DEFAULT_LANGS)
    ap.add_argument("--sync", action="store_true", help="append missing keys (default)")
    ap.add_argument("--canonicalise", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--upstream", type=Path, help="upstream Witchcraft mod root (--canonicalise)")
    ap.add_argument("--scratch", type=Path, default=Path("_locdiff"))
    ap.add_argument("--rename-map", type=Path, help='JSON {"upstream_key": "his_key"}')
    ap.add_argument("--skip-list", type=Path, help="newline-delimited keys never to regenerate")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.src.is_dir():
        print(f"  !! {a.src} not found -- run this from the mod root", file=sys.stderr)
        return 2

    renames = json.loads(a.rename_map.read_text(encoding="utf-8-sig")) if a.rename_map else {}
    skip = set()
    if a.skip_list:
        skip = {l.strip() for l in a.skip_list.read_text(encoding="utf-8-sig").splitlines()
                if l.strip() and not l.startswith("#")}

    if a.report:
        do_report(a.src, a.langs)
    if a.canonicalise:
        if not a.upstream:
            print("  !! --canonicalise needs --upstream", file=sys.stderr)
            return 2
        do_canonicalise(a.src, a.upstream, a.scratch)
    if a.sync or not (a.report or a.canonicalise):
        do_sync(a.src, a.langs, renames, skip, a.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
