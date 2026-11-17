#!/usr/bin/env python3
"""
Supernatural -- the CK3 1.21 modifier budget.  Run from the mod root:   py apply_ck3_121_terrain_budget.py

Why: CK3 reserves room for 8192 modifier types. Every terrain type generates ~30 of them in 1.21 (25 in 1.20), and
Witchcraft defines 141 "fake" terrains (common/terrain_types/00_terrains_magicc.txt) only so that a trait or modifier
can show a line such as "Unlocks Arcane Focus for Witches" (<name>_terrain_cancel_negative_supply = yes) or "Fire: +3"
(<name>_terrain_advantage = 3). That is ~4,200 modifier types, and the 2.41 boot log showed
"Modifier definitions are full at 8192". No province has these terrains, so none of their modifiers does anything.

What this does (idempotent; a second run changes nothing):
  1. DEAD: drops the fake terrains whose modifiers are used nowhere in script (only in comments or as loc text).
     Their loc keys stay, because the text is still pasted elsewhere as $key$.
  2. MOVES: a fake terrain used only for its _advantage line still owns an unused _cancel_negative_supply slot.
     A yes/no line from a terrain that has nothing else is moved into that slot (same loc text, same format, a new
     key name), and the emptied terrain is dropped. Each move is paired by family where one exists.
Code is renamed outside comments; localization only at keys and $key$ references (Russian text untouched).
Added in Supernatural 2.41. Standard library only.
"""
import os, re

DEAD = ['alchemy_archmage', 'custom_spell', 'demon_domination', 'domination_range', 'immortality', 'immune_for_illness',
        'legendary_mage', 'mage_magic_research', 'magic_pen', 'magic_pro', 'master_defence', 'md_demon_damage',
        'md_demon_pc', 'md_doom_spell2', 'md_doom_spell3', 'md_doom_spell', 'md_power_clash2', 'md_power_clash',
        'necromancer2_special1', 'wc_allows_raiding', 'wh2_eso']
# source yes/no terrain -> terrain that keeps its _advantage line and lends its free yes/no slot
MOVES = [
    ('blackgrimoire_study', 'blackgrimoire_demonology'),
    ('crown2', 'corruption_chance'),
    ('combat_spells', 'e_endurance'),
    ('demon_firestorm', 'e_fire'),
    ('mage_countering_spec1', 'e_kinetic'),
    ('necromancer2_special2', 'e_necrotic2'),
    ('mr_curse_expert_spec1', 'e_necrotic'),
    ('demon_power_strike', 'e_power'),
    ('mage_alchemy4', 'mage_alchemy'),
    ('valuable_magic_component', 'mage_alchemy2'),
    ('mage_summit_enables', 'mage_summit_discount'),
    ('mc_black_mage_special2', 'magic_epic_cooldown'),
    ('true_source', 'magic_gain'),
    ('mage_house_learn', 'mr_add_option'),
    ('legendary_mage2', 'mr_progress_boost'),
    ('mage_alchemy3', 'spec_master_alteration'),
    ('source4B', 'true3_source'),
    ('ultimate_spell_control', 'ultimate_spell_bonus'),
    ('search_artifacts', 'wc_enemy_steal_artifact'),
]
SFX = '_terrain_cancel_negative_supply'
root = os.path.dirname(os.path.abspath(__file__))
TERRAIN_FILE = os.path.join(root, 'common', 'terrain_types', '00_terrains_magicc.txt')
FORMAT_FILE = os.path.join(root, 'common', 'modifier_definition_formats', '01_lifestyle_definitions_magic.txt')
CHANGES = []

def load(p):
    raw = open(p, 'rb').read(); return raw.decode('utf-8-sig'), raw.startswith(b'\xef\xbb\xbf')
def save(p, t, bom):
    open(p, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf-8'))
def split_comment(line):
    inq = False
    for i, c in enumerate(line):
        if c == '"': inq = not inq
        elif c == '#' and not inq: return line[:i], line[i:]
    return line, ''

def drop_block(text, key):
    """Remove a top-level `key = { ... }` block (brace-matched) and the blank line after it."""
    m = re.search(r'(?m)^' + re.escape(key) + r'\s*=\s*\{', text)
    if not m: return text, 0
    i = m.end(); depth = 1
    while depth:
        c = text[i]
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        i += 1
    j = i
    while j < len(text) and text[j] in ' \t': j += 1
    if j < len(text) and text[j] == '\r': j += 1
    if j < len(text) and text[j] == '\n': j += 1
    return text[:m.start()] + text[j:], 1

renames = [(s + SFX, d + SFX) for s, d in MOVES]
for top in ('common', 'events', 'gui', 'localization'):
    for dp, _, fs in os.walk(os.path.join(root, top)):
        for f in fs:
            p = os.path.join(dp, f); rel = os.path.relpath(p, root)
            if not f.endswith(('.txt', '.gui', '.yml')): continue
            t, bom = load(p); n = 0
            if f.endswith('.yml'):
                for old, new in renames:
                    t, k = re.subn(r'(?m)^(\s*)' + old + r'(:)', r'\g<1>' + new + r'\2', t); n += k
                    t, k = re.subn(r'\$' + old + r'\$', '$' + new + '$', t); n += k
            else:
                lines = t.split('\n')
                for i, line in enumerate(lines):
                    code, com = split_comment(line)
                    for old, new in renames:
                        code, k = re.subn(r'(?<![A-Za-z0-9_])' + old + r'(?![A-Za-z0-9_])', new, code); n += k
                    lines[i] = code + com
                t = '\n'.join(lines)
            if n: save(p, t, bom); CHANGES.append((rel, n))

# drop the emptied and dead terrains, and every format block of a terrain that no longer exists
t, bom = load(TERRAIN_FILE); n = 0
for name in DEAD + [s for s, _ in MOVES]:
    t, k = drop_block(t, name + '_terrain'); n += k
if n: save(TERRAIN_FILE, t, bom); CHANGES.append((os.path.relpath(TERRAIN_FILE, root), n))
alive = set(re.findall(r'(?m)^([A-Za-z0-9_]+_terrain)\s*=\s*\{', t))
f, bom = load(FORMAT_FILE); n = 0
for key in re.findall(r'(?m)^([A-Za-z0-9_]+_terrain)_[a-z_]+\s*=\s*\{', f):
    if key not in alive:
        for full in re.findall(r'(?m)^(' + key + r'_[a-z_]+)\s*=\s*\{', f):
            f, k = drop_block(f, full); n += k
if n: save(FORMAT_FILE, f, bom); CHANGES.append((os.path.relpath(FORMAT_FILE, root), n))

for rel, n in sorted(CHANGES): print(f'{n:5d}  {rel}')
print(f'\nfake terrains now: {len(alive)}' if CHANGES else 'Nothing to change: already applied.')
