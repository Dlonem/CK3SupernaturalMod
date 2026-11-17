#!/usr/bin/env python3
"""
Supernatural -- the CK3 1.21 ("Florin") port: the renames.  Run from the mod root:   py apply_ck3_121_port.py

Idempotent: a second run finds nothing left to change. Code is rewritten only outside comments; localization is
touched only at KEYS and at key references ($key$, [concept|E]) -- the translated words themselves are never edited
(Adrian's Russian included). Every target name was confirmed in vanilla 1.21.0 script, and every old name has zero
uses left in vanilla 1.21.0 script (diff of 17 Nov 2026, _vanilla-snapshots\diff-1.20.1.2-to-1.21.0).

Paradox's table: "Silk & Silver" Dev Diary #9, "Updating your mod". The control mappings are vanilla's own
(1.21 traits, perks, domicile buildings and epidemics were converted exactly this way).
Added in Supernatural 2.41. Companion to apply_upstream_edits.py and apply_ck3_120_port.py. Standard library only.
"""
import os, re, sys

# Order matters: longer names first so a prefix never eats a longer key.
CODE_RENAMES = [
    ('character_capital_county_monthly_development_growth_add', 'character_capital_county_monthly_prosperity_growth_add'),
    ('world_innovation_elephants_development_growth_factor', 'world_innovation_elephants_prosperity_growth_factor'),
    ('development_towards_level_increase', 'prosperity_towards_level_increase'),
    ('development_growth_factor', 'prosperity_growth_factor'),
    ('development_decline_factor', 'prosperity_decline_factor'),
    ('development_growth', 'prosperity_growth'),
    ('development_decline', 'prosperity_decline'),
    ('change_development_level', 'change_prosperity_level'),
    ('change_development_progress', 'change_prosperity_progress'),
    ('development_level', 'prosperity_level'),
    ('development_rate', 'prosperity_rate'),
    ('major_development_progress_loss', 'major_prosperity_progress_loss'),
    ('medium_development_progress_loss', 'medium_prosperity_progress_loss'),
    ('minor_development_progress_loss', 'minor_prosperity_progress_loss'),
    ('county_opinion_add', 'popular_opinion_add'),
    ('county_holder_opinion', 'popular_opinion'),
    ('county_opinion', 'popular_opinion'),
    ('monthly_county_control_growth_add', 'monthly_control_change_when_below_baseline_add'),
    ('monthly_county_control_growth_factor', 'monthly_control_change_when_below_baseline_mult'),
    ('monthly_county_control_decline_add', 'monthly_control_change_when_above_baseline_add'),
    ('monthly_county_control_decline_factor', 'monthly_control_change_when_above_baseline_mult'),
    ('tax_mult', 'all_tax_mult'),
    ('has_special_building_slot', 'has_special_district_slot'),
    ('has_special_building', 'has_special_district'),
    ('has_ongoing_construction', 'has_ongoing_holding_construction'),
]
# The mod's own special buildings, which 1.21 places through a wrapper district (zz_spn_magic_districts.txt).
SPECIAL = ['mage_tower_01', 'mage_tower_02', 'mage_tower_03', 'witch_house', 'horned_god_house', 'mage_house', 'houska']
# Building loc keys lose their building_ prefix in 1.21 (<key> / <key>_desc).
MOD_BUILDINGS = SPECIAL + ['spn_order_collegium_01']
CONCEPTS = [('development', 'prosperity'), ('county_opinion', 'popular_opinion')]

CHANGES = []
# A dotted link (root.capital_county.development_level) is renamed too; only @values, $params$ and longer names are skipped.
B = r'(?<![A-Za-z0-9_@$])'; E = r'(?![A-Za-z0-9_])'

def split_comment(line):
    inq = False
    for i, c in enumerate(line):
        if c == '"': inq = not inq
        elif c == '#' and not inq: return line[:i], line[i:]
    return line, ''

def load(p):
    raw = open(p, 'rb').read(); bom = raw.startswith(b'\xef\xbb\xbf'); t = raw.decode('utf-8-sig')
    return t, bom
def save(p, t, bom):
    open(p, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf-8'))

def port_code(text, rel):
    out = []; n = 0
    in_building_file = rel.replace('\\', '/').startswith('common/buildings/')
    for line in text.split('\n'):
        code, com = split_comment(line)
        for old, new in CODE_RENAMES:
            code, k = re.subn(B + old + E, new, code); n += k
        # add_special_building_slot = X / add_special_building = X  ->  the X_district wrapper
        code, k = re.subn(r'\badd_special_building_slot(\s*=\s*)(' + '|'.join(SPECIAL) + r')\b', r'add_special_district_slot\1\2_district', code); n += k
        code, k = re.subn(r'\badd_special_building(\s*=\s*)(' + '|'.join(SPECIAL) + r')\b', r'add_special_district\1\2_district', code); n += k
        # a building's PROVINCE income is a tax category in 1.21 (character monthly_income is unchanged)
        if in_building_file:
            code, k = re.subn(B + r'monthly_income' + E, 'monthly_generic_tax', code); n += k
        # loc keys named in script
        for b in MOD_BUILDINGS:
            code, k = re.subn(r'\bbuilding_' + b + r'(_desc)?\b', b + r'\1', code); n += k
        out.append(code + com)
    return '\n'.join(out), n

def port_loc(text):
    n = 0
    for b in MOD_BUILDINGS:
        text, k = re.subn(r'(?m)^(\s*)building_' + b + r'(_desc)?:', r'\1' + b + r'\2:', text); n += k
        text, k = re.subn(r'\$building_' + b + r'(_desc)?\$', '$' + b + r'\1$', text); n += k
    for old, new in CONCEPTS:
        text, k = re.subn(r'\[' + old + r'(\|[A-Za-z]+\])', '[' + new + r'\1', text); n += k
    text, k = re.subn(r'world_innovation_elephants_development_growth_factor', 'world_innovation_elephants_prosperity_growth_factor', text); n += k
    return text, n

root = os.path.dirname(os.path.abspath(__file__))
for top in ('common', 'events', 'history', 'localization'):
    for dp, _, fs in os.walk(os.path.join(root, top)):
        for f in fs:
            p = os.path.join(dp, f); rel = os.path.relpath(p, root)
            if f.endswith('.txt') and top != 'localization':
                t, bom = load(p); new, n = port_code(t, rel)
            elif f.endswith('.yml'):
                t, bom = load(p); new, n = port_loc(t)
            else: continue
            if n and new != t:
                save(p, new, bom); CHANGES.append((rel, n))

for rel, n in sorted(CHANGES): print(f'{n:5d}  {rel}')
print(f'\n{sum(n for _, n in CHANGES)} replacements in {len(CHANGES)} files' if CHANGES else 'Nothing to change: already ported.')
