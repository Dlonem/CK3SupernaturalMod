#!/usr/bin/env python3
"""
Supernatural -- re-apply the mod's deliberate edits to files that come from the upstream Witchcraft mod.

Run from the mod root after copying a new Witchcraft release over:   py apply_upstream_edits.py
Idempotent: an edit that is already present is skipped; one whose anchor text has moved is reported so the
merge can be done by hand. Nothing here touches Supernatural's own files.

Added 2.34 (WORK-ORDER-2.34-v3-BUILD). Each entry: (file, old, new).
"""
import re, sys, os

EDITS = []
def E(path, old, new): EDITS.append((path, old, new))

# ---- common/decisions/magic_dec.txt ---------------------------------------------------------------
E("common/decisions/magic_dec.txt",
"""	effect = {
		remove_trait = supernatural_hunter
		#add_trait_force_tooltip = witch_hunter2
		give_witch_secret_or_trait_effect2 = yes
""",
"""	effect = {
		# 2.34: was a bare remove_trait, which left spn_known_hunter and the hunter secret behind (Workshop report, Aug 2026).
		# spn_initiate.3002 is the mod's one complete hunter cleanup; use it so the two never drift apart again.
		show_as_tooltip = { remove_trait = supernatural_hunter }
		hidden_effect = { trigger_event = spn_initiate.3002 }
		#add_trait_force_tooltip = witch_hunter2
		give_witch_secret_or_trait_effect2 = yes
""")
E("common/decisions/magic_dec.txt",
"""	is_shown = {
		is_imprisoned = no
		is_adult = yes
		#trait_is_criminal_in_faith_trigger = { TRAIT = trait:witch FAITH = root.faith GENDER_CHARACTER = root }
		has_trait = witch_hunter
		
	}
""",
"""	is_shown = {
		is_imprisoned = no
		is_adult = yes
		#trait_is_criminal_in_faith_trigger = { TRAIT = trait:witch FAITH = root.faith GENDER_CHARACTER = root }
		# 2.34 (Supernatural): witch_hunter is the CAPSTONE of the witch-hunter tree ("True Witch Hunter"); you should not
		# need it to begin hunting. The hunt opens on the first witch_hunting track threshold, or on the tree's root perk,
		# whose tooltip has always promised exactly this. The trait stays as a branch for the paths that grant it directly.
		OR = {
			has_trait = witch_hunter
			has_perk = antimage_perk
			has_trait_xp = { trait = supernatural_hunter track = witch_hunting value >= 25 }
		}
	}
""")
E("common/decisions/magic_dec.txt",
"""			has_perk = combat_spells_p3_perk
		}
	}
	is_valid_showing_failures_only = {
""",
"""			OR = { has_perk = combat_spells_p3_perk has_perk = combat_spells_perk } # 2.34 (Supernatural): the hunter's Combat Spells perk reaches the Witcher's elixirs
		}
	}
	is_valid_showing_failures_only = {
""")

# ---- common/traits/00_traits_magic.txt -----------------------------------------------------------
E("common/traits/00_traits_magic.txt",
"""	opposites = {
		warlock
		supernatural_hunter
		witch_hunter
	}
""",
"""	opposites = {
		# 2.34: `warlock` removed. archmage and warlock are both lifestyle capstones; with the exclusion whichever one
		# was bought second silently failed to add (Workshop report, Aug 2026). witch_hunter stays -- the capstone perks
		# now refuse to be picked by a hunter instead of failing silently.
		supernatural_hunter
		witch_hunter
	}
""")
E("common/traits/00_traits_magic.txt",
"""demon1 = {
	name = minor_demon
	desc = trait_demon_desc
	icon = demon.dds
""",
"""demon1 = {
	flag = blocks_getting_non_epidemic_disease # 2.34 (Supernatural): demons do not sicken; the epidemic half is the immune_to_disease flag, set by spn_retro_disease_immunity
	name = minor_demon
	desc = trait_demon_desc
	icon = demon.dds
""")
E("common/traits/00_traits_magic.txt",
"""demon2 = {
	name = {
""",
"""demon2 = {
	flag = blocks_getting_non_epidemic_disease # 2.34 (Supernatural): see demon1
	name = {
""")

