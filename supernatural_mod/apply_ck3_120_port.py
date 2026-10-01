#!/usr/bin/env python3
"""
Supernatural -- re-apply the CK3 1.20 ("Crozier") port to files that come from the upstream Witchcraft mod.

Run from the mod root AFTER copying a new Witchcraft release over and AFTER apply_upstream_edits.py:

    py apply_upstream_edits.py
    py apply_ck3_120_port.py

Idempotent: an edit that is already present is skipped. An anchored edit whose anchor has moved is reported
as NEEDS A HAND MERGE and nothing is written for it. The mechanical sweeps (faith -> rite triggers, the
erudite rename, stress_and_fulfillment_impact, rite next to faith) run over every .txt under common/, events/
and history/, so they also catch anything a fresh upstream copy brings back in 1.19 form. On Supernatural's own
files they find nothing to do.

What this script does NOT redo (it cannot, without the vanilla files to merge against): the blocks and files
that 2.36 rebased onto vanilla 1.20. If an upstream update touches one of them, the script says so at the end
(it compares against the 2.36 text) and that one is a Beyond Compare job against vanilla 1.20.

Added in Supernatural 2.36. Companion to apply_upstream_edits.py (2.34). Standard library only.
"""
import os, re, sys, difflib, hashlib

APPLIED, SKIPPED, HAND = [], [], []

# ------------------------------------------------------------------------------------------------- io
def load(path):
    raw = open(path, 'rb').read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    orig = raw.decode('utf-8-sig')
    return orig.replace('\r\n', '\n'), (bom, orig)

def save(path, text, meta):
    """Write LF text back with the file's own BOM and line endings (mixed files keep each unchanged line's ending)."""
    bom, orig = meta
    n_crlf, n_lf = orig.count('\r\n'), orig.count('\n')
    if n_crlf and n_crlf != n_lf:
        olines = orig.split('\n'); okeys = [l[:-1] if l.endswith('\r') else l for l in olines]
        nlines = text.split('\n'); maj = '\r' if n_crlf * 2 >= n_lf else ''
        out = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, okeys, nlines, autojunk=False).get_opcodes():
            out.extend(olines[i1:i2] if tag == 'equal' else [l + maj for l in nlines[j1:j2]])
        data = '\n'.join(out)
    else:
        data = text.replace('\n', '\r\n') if n_crlf else text
    open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + data.encode('utf-8'))

def split_comment(line):
    inq = False
    for i, c in enumerate(line):
        if c == '"': inq = not inq
        elif c == '#' and not inq: return line[:i], line[i:]
    return line, ''

def code_sub(text, pattern, repl):
    """Regex substitution on the code part of each line only (comments untouched)."""
    rx = re.compile(pattern); n = 0; out = []
    for line in text.split('\n'):
        code, com = split_comment(line)
        new, k = rx.subn(repl, code); n += k
        out.append(new + com)
    return '\n'.join(out), n

def find_block(text, key):
    """(start, end) of a top-level `key = { ... }` block, comment- and string-aware."""
    m = re.search(r'(?m)^﻿?' + re.escape(key) + r'\s*=\s*\{', text)
    if not m: return None
    i, d, inq = m.end(), 1, False
    while i < len(text) and d:
        c = text[i]
        if c == '"': inq = not inq
        elif not inq and c == '#':
            j = text.find('\n', i); i = len(text) if j < 0 else j; continue
        elif not inq and c == '{': d += 1
        elif not inq and c == '}': d -= 1
        i += 1
    return m.start(), i

