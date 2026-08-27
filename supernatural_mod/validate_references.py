#!/usr/bin/env python3
"""
validate_references.py -- find references to things that do not exist.

Written for Supernatural 2.32, after the portrait-animation finding: 31 `animation = X`
references in the mod named animations CK3 does not have. CK3 does not error on those -- it
silently falls back to `idle` -- so the best-written events in the mod had been rendering
every portrait as a neutral pose, and nothing in error.log ever said so.

That is a whole CLASS of defect: a name that looks right, resolves to nothing, and fails
quietly. This script checks that class across every reference type the mod uses.

WHAT IT CHECKS
  portrait animations      animation = X                (vs gfx/portraits/portrait_animations)
  scripted animations      scripted_animation = X       (vs common/scripted_animations)
  traits                   has_/add_/remove_trait = X   (trait GROUPS count as valid)
  event backgrounds        background = { reference = X }
  event themes             theme = X
  character + opinion mods  has_/add_character_modifier, add_opinion
  death reasons            death_reason = X
  perks / focuses / secrets / scripted relations
  trait icons              icon = X.dds                 (checks the file is on disk)
  scripted helpers         *_trigger / *_effect / *_value calls, brace-depth aware
  localization keys        desc / title / custom_tooltip / selection_tooltip

WHY IT IS BRACE-AWARE
  A naive regex cannot tell `foo = {` at the top of a file (a DEFINITION) from `foo = {`
  nested inside a block (a CALL). The helper check tracks real brace depth so it does not
  report every nested field name as an undefined effect.

KNOWN-GOOD EXCLUSIONS (learned the hard way, do not remove without checking)
  * `scripted_animation = X` is a DIFFERENT system from `animation = X`. Matching
    `animation\\s*=` also matches the tail of `scripted_animation =`; use the lookbehind.
  * Trait GROUPS (`wounded`, `kinslayer`, `education_martial`, `beauty_good` ...) are valid
    targets of `has_trait` even though they are not traits. 21 of them.
  * Inside `icon = { first_valid = { triggered_desc = { desc = X.dds } } }`, `desc` names a
    FILE, not a loc key.
  * A leading UTF-8 BOM hides the first definition in a file from `^name = {`. Always read
    with encoding="utf-8-sig". This bit four separate checks while writing this.

USAGE
  py validate_references.py                       # everything
  py validate_references.py --only animations traits
  py validate_references.py --game "D:/SteamLibrary/steamapps/common/Crusader Kings III/game"
  py validate_references.py --own                 # only files that are Thomas's, not upstream's
"""

from __future__ import annotations
import re, os, sys, argparse, collections, glob

DEF_TOP = re.compile(r"(?m)^([A-Za-z0-9_.\-]+)\s*=\s*\{")

DEF_DIRS = {
    "trait":            ["common/traits"],
    "char_modifier":    ["common/modifiers"],
    "opinion_modifier": ["common/opinion_modifiers"],
    "death_reason":     ["common/deathreasons"],
    "background":       ["common/event_backgrounds"],
    "theme":            ["common/event_themes"],
    "perk":             ["common/lifestyle_perks"],
    "focus":            ["common/focuses"],
    "secret":           ["common/secret_types"],
    "relation":         ["common/scripted_relations"],
    "effect":           ["common/scripted_effects"],
    "trigger":          ["common/scripted_triggers"],
    "value":            ["common/script_values"],
}

OWN_HINTS = ("spn_", "supernatural", "vampire_feeding")


# ------------------------------------------------------------------ harvesting

def harvest_dirs(root: str, dirs) -> set[str]:
    names = set()
    for d in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for r, _, fs in os.walk(base):
            for f in fs:
                if not f.endswith(".txt") or f.startswith("_"):
                    continue
                try:
                    t = open(os.path.join(r, f), encoding="utf-8-sig", errors="ignore").read()
                except OSError:
                    continue
                names |= set(DEF_TOP.findall(re.sub(r"#.*", "", t)))
    return names


def harvest_animations(game: str) -> tuple[set[str], set[str]]:
    a = os.path.join(game, "gfx/portraits/portrait_animations/animations.txt")
    s = os.path.join(game, "common/scripted_animations/00_scripted_animations.txt")
    anim = set(re.findall(r"(?m)^([a-z_0-9]+) = \{",
               open(a, encoding="utf-8-sig").read())) if os.path.exists(a) else set()
    scr = set(re.findall(r"(?m)^([a-z_0-9]+)\s*=\s*\{",
              open(s, encoding="utf-8-sig").read())) if os.path.exists(s) else set()
    return anim, scr