# ---- the three magic capstone perks: a hunter cannot buy a perk whose trait it cannot hold -------------
GUARD = """		custom_description = {
			text = spn_capstone_blocked_by_hunter
			NOR = { has_trait = witch_hunter has_trait = supernatural_hunter }
		}
"""
E("common/lifestyle_perks/00_magic_1_arcane_tree_perks.txt",
"""	trait = archmage
	can_be_picked = {
		OR = {
			has_focus = arcane_focus
			is_true_mage = yes
		}
	}
""",
"""	trait = archmage
	can_be_picked = {
		OR = {
			has_focus = arcane_focus
			is_true_mage = yes
		}
		# 2.34: archmage is an opposite of the hunter traits; a perk must never be purchasable when its trait cannot be added
""" + GUARD + """	}
""")
E("common/lifestyle_perks/00_magic_1_arcane_tree_perks.txt",
"""	effect = {
		add_trait_force_tooltip = archmage
		#custom_tooltip = mage_p4_perk_ctt
""",
"""	effect = {
		add_trait_force_tooltip = archmage
		hidden_effect = { # 2.34: the mage's memory, once; anchors the "What the Word Meant" event
			if = {
				limit = { NOT = { any_memory = { has_memory_type = spn_became_a_mage_memory } } }
				create_character_memory = { type = spn_became_a_mage_memory }
			}
		}
		#custom_tooltip = mage_p4_perk_ctt
""")
E("common/lifestyle_perks/00_magic_2_blackmagic_tree_perks.txt",
"""	can_be_picked = {
		AND = {
			has_focus = blackmagic_focus
			has_perk = summoner_p8_perk
		}
	}

	trait = warlock
""",
"""	can_be_picked = {
		AND = {
			has_focus = blackmagic_focus
			has_perk = summoner_p8_perk
		}
		# 2.34: warlock is an opposite of the hunter traits; a perk must never be purchasable when its trait cannot be added
""" + GUARD + """	}

	trait = warlock
""")
E("common/lifestyle_perks/00_magic_3_witch_tree_perks.txt",
"""	parent = magical_senses_perk
	
	trait = true_witch
	effect = {
		custom_tooltip = true_witch_perk_tt
""",
"""	parent = magical_senses_perk
	
	trait = true_witch
	# 2.34: true_witch is an opposite of the hunter traits; a perk must never be purchasable when its trait cannot be added
	can_be_picked = {
""" + GUARD + """	}
	effect = {
		custom_tooltip = true_witch_perk_tt
""")

# ---- events -----------------------------------------------------------------------------------------
E("events/ev3.txt",
"""	option = {
		name = ev3.53.a
		add_trait = witch_hunter
		create_witch_hunter_crossbow_effect = yes
""",
"""	option = {
		name = ev3.53.a
		# 2.34: was `add_trait = witch_hunter` -- the capstone of a tree the graduate could not even enter, since every
		# perk in it needs supernatural_hunter (Workshop report, Aug 2026). The quest now makes a hunter with a head start.
		add_trait_force_tooltip = supernatural_hunter
		trigger_event = spn_initiate.3001 #Initiate Hunter
		hidden_effect = {
			add_trait_xp = { trait = supernatural_hunter track = witch_hunting value = 25 }
		}
		create_witch_hunter_crossbow_effect = yes
""")
E("events/ev4.txt",
"""					else = {
						random = {
							chance = 10
							add_trait = witch_hunter
						}
					}
""",
"""					else = {
						# 2.34: a 10% roll used to hand out witch_hunter, the witch-hunter tree's capstone ("True Witch Hunter").
						# A duel win now starts someone on the road instead: supernatural_hunter plus witch_hunting track XP.
						random = {
							chance = 10
							trigger_event = spn_initiate.3001 #Initiate Hunter
							hidden_effect = {
								add_trait_xp = { trait = supernatural_hunter track = witch_hunting value = 25 }
							}
						}
					}
""")
E("events/ev2.txt",
"""	immediate = {
		add_trait = witch_hunter
		#add_perk = protective_runes_perk
		#add_perk = magical_senses_perk
		create_witch_hunter2_amulet_artifact_effect = yes
""",
"""	immediate = {
		# 2.34: the inquisitor was given witch_hunter and 90 witch_hunting XP but never supernatural_hunter, the trait the
		# track lives on -- so the XP went nowhere. Make them a real hunter first; the capstone trait stays (they are the world's veteran).
		trigger_event = spn_initiate.3001 #Initiate Hunter
		add_trait = witch_hunter
		#add_perk = protective_runes_perk
		#add_perk = magical_senses_perk
		create_witch_hunter2_amulet_artifact_effect = yes
""")
E("common/on_action/yearly2_on_actions.txt",
"""			player_heir = {
				add_trait = witch_hunter
				if = {
					limit = {
						NOT = {
							has_perk = protective_runes_perk
""",
"""			player_heir = {
				# 2.34: the heir used to inherit witch_hunter itself -- the capstone ("True Witch Hunter") of a tree they never
				# entered. They now inherit the calling: supernatural_hunter (spn_initiate.3001 is a no-op if they already have
				# it or are a creature) and a head start on the witch_hunting track.
				trigger_event = spn_initiate.3001 #Initiate Hunter
				add_trait_xp = { trait = supernatural_hunter track = witch_hunting value = 25 }
				if = {
					limit = {
						NOT = {
							has_perk = protective_runes_perk
""")
E("common/scripted_effects/00_variety_magic_effects.txt",
"""		add_trait_xp = {
			trait = witch_hunter
			value = 100
		}
""",
"""		add_trait_xp = { # 2.34 (Supernatural): witch_hunter has no track since the rewrite; the witch_hunting track lives on supernatural_hunter
			trait = supernatural_hunter
			track = witch_hunting
			value = 100
		}
""")
E("common/character_interactions/00_magic_interactions.txt",
"""		scope:actor = {
				is_adult = yes
				has_trait = witch_hunter
				#has_trait_xp = {
				#	trait = supernatural_hunter
				#	track = witch_hunting
				#	value > 29
				#}
				is_imprisoned = no
""",
"""		scope:actor = {
				is_adult = yes
				# 2.34 (Supernatural): same gate as witch_hunting_decision -- the capstone trait, the root perk, or the first track threshold
				OR = {
					has_trait = witch_hunter
					has_perk = antimage_perk
					has_trait_xp = { trait = supernatural_hunter track = witch_hunting value >= 25 }
				}
				is_imprisoned = no
""")