# ------------------------------------------------------------------------------ the mechanical sweeps
# S5 -- vanilla 1.20 deleted the *_in_faith_trigger family; the *_in_rite_trigger versions take RITE = x.rite
TRIG = r'\b(trait_is_criminal|trait_is_shunned|trait_is_shunned_or_criminal)_in_faith_trigger(\s*=\s*\{[^}]*?)\bFAITH\s*=\s*([^\s}]+)\.faith\b'
REL = r'\b(relation_with_character_is_(?:sodomy|incestuous))_in_faith_trigger(\s*=\s*\{[^}]*?)\bFAITH\s*=\s*([^\s}]+)\.faith\b'
def sweep_rite_triggers(t):
    n = 0
    for pat, rep in ((TRIG, r'\1_in_rite_trigger\2RITE = \3.rite'), (REL, r'\1_in_rite_trigger\2RITE = \3.rite'),
                     (r'\btrait_is_shunned_or_criminal_in_my_or_lieges_faith_trigger\b', 'trait_is_shunned_or_criminal_in_my_or_lieges_rite_trigger'),
                     (r'\brelation_with_character_is_sodomy_in_my_or_lieges_faith_trigger\b', 'relation_with_character_is_sodomy_in_my_or_lieges_rite_trigger'),
                     (r'\brelation_with_character_is_incestuous_in_my_faith_trigger\b', 'relation_with_character_is_incestuous_in_my_rite_trigger')):
        t, k = code_sub(t, pat, rep); n += k
    return t, n

# S7 -- `faith = { has_doctrine(_parameter) = x }` on a character -> `rite = { rite_has_doctrine / rite_has_parameter = x }`.
# Only blocks whose whole content is doctrine/parameter/virtue/sin checks; faith-only doctrines (head of faith...) stay.
def _tokens(text):
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '#':
            j = text.find('\n', i); i = n if j < 0 else j; continue
        if c == '"':
            j = text.find('"', i + 1); j = n - 1 if j < 0 else j; yield ('str', i, j + 1, text[i:j + 1]); i = j + 1; continue
        if c in '{}': yield (c, i, i + 1, c); i += 1; continue
        if c.isspace(): i += 1; continue
        m = re.match(r'[^\s{}#"=<>!?]+|[=<>!?]+', text[i:])
        yield ('w', i, i + m.end(), m.group(0)); i += m.end()
FAITH_OPENER = re.compile(r'^((?:[A-Za-z_]+:[A-Za-z_\.@$]+|root|this|prev|\$[A-Z_]+\$|[a-z_]+)\.)?faith$')
SAFE = set('has_doctrine has_doctrine_parameter trait_is_virtue trait_is_sin NOT NOR OR AND = yes no limit'.split())
FAITH_ONLY = set('doctrine_spiritual_head doctrine_temporal_head doctrine_no_head religious_head religion religion_tag '
                 'faith_hostility_level has_doctrine_parameter_count holy_site any_holy_site save_scope_as '
                 'save_temporary_scope_as is_in_family'.split())
VALUE_WORD = re.compile(r'^(doctrine_|tenet_|spn_|witchcraft_|[a-z_]+_(illegal|shunned|accepted|crime|active|none|restricted|marriage|penalty|reduced|minimal)$)')
def _faith_blocks(text):
    toks = list(_tokens(text)); res = []
    for k, (kind, s, e, v) in enumerate(toks):
        if kind == 'w' and FAITH_OPENER.match(v) and k + 2 < len(toks) and toks[k + 1][3] in ('=', '?=') and toks[k + 2][0] == '{':
            d = 0
            for m in range(k + 2, len(toks)):
                if toks[m][0] == '{': d += 1
                elif toks[m][0] == '}':
                    d -= 1
                    if d == 0: break
            inner = [t[3] for t in toks[k + 3:m]]
            words = set(w for w in inner if w not in ('{', '}'))
            if not any(w in ('has_doctrine', 'has_doctrine_parameter', 'trait_is_virtue', 'trait_is_sin') for w in inner): continue
            faith_only = words & FAITH_ONLY
            other = [w for w in words if w not in SAFE and not VALUE_WORD.match(w) and w not in FAITH_ONLY]
            if not faith_only and not other:
                res.append((s, toks[m][2], v))
    return res
def sweep_faith_blocks(t):
    bl = _faith_blocks(t)
    for s, e, opener in sorted(bl, key=lambda b: -b[0]):
        seg = t[s:e]; body = seg[len(opener):]
        body = re.sub(r'\bhas_doctrine_parameter\b', 'rite_has_parameter', body)
        body = re.sub(r'(?<![_\w])has_doctrine\s*=\s*(tenet_\w+)', r'rite_has_tenet = \1', body)
        body = re.sub(r'(?<![_\w])has_doctrine\b', 'rite_has_doctrine', body)
        body = re.sub(r'(?<![_\w])trait_is_virtue\b', 'trait_is_virtue_rite', body)
        body = re.sub(r'(?<![_\w])trait_is_sin\b', 'trait_is_sin_rite', body)
        t = t[:s] + opener[:-len('faith')] + 'rite' + body + t[e:]
    return t, len(bl)