def harvest_trait_groups(*roots) -> set[str]:
    g = set()
    for base in roots:
        for f in glob.glob(os.path.join(base, "common/traits/*.txt")):
            g |= set(re.findall(r"(?m)^\s*group\s*=\s*([a-z_0-9]+)",
                     open(f, encoding="utf-8-sig", errors="ignore").read()))
    return g


def harvest_loc(base: str) -> set[str]:
    k = set()
    d = os.path.join(base, "localization", "english")
    for r, _, fs in os.walk(d):
        for f in fs:
            if f.endswith(".yml"):
                k |= set(re.findall(r"(?m)^\s*([A-Za-z0-9_.\-]+):\d*\s",
                         open(os.path.join(r, f), encoding="utf-8-sig", errors="ignore").read()))
    return k


def load_files(mod: str, own_only: bool):
    out = {}
    for r, _, fs in os.walk(mod):
        if os.sep + "." in r:
            continue
        for f in fs:
            if not f.endswith(".txt"):
                continue
            p = os.path.join(r, f)
            if own_only and not any(h in p for h in OWN_HINTS):
                continue
            try:
                raw = open(p, encoding="utf-8-sig", errors="ignore").read()
            except OSError:
                continue
            out[p] = "\n".join(l.split("#")[0] for l in raw.split("\n"))
    return out


# -------------------------------------------------------------------- checking

def collect(files, pattern, ok, flags=0):
    hits = collections.defaultdict(list)
    for p, t in files.items():
        for m in re.finditer(pattern, t, flags):
            n = m.group(1)
            if n in ok or n in ("yes", "no", "this", "root", "prev"):
                continue
            hits[n].append((os.path.basename(p), t[:m.start()].count("\n") + 1))
    return hits


def helper_calls(files, defined):
    """Brace-depth aware: depth 0 is a definition, deeper is a call."""
    HELPER = re.compile(r"^(?:spn_|vf_|st_|ww_)?[a-z0-9_]*(?:_trigger|_effect|_value)$")
    # Engine field names that happen to match the helper naming convention. Verified by hand
    # against the game files -- each is a built-in field, not a scripted symbol.
    SKIP = {"hidden_effect", "random_list", "ai_value", "siege_value", "play_sound_effect",
            "on_applied_effect", "ai_target_quick_trigger", "scripted_effect", "scripted_trigger",
            # gene keys inside a `dna = { }` block, not script value calls
            "gene_dragon_primary_color_value", "gene_dragon_secondary_value",
            "gene_dragon_tertiary_value", "gene_dragon_eye_color_value",
            "gene_dragon_horn_color_value"}
    local_defs, calls = set(), collections.defaultdict(list)
    for p, t in files.items():
        depth = 0
        for ln, line in enumerate(t.split("\n"), 1):
            m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_.\-]*)\s*=", line)
            if m:
                if depth == 0:
                    local_defs.add(m.group(1))
                elif HELPER.match(m.group(1)) and m.group(1) not in SKIP:
                    calls[m.group(1)].append((os.path.basename(p), ln))
            depth += line.count("{") - line.count("}")
    return {k: v for k, v in calls.items() if k not in defined and k not in local_defs}