# ---- localisation: a memory participant tag that was never declared -------------------------------------
# (character_memories_magic.txt declares `target0`; the third-person string referenced `victim`.) Russian is human
# translation and is left alone on purpose -- fix that one line by hand.
LOC_FIX = [("localization/%s/event_localization/witch_ep4_l_%s.yml" % (l, l)) for l in
           ("english","french","german","korean","polish","simp_chinese","spanish")]
def apply_loc_fix():
    for path in LOC_FIX:
        if not os.path.exists(path): print("MISSING FILE", path); continue
        s = read(path); nl = nl_of(s); lines = s.split(nl); changed = False
        for i, ln in enumerate(lines):
            if ln.lstrip().startswith("discovered_magical_item_desc_third_perspective_1") and "[victim." in ln:
                lines[i] = ln.replace("[victim.", "[target0."); changed = True
        if changed: write(path, nl.join(lines)); print("loc fixed", path)

# ---- auto_selection_weight for the three magic trees (they were the only trees without one) ---------------
MAGIC_PERK_FILES = [
    "common/lifestyle_perks/00_magic_1_arcane_tree_perks.txt",
    "common/lifestyle_perks/00_magic_2_blackmagic_tree_perks.txt",
    "common/lifestyle_perks/00_magic_3_witch_tree_perks.txt",
]
WEIGHT_CHILD = """
	auto_selection_weight = { # 2.34 (Supernatural): the three magic trees had no AI weighting past their roots
		value = 0
		if = {
			limit = {
				OR = {
					has_trait = witch
					any_secret = { type = secret_witch }
				}
			}
			add = 2000
		}
	}
"""
WEIGHT_ROOT_GUARD = """		if = {
			limit = { can_start_new_lifestyle_tree_trigger = no } # 2.34 (Supernatural): the tree has a clause in the trigger now
			multiply = 0
		}
"""

def read(p):
    with open(p, encoding="utf-8", newline="") as f: return f.read()
def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f: f.write(s)

def nl_of(s): return "\r\n" if "\r\n" in s else "\n"

def apply_pairs():
    ok = skipped = missing = 0
    for path, old, new in EDITS:
        if not os.path.exists(path):
            print("MISSING FILE", path); missing += 1; continue
        s = read(path); nl = nl_of(s)
        o = old.replace("\n", nl); n = new.replace("\n", nl)
        if n in s:
            skipped += 1; continue
        if s.count(o) != 1:
            print("ANCHOR NOT FOUND (%d hits): %s :: %r" % (s.count(o), path, old[:70])); missing += 1; continue
        write(path, s.replace(o, n)); ok += 1
        print("applied", path)
    return ok, skipped, missing

def apply_weights():
    for path in MAGIC_PERK_FILES:
        if not os.path.exists(path): print("MISSING FILE", path); continue
        s = read(path); nl = nl_of(s); changed = False
        blocks = list(re.finditer(r'^\ufeff?([a-z0-9_]+) = \{[^\r\n]*' + nl + r'(.*?)^\}(?:' + nl + r'|\Z)', s, re.S | re.M))
        out = s
        for m in reversed(blocks):
            name, body = m.group(1), m.group(2)
            is_root = not re.search(r'^\s*parent =', body, re.M)
            if "auto_selection_weight" not in body:
                im = re.search(r'^\ticon = [^\r\n]*' + nl, body, re.M)
                if not im: print("no icon line in", name); continue
                body2 = body[:im.end()] + WEIGHT_CHILD.replace("\n", nl) + body[im.end():]
                if is_root:
                    body2 = body2.replace("\t\t\tadd = 2000" + nl + "\t\t}" + nl + "\t}" + nl,
                                          "\t\t\tadd = 2000" + nl + "\t\t}" + nl + WEIGHT_ROOT_GUARD.replace("\n", nl) + "\t}" + nl, 1)
                out = out[:m.start(2)] + body2 + out[m.end(2):]; changed = True
            elif is_root and "can_start_new_lifestyle_tree_trigger" not in body:
                wm = re.search(r'^\tauto_selection_weight = \{' + nl + r'(.*?)^\t\}' + nl, body, re.S | re.M)
                if not wm: print("odd weight block in", name); continue
                body2 = body[:wm.end(1)] + WEIGHT_ROOT_GUARD.replace("\n", nl) + body[wm.end(1):]
                out = out[:m.start(2)] + body2 + out[m.end(2):]; changed = True
        if changed:
            write(path, out); print("weighted", path)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
    ok, skipped, missing = apply_pairs()
    apply_weights()
    apply_loc_fix()
    print("done: %d applied, %d already present, %d need a hand merge" % (ok, skipped, missing))
    sys.exit(1 if missing else 0)