# S8 -- vanilla 1.20 renamed the trait scholar -> erudite and the perk scholar_perk -> erudite_perk
def sweep_erudite(t):
    n = 0
    for pat, rep in ((r'\bscholar_perk\b', 'erudite_perk'),
                     (r'\b(has_trait|add_trait|remove_trait|add_trait_force_tooltip|trait)(\s*=\s*)scholar\b', r'\1\2erudite'),
                     (r'(?<![\w:])scholar(\s*=\s*(?:minor_|medium_|major_|miniscule_|massive_)?stress_)', r'erudite\1'),
                     (r'(?<![\w:])scholar(\s*=\s*@(?:pos|neg)_compat)', r'erudite\1'),
                     (r'(?<![\w:])scholar(\s*=\s*\{\s*\})', r'erudite\1'),
                     (r'\btrait:scholar\b', 'trait:erudite')):
        t, k = code_sub(t, pat, rep); n += k
    return t, n

# S19 -- vanilla 1.20 moved ~12,100 of its own stress_impact blocks to stress_and_fulfillment_impact (same syntax;
# the old one still works but never moves Spiritual Fulfillment)
def sweep_fulfillment(t):
    return code_sub(t, r'\bstress_impact = \{', 'stress_and_fulfillment_impact = {')

# S20 -- copying someone's faith copies their Rite too (vanilla 1.20's own pattern)
def sweep_rite_copy(t):
    n = 0; out = []; pos = 0
    for m in re.finditer(r'create_character\s*=\s*\{', t):
        if m.start() < pos: continue
        i = m.end(); d = 1; j = i
        while d and j < len(t):
            if t[j] == '{': d += 1
            elif t[j] == '}': d -= 1
            j += 1
        lines = t[i:j - 1].split('\n'); depth = 0; has_rite = False; fidx = None
        for k, line in enumerate(lines):
            code, _ = split_comment(line)
            if depth == 0:
                if re.match(r'\s*rite\s*=', code): has_rite = True
                mm = re.match(r'(\s*)faith\s*=\s*(\S+)\.faith\s*$', code)
                if mm: fidx, ind, expr = k, mm.group(1), mm.group(2)
            depth += code.count('{') - code.count('}')
        if fidx is not None and not has_rite:
            lines.insert(fidx + 1, '%srite = %s.rite' % (ind, expr)); n += 1
        out.append(t[pos:i]); out.append('\n'.join(lines)); pos = j - 1
    out.append(t[pos:]); t = ''.join(out)
    lines = t.split('\n'); out = []
    for k, line in enumerate(lines):
        out.append(line)
        code, _ = split_comment(line)
        mm = re.match(r'^(\s*)set_character_faith = (\S+)\.faith\s*$', code)
        if mm and 'set_character_rite' not in (lines[k + 1] if k + 1 < len(lines) else ''):
            out.append('%sset_character_rite = %s.rite' % (mm.group(1), mm.group(2))); n += 1
    return '\n'.join(out), n

# S20 (templates) -- a character template that copies a faith copies the Rite too (vanilla 1.20: all 68 of its own)
def sweep_template_rite(t):
    lines = t.split('\n'); out = []; depth = 0; n = 0; block = []; state = {'rite': False, 'fl': None}
    def flush():
        nonlocal n
        if state['fl'] is not None and not state['rite']:
            k, ind, expr = state['fl']; block.insert(k + 1, '%srite = %s.rite' % (ind, expr)); n += 1
        out.extend(block)
    for line in lines:
        code, _ = split_comment(line)
        if depth == 0:
            if block: flush()
            block[:] = [line]; state['rite'] = False; state['fl'] = None
        else:
            block.append(line)
            if depth == 1:
                if re.match(r'\s*rite\s*=', code): state['rite'] = True
                mm = re.match(r'(\s*)faith\s*=\s*(\S+)\.faith\s*$', code)
                if mm: state['fl'] = (len(block) - 1, mm.group(1), mm.group(2))
        depth += code.count('{') - code.count('}')
    if block: flush()
    return '\n'.join(out), n