def report(title, hits, limit=40) -> int:
    if not hits:
        print(f"  [ok]   {title}")
        return 0
    tot = sum(len(v) for v in hits.values())
    print(f"\n  [!!]   {title}: {tot} reference(s), {len(hits)} distinct")
    for n, l in sorted(hits.items(), key=lambda kv: -len(kv[1]))[:limit]:
        where = "; ".join(f"{f}:{ln}" for f, ln in l[:3])
        print(f"           {n:<44} x{len(l):<4} {where}")
    print()
    return tot


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", default=".")
    ap.add_argument("--game", default=os.path.expanduser(
        "~/mnt/game" if os.path.isdir(os.path.expanduser("~/mnt/game"))
        else "D:/SteamLibrary/steamapps/common/Crusader Kings III/game"))
    ap.add_argument("--own", action="store_true", help="only Thomas's files, not vendored upstream")
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()

    if not os.path.isdir(os.path.join(a.game, "common")):
        print(f"  !! game folder not found at {a.game} -- pass --game", file=sys.stderr)
        return 2

    K = {c: harvest_dirs(a.game, d) | harvest_dirs(a.mod, d) for c, d in DEF_DIRS.items()}
    anim, scr = harvest_animations(a.game)
    K["trait"] |= harvest_trait_groups(a.game, a.mod)
    mods = K["char_modifier"] | K["opinion_modifier"]
    loc = harvest_loc(a.mod) | harvest_loc(a.game)
    files = load_files(a.mod, a.own)

    print(f"\n  scanning {len(files)} .txt files against {a.game}\n")
    want = lambda n: a.only is None or n in a.only
    bad = 0

    if want("animations"):
        # the lookbehind is load-bearing: scripted_animation is a different system
        bad += report("portrait animations",
                      collect(files, r"(?<!scripted_)\banimation\s*=\s*([a-z][a-z0-9_]+)", anim))
        bad += report("scripted animations",
                      collect(files, r"\bscripted_animation\s*=\s*([a-z][a-z0-9_]+)", scr))
    if want("traits"):
        bad += report("traits", collect(
            files, r"\b(?:has_trait|add_trait|remove_trait|add_trait_force_tooltip)\s*=\s*([a-z][a-z0-9_]+)",
            K["trait"]))
    if want("backgrounds"):
        bad += report("event backgrounds", collect(
            files, r"(?:override_)?background\s*=\s*\{[^{}]*?reference\s*=\s*([a-z][a-z0-9_]+)",
            K["background"], re.S))
    if want("themes"):
        bad += report("event themes",
                      collect(files, r"(?m)^\s*theme\s*=\s*([a-z][a-z0-9_]+)", K["theme"]))
    if want("modifiers"):
        bad += report("modifiers (has_/remove_)", collect(
            files, r"\b(?:has_character_modifier|remove_character_modifier)\s*=\s*([a-z][a-z0-9_]+)", mods))
        bad += report("modifiers (inside add_* blocks)", collect(
            files, r"(?:add_character_modifier|add_opinion|add_house_modifier|add_county_modifier)"
                   r"\s*=\s*\{[^{}]*?modifier\s*=\s*([a-z][a-z0-9_]+)", mods, re.S))
    if want("deaths"):
        bad += report("death reasons",
                      collect(files, r"\bdeath_reason\s*=\s*([a-z][a-z0-9_]+)", K["death_reason"]))
    if want("perks"):
        bad += report("perks", collect(
            files, r"\b(?:has_perk|add_perk|remove_perk)\s*=\s*([a-z][a-z0-9_]+)", K["perk"]))
        bad += report("focuses", collect(files, r"\bhas_focus\s*=\s*([a-z][a-z0-9_]+)", K["focus"]))
    if want("secrets"):
        bad += report("secret types",
                      collect(files, r"\bsecret_type\s*=\s*([a-z][a-z0-9_]+)", K["secret"]))
    if want("relations"):
        bad += report("scripted relations", collect(
            files, r"\b(?:has_relation|set_relation|remove_relation)_([a-z][a-z0-9_]+)\s*=", K["relation"]))
    if want("helpers"):
        bad += report("scripted effect/trigger/value calls",
                      helper_calls(files, K["effect"] | K["trigger"] | K["value"]))
    if want("icons"):
        # note the folder is `death_reason`, singular -- guessing the plural reports a false
        # positive on every death reason icon in the mod.
        avail = set()
        for base in (a.mod, a.game):
            for sub in ("gfx/interface/icons/traits", "gfx/interface/icons/traits_small",
                        "gfx/interface/icons/death_reason", "gfx/interface/icons/activities",
                        "gfx/interface/icons/faith_doctrines", "gfx/interface/icons/decisions"):
                d = os.path.join(base, sub)
                if os.path.isdir(d):
                    for r, _, fs in os.walk(d):
                        avail |= set(fs)
        bad += report("icon files (trait / death reason / activity)", collect(
            files, r"(?:icon|desc)\s*=\s*([A-Za-z0-9_.\-]+\.dds)", avail))
    if want("loc"):
        # inside an icon block, `desc` names a FILE -- exclude .dds before comparing
        hits = collect(files,
                       r"(?:desc|title|custom_tooltip|selection_tooltip)\s*=\s*([a-z][A-Za-z0-9_.]{4,})\s*(?:\n|$)",
                       loc)
        hits = {k: v for k, v in hits.items()
                if not k.endswith((".dds", "_trigger", "_effect", "_value"))}
        # vanilla's own key, used by the faithful shadow of 00_marriage_scripted_modifiers.txt.
        # Missing from vanilla's english loc too -- Paradox's, not ours.
        hits.pop("ceremony_house_power", None)
        bad += report("localization keys", hits)

    print(f"\n  {'CLEAN -- every reference resolves' if bad == 0 else f'{bad} unresolved reference(s)'}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