SWEEPS = (('faith -> rite triggers', sweep_rite_triggers), ('faith -> rite doctrine checks', sweep_faith_blocks),
          ('scholar -> erudite', sweep_erudite), ('stress_and_fulfillment_impact', sweep_fulfillment),
          ('rite next to faith', sweep_rite_copy))
SWEEP_SKIP = {'common/scripted_triggers/10_spn_religious_triggers.txt'}   # vanilla 1.20 shadow, written by hand

# --------------------------------------------------------------------------------- anchored edits
PAIRS = []
def E(path, old, new): PAIRS.append((path, old, new))

E('common/scripted_effects/00_magic_spells_effects.txt',   # S6 -- 1.20's excommunication test (tenets are not doctrines)
  "\t\t\t\t\t\tscope:actor.faith = {\n\t\t\t\t\t\t\thas_doctrine = tenet_communion\n\t\t\t\t\t\t\thas_doctrine = doctrine_spiritual_head\n\t\t\t\t\t\t}\n",
  "\t\t\t\t\t\tscope:actor.faith = {\n\t\t\t\t\t\t\tfaith_has_sacraments_central_trigger = yes # CK3 1.20: vanilla's excommunication test; tenet_communion is no longer a doctrine\n\t\t\t\t\t\t\thas_doctrine = doctrine_spiritual_head\n\t\t\t\t\t\t}\n")
E('events/ev7.txt', "faith = {\n\t\t\t\t\t\thas_doctrine = tenet_human_sacrifice\n",
                    "rite = {\n\t\t\t\t\t\trite_has_tenet = tenet_human_sacrifice\n")
E('common/scripted_effects/00_variety_magic_effects.txt',   # S11 -- Ismaili is the main Rite of the Shia faith
  "\t\t\t\texists = culture:persian\n\t\t\t\texists = faith:ismaili\n",
  "\t\t\t\texists = culture:persian\n\t\t\t\texists = faith:shia\t# CK3 1.20: Ismaili is the main Rite of the Shia faith\n\t\t\t\texists = rite:ismaili\n")
E('common/scripted_effects/00_variety_magic_effects.txt', "\t\t\t\tfaith = faith:ismaili\n", "\t\t\t\tfaith = faith:shia\n\t\t\t\trite = rite:ismaili\n")
E('common/decisions/magic_dec.txt', "\t\tcontroller = create_holy_order\n\t\tbarony_valid = {\n",   # S13
                                    "\t\tcontroller = create_holy_order\n\t\ttitle_valid = {\n")
for _f, _id, _icon in (('events/ev7.txt', 'magic_ev7.132', 'splash_legends'),             # S16
                       ('events/ev10.txt', 'magic_ev10.93', 'splash_epidemics'),
                       ('events/ev10.txt', 'magic_ev10.121', 'splash_epidemics')):
    E(_f, '%s = {\n\ttype = character_event\n\twindow = fullscreen_event\n' % _id,
          '%s = {\n\ttype = character_event\n\twindow = fullscreen_event\n\tqueue_icon = "gfx/interface/icons/splash_icons/%s.dds"\t# CK3 1.20: fullscreen events require a queue icon\n' % (_id, _icon))
E('common/character_interactions/00_magic_interactions.txt',   # S20 -- the convert follows the actor's Rite
  '\t\t\t\t\tif = {\n\t\t\t\t\t\tlimit = {\n\t\t\t\t\t\t\tNOT = {\tfaith = scope:actor.faith\t}\n\t\t\t\t\t\t}\n\t\t\t\t\t\tset_character_faith_with_conversion = scope:actor.faith\n\t\t\t\t\t}\n',
  '\t\t\t\t\tif = {\n\t\t\t\t\t\tlimit = {\n\t\t\t\t\t\t\tNOT = {\trite = scope:actor.rite\t}\t# CK3 1.20: the convert follows the actor\'s Rite, not only the Faith\n\t\t\t\t\t\t}\n\t\t\t\t\t\tset_character_rite_with_conversion = scope:actor.rite\n\t\t\t\t\t}\n')

def apply_pairs():
    for path, old, new in PAIRS:
        if not os.path.exists(path): HAND.append('MISSING FILE %s' % path); continue
        t, meta = load(path)
        held = t.replace(new, '\0')          # occurrences already converted are set aside
        n = held.count(old)
        if n == 0:
            if new in t: SKIPPED.append(path)
            else: HAND.append('anchor not found in %s :: %r' % (path, old.strip()[:70]))
            continue
        save(path, held.replace(old, new).replace('\0', new), meta); APPLIED.append('%s (%d)' % (path, n))

# S15 -- 1.20 activity types name their own header art
HEADER = {'common/activities/activity_types/witch_ritual.txt': ('activity_witch_ritual', 'activity_witch_ritual.dds'),
          'common/activities/activity_types/mages_summit.txt': ('mages_summit', 'mages_summit.dds'),
          'common/activities/activity_types/magical_research.txt': ('magical_research', 'magical_research.dds'),
          'common/activities/activity_types/artifacts_searching.txt': ('artifacts_searching', 'artifacts_searching.dds')}
def apply_headers():
    for path, (key, dds) in HEADER.items():
        if not os.path.exists(path): HAND.append('MISSING FILE %s' % path); continue
        t, meta = load(path); r = find_block(t, key)
        if not r: HAND.append('activity %s not found in %s' % (key, path)); continue
        blk = t[r[0]:r[1]]
        if 'header_background' in blk: SKIPPED.append(path); continue
        new = blk[:-1].rstrip('\n') + ('\n\n\t# CK3 1.20: the activity windows read the header art from the activity type.\n'
                                       '\theader_background = "gfx/interface/illustrations/activity_header_backgrounds/%s"\n}' % dds)
        save(path, t[:r[0]] + new + t[r[1]:], meta); APPLIED.append(path + ' (header_background)')

# S22 -- the witch war's victory moves every RITE one step (Faith-scope add_doctrine only reaches the main Rite)
def apply_witch_war():
    path = 'common/casus_belli_types/01_magic_cb.txt'
    if not os.path.exists(path): HAND.append('MISSING FILE %s' % path); return
    t, meta = load(path)
    if 'spn_witch_war_rite' in t: SKIPPED.append(path); return
    head = '\t\t\tevery_religion_global = {\n\t\t\t\tevery_faith = {\n\t\t\t\t\tlimit = {\n\t\t\t\t\t\thas_doctrine = doctrine_witchcraft_accepted'
    if t.count(head) != 1: HAND.append('witch war doctrine shift not found in %s' % path); return
    i = t.index(head); j = t.index('\n\t\t\t}\n\t\t}\n\t}\n\ton_invalidated_desc', i); old = t[i:j + len('\n\t\t\t}')]
    if old.count('every_faith = {') != 3 or old.count('add_doctrine') != 3: HAND.append('witch war block changed shape in %s' % path); return
    inner = old[old.index('\t\t\t\t\t\tevery_faith_character = {'):old.index('\t\t\t\t\tadd_doctrine = doctrine_witchcraft_accepted')]
    inner = inner[:inner.rindex('\t\t\t\t\t}')]
    lim = '\t\t\t\t\t\tevery_faith_character = {\n\t\t\t\t\t\t\tlimit = {\n'
    if not inner.startswith(lim): HAND.append('witch war character block changed shape in %s' % path); return
    inner = lim + '\t\t\t\t\t\t\t\trite = scope:spn_witch_war_rite\n' + inner[len(lim):]
    inner = '\n'.join((('\t\t' + l) if l.strip() else l) for l in inner.rstrip('\n').split('\n')) + '\n'
    new = ('\t\t\t# CK3 1.20: doctrines live on Rites; Faith-scope add_doctrine only reaches each Faith\'s main Rite.\n'
           '\t\t\t# Same three steps as before, applied to every Rite: accepted -> virtuous, shunned -> accepted, crime -> shunned.\n'
           '\t\t\tevery_religion_global = {\n\t\t\t\tevery_faith = {\n'
           '\t\t\t\t\tevery_faith_rite = {\n\t\t\t\t\t\tlimit = { rite_has_doctrine = doctrine_witchcraft_accepted }\n\t\t\t\t\t\tchange_rite_doctrine = doctrine_witchcraft_virtuous\n\t\t\t\t\t}\n'
           '\t\t\t\t\tevery_faith_rite = {\n\t\t\t\t\t\tlimit = { rite_has_doctrine = doctrine_witchcraft_shunned }\n'
           '\t\t\t\t\t\tsave_temporary_scope_as = spn_witch_war_rite\n'
           '\t\t\t\t\t\thidden_effect = {\n\t\t\t\t\t\t\tfaith = {\n' + inner + '\t\t\t\t\t\t\t}\n\t\t\t\t\t\t}\n'
           '\t\t\t\t\t\tchange_rite_doctrine = doctrine_witchcraft_accepted\n\t\t\t\t\t}\n'
           '\t\t\t\t\tevery_faith_rite = {\n\t\t\t\t\t\tlimit = { rite_has_doctrine = doctrine_witchcraft_crime }\n\t\t\t\t\t\tchange_rite_doctrine = doctrine_witchcraft_shunned\n\t\t\t\t\t}\n'
           '\t\t\t\t}\n\t\t\t}')
    save(path, t[:i] + new + t[j + len('\n\t\t\t}'):], meta); APPLIED.append(path + ' (witch war)')

# S8b -- Witchcraft's own `scholar` override would now make an orphan trait nothing grants
def apply_scholar_block():
    path = 'common/traits/00_traits_magic.txt'
    if not os.path.exists(path): return
    t, meta = load(path); r = find_block(t, 'scholar')
    if not r: SKIPPED.append(path); return
    save(path, t[:r[0]] + ('# `scholar` override removed for CK3 1.20 (Supernatural 2.36): vanilla renamed the trait to `erudite`, and this copy\n'
                           '# was already shadowed by Supernatural\'s own in 10_spn_traits.txt. The magic-XP bonus lives on `erudite` there.')
         + t[r[1]:], meta)
    APPLIED.append(path + ' (scholar block)')

# S9 -- 1.19 laws wrapped every law in its group (`camp_purpose = { camp_purpose_x = { } }`); 1.20 refuses that form.
# If a fresh upstream copy brings the old wrapped file back, say so -- 2.36's 01_magic_laws.txt must be put back.
def check_laws():
    path = 'common/laws/01_magic_laws.txt'
    if not os.path.exists(path): HAND.append('MISSING FILE %s' % path); return
    t, _ = load(path)
    if re.search(r'(?m)^camp_purpose\s*=\s*\{', t):
        HAND.append('%s is in the 1.19 wrapped-group form again -- restore the 2.36 file (one standalone '
                    'camp_purpose_seekers law, law_group_type = camp_purpose, index = 6)' % path)
    else: SKIPPED.append(path)

# S17 -- three Witchcraft keys vanilla 1.20 now ships itself (Russian is the translator's and is never touched)
LOC_DUPES = ('scheme_agent_aptitude.trait.lifestyle_mystic', 'murder_enemy_scheme_phase_duration_add',
             'convert_to_witchcraft_scheme_phase_duration_add')
def apply_loc():
    for l in ('english', 'french', 'german', 'korean', 'polish', 'simp_chinese', 'spanish'):
        path = 'localization/%s/event_localization/witch_ep8_l_%s.yml' % (l, l)
        if not os.path.exists(path): continue
        t, meta = load(path); out = []; n = 0
        for ln in t.split('\n'):
            m = re.match(r'^ ([A-Za-z0-9_.]+):\d*\s', ln)
            if m and m.group(1) in LOC_DUPES: n += 1; continue
            out.append(ln)
        if n: save(path, '\n'.join(out), meta); APPLIED.append('%s (%d duplicate keys)' % (path, n))

# S18 -- history characters hold a Rite (vanilla 1.20 history writes rite = ; religion = still loads)
def apply_history():
    path = 'history/characters/magic_chars.txt'
    if not os.path.exists(path): return
    t, meta = load(path); t2, n = code_sub(t, r'^(\s*)religion = "', r'\1rite = "')
    if n: save(path, t2, meta); APPLIED.append('%s (%d)' % (path, n))

# ------------------------------------------------------------------------------- hand-merge watch
# Blocks and files 2.36 rebased onto vanilla 1.20 (three-way merge). md5 of the LF-normalised 2.36 text.
WATCH = {
    ('common/schemes/scheme_types/abduct_scheme.txt', None): '7512e37111fb20b1fb05ddd1fb3b711d',
    ('common/schemes/scheme_types/convert_to_witchcraft_scheme.txt', None): '9b0a545fb85057d1035cff02f3182f2d',
    ('common/schemes/scheme_types/steal_back_artifact_scheme.txt', None): '5c72ed66194d62f15972c8fdde33ce8e',
    ('common/character_interactions/00_overwritten_interactions.txt', 'demand_artifact_interaction'): '05715102249af60863621b4def13c0d5',
    ('common/character_interactions/00_overwritten_interactions.txt', 'disinherit_children_interaction'): '1a810ba785b55b28fc6f8b26e4526068',
    ('common/character_interactions/00_overwritten_interactions.txt', 'disinherit_interaction'): 'b221eee41d245240d9a810349fa536d1',
    ('common/decisions/magic_dec_overwritten.txt', 'hold_mystical_communion_decision'): '9f108ff64720df1b482746cf6ee11156',
    ('common/scripted_triggers/01_interaction_overwritten_triggers.txt', 'title_revocation_is_tyrannical_trigger'): '1b7f786706620ef269b36d4fa7b78f2a',
    ('common/traits/00_traits_magic.txt', 'witch'): '30b434a141cdd196d934281a789085d3',
    ('common/traits/00_traits_magic.txt', 'lifestyle_mystic'): 'a995e3ef0a7efe3b9077dda028089f42',
    ('common/traits/00_traits_magic.txt', 'possessed_1'): '72d9f755547befe7a34b223375475daa',
    ('common/traits/00_traits_magic.txt', 'possessed_genetic'): '7e8758b9127538970912ce440768986e',
    ('common/laws/01_magic_laws.txt', None): 'f00f134795e14813e6eb60ec6ffd431e',
    ('gui/window_activity_planner.gui', None): 'a6967f3f287d0f61b1d42b9a2ce4f242',
    ('gui/window_character_lifestyle.gui', None): 'b9f95ee8ca137d7a1b61e985ca0b3fcc',
}

def watch_report():
    for (path, key), digest in WATCH.items():
        if not os.path.exists(path): HAND.append('MISSING FILE %s' % path); continue
        t, _ = load(path)
        if key:
            r = find_block(t, key)
            if not r: HAND.append('%s :: %s is gone' % (path, key)); continue
            t = t[r[0]:r[1]]
        if hashlib.md5(t.encode('utf-8')).hexdigest() != digest:
            HAND.append('%s%s differs from 2.36 -- it was rebased on vanilla 1.20; merge the upstream change by hand'
                        % (path, (' :: ' + key) if key else ''))

# ------------------------------------------------------------------------------------------- main
def main():
    here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
    swept = {name: 0 for name, _ in SWEEPS}
    for top in ('common', 'events', 'history'):
        for dp, _, fs in os.walk(top):
            for f in fs:
                if not f.endswith('.txt'): continue
                path = os.path.join(dp, f).replace('\\', '/')
                if path in SWEEP_SKIP: continue
                t, meta = load(path); t0 = t
                for name, fn in SWEEPS:
                    t, n = fn(t); swept[name] += n
                if path.startswith('common/scripted_character_templates/'):
                    t, n = sweep_template_rite(t); swept['rite next to faith'] += n
                if t != t0: save(path, t, meta); APPLIED.append(path + ' (sweeps)')
    apply_pairs(); apply_headers(); apply_witch_war(); apply_scholar_block(); check_laws(); apply_loc(); apply_history()
    watch_report()
    for name, n in swept.items(): print('  sweep %-32s %d' % (name, n))
    for a in APPLIED: print('applied   ', a)
    for h in HAND: print('HAND MERGE', h)
    print('done: %d applied, %d already present, %d need a hand merge' % (len(APPLIED), len(SKIPPED), len(HAND)))
    return 1 if HAND else 0

if __name__ == '__main__':
    sys.exit(main())
