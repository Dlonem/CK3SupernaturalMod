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
# 2.39 (WORK-ORDER-2.39 B14, entry 1): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's text
# and never matched upstream
E('common/decisions/magic_dec.txt',
"""	effect = {
		remove_trait = witch_hunter
		add_trait_force_tooltip = witch_hunter2
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
# 2.39 (WORK-ORDER-2.39 B14, entry 2): B9: re-anchored. The 2.35 clause that retires this decision for hunters who
# can ride the Supernatural Hunt was added inside the old text by hand, so the entry asked for a hand merge on every
# run; it is part of `new` now. `old` is Witchcraft 2.18's own text.
E('common/decisions/magic_dec.txt',
"""		has_trait = witch_hunter
		
	}

	#is_valid_showing_failures_only = {
""",
"""		# 2.34 (Supernatural): witch_hunter is the CAPSTONE of the witch-hunter tree ("True Witch Hunter"); you should not
		# need it to begin hunting. The hunt opens on the first witch_hunting track threshold, or on the tree's root perk,
		# whose tooltip has always promised exactly this. The trait stays as a branch for the paths that grant it directly.
		OR = {
			has_trait = witch_hunter
			has_perk = antimage_perk
			has_trait_xp = { trait = supernatural_hunter track = witch_hunting value >= 25 }
		}
		# 2.35 (Supernatural) -- RETIRED for anyone who can ride the Supernatural Hunt instead.
		#
		# This decision was a button that fired one of two Witchcraft events at random. The Witch kind of the
		# Supernatural Hunt now does everything it did -- the same magic_ev3.63/.65 pair, the same 7% magic_ev8.3
		# roll -- and adds three weeks of actual hunting around them, against a witch who really lives in the
		# county rather than one conjured for the occasion. Two buttons for one act is duplication, and the worse
		# of the two should be the one to go.
		#
		# The clause is deliberately narrow: it hides the decision ONLY from a character who meets the activity's
		# own is_shown (supernatural_hunter, adult, landed or a landless adventurer). A witch_hunter or an
		# antimage who is none of those keeps the decision exactly as before, so nothing is taken away from
		# anybody -- it is moved.
		NOT = {
			AND = {
				has_trait = supernatural_hunter
				OR = {
					is_landed_or_landless_administrative = yes
					is_landless_adventurer = yes
				}
			}
		}
	}

	#is_valid_showing_failures_only = {
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
# 2.39 (WORK-ORDER-2.39 B14, entry 4): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's text
# and never matched upstream
E('common/traits/00_traits_magic.txt',
"""		possessed_genetic = 30
	}
	opposites = {
		witch_hunter
	}
}

""",
"""		possessed_genetic = 30
	}
	opposites = {
		# 2.34: `warlock` removed. archmage and warlock are both lifestyle capstones; with the exclusion whichever one
		# was bought second silently failed to add (Workshop report, Aug 2026). witch_hunter stays -- the capstone perks
		# now refuse to be picked by a hunter instead of failing silently.
		supernatural_hunter
		witch_hunter
	}
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
# 2.38e (Supernatural): one capstone. Each magic capstone perk also refuses a character who already walks another path;
# one who already holds two keeps both. These ride on the 2.34 entries below; apply_capstone_bridge lifts an older tree.
def _cap(cond, who):
    return ("\t\t# 2.38e (Supernatural): one capstone. " + who + " cannot take this one; a character who already holds two keeps both\n"
            "\t\tcustom_description = {\n\t\t\ttext = spn_capstone_another_path\n\t\t\t" + cond + "\n\t\t}\n")
CAP38E = {
    "archmage": _cap("NOR = { has_trait = warlock has_trait = true_witch }", "A Warlock or a True Witch"),
    "warlock": _cap("NOR = { is_true_mage = yes has_trait = true_witch }", "A Mage or a True Witch"),
    "true_witch": _cap("NOR = { is_true_mage = yes has_trait = warlock }", "A Mage or a Warlock"),
}
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
""" + GUARD + CAP38E["archmage"] + """	}
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
""" + GUARD + CAP38E["warlock"] + """	}

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
""" + GUARD + CAP38E["true_witch"] + """	}
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
# 2.39 (WORK-ORDER-2.39 B14, entry 16): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream
E('common/character_interactions/00_magic_interactions.txt',
"""		scope:actor = {
				is_adult = yes
				has_trait = witch_hunter
				#has_trait_xp = {
				#	trait = witch_hunter
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
# (character_memories_magic.txt declares `target0`; the third-person string referenced `victim`.)
# 2.39 (WORK-ORDER-2.39 B8): Russian too. The fix changes the scope inside [..], never a word of the translation, and
# Adrian's 2.38 file kept the same line.
LOC_FIX = [("localization/%s/event_localization/witch_ep4_l_%s.yml" % (l, l)) for l in
           ("english","french","german","korean","polish","russian","simp_chinese","spanish")]
# ---- 2.37 "The Six Hides" -- the ringing (WORK-ORDER-2.37 §18) ---------------------------------------------
# Seven of the eight magical_senses_perk tests in send_message_4_magic_sense_effect become spn_senses_magic_trigger (the
# legendary-mage branch's own test is left alone); magic_ev.4 gains the champion's text and Follow the ringing;
# magic_ev.44 gains Go after them.
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				location = {
					every_character_in_location = {
						limit = {
							has_perk = magical_senses_perk
""",
"""				location = {
					every_character_in_location = {
						limit = {
							spn_senses_magic_trigger = yes # 2.37 (Supernatural): a hide's champion hears magic too
""")
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				every_vassal = {
					limit = {
						has_perk = magical_senses_perk
""",
"""				every_vassal = {
					limit = {
						spn_senses_magic_trigger = yes # 2.37 (Supernatural): a hide's champion hears magic too
""")
E('common/scripted_effects/00_variety_magic_effects.txt',
"""					every_courtier_or_guest = {
						limit = {
							has_perk = magical_senses_perk
							NOT = { THIS = scope:magic_user }
""",
"""					every_courtier_or_guest = {
						limit = {
							spn_senses_magic_trigger = yes # 2.37 (Supernatural): a hide's champion hears magic too
							NOT = { THIS = scope:magic_user }
""")
E('common/scripted_effects/00_variety_magic_effects.txt',
"""					liege = {
						if = {
							limit = {
								has_perk = magical_senses_perk
""",
"""					liege = {
						if = {
							limit = {
								spn_senses_magic_trigger = yes # 2.37 (Supernatural): a hide's champion hears magic too
""")
E('common/scripted_effects/00_variety_magic_effects.txt',
"""						every_courtier_or_guest = {
							limit = {
								has_perk = magical_senses_perk
""",
"""						every_courtier_or_guest = {
							limit = {
								spn_senses_magic_trigger = yes # 2.37 (Supernatural): a hide's champion hears magic too
""")
E('common/scripted_effects/00_variety_magic_effects.txt',
"""					every_neighboring_realm_same_rank_owner = {
						limit = {
							has_perk = magical_senses_perk
""",
"""					every_neighboring_realm_same_rank_owner = {
						limit = {
							spn_senses_magic_trigger = yes # 2.37 (Supernatural): a hide's champion hears magic too
""")
E('common/scripted_effects/00_variety_magic_effects.txt',
"""						every_neighboring_realm_same_rank_owner = {
							limit = {
								has_perk = magical_senses_perk
""",
"""						every_neighboring_realm_same_rank_owner = {
							limit = {
								spn_senses_magic_trigger = yes # 2.37 (Supernatural): a hide's champion hears magic too
""")
E('events/ev1.txt',
"""#for magic sense
magic_ev.4 = {
	title = ev4.0.title
	desc = ev4.0.desc
	theme =  mental_health
""",
"""#for magic sense
magic_ev.4 = {
	# 2.37 (Supernatural): a hide's champion hears it as The Ringing.
	title = {
		first_valid = {
			triggered_desc = {
				trigger = { spn_is_champion_trigger = yes }
				desc = spn_ev4.0.title
			}
			desc = ev4.0.title
		}
	}
	desc = {
		first_valid = {
			triggered_desc = {
				trigger = { spn_is_champion_trigger = yes }
				desc = spn_ev4.0.desc
			}
			desc = ev4.0.desc
		}
	}
	theme =  mental_health
""")
E('events/ev1.txt',
"""			trigger_event = magic_ev2.53
		}
		
		ai_chance = {
			base = 10
		}
	}
""",
"""			trigger_event = magic_ev2.53
		}
		
		ai_chance = {
			base = 10
		}
	}
	# 2.37 (Supernatural): Follow the ringing. A champion goes after a caster who is none of his own (never his liege,
	# spouse, close family, friend, lover or courtier), once a year. Magic Tracking names the caster.
	option = {
		name = spn_ev4.0.ring
		trigger = {
			spn_is_champion_trigger = yes
			NOT = { has_character_flag = spn_hide_chased_ringing }
			exists = scope:magic_user
			NOT = { scope:magic_user = ROOT }
			NOT = { liege ?= scope:magic_user }
			scope:magic_user = {
				NOT = { has_strong_hook = ROOT }
				NOR = {
					is_spouse_of = ROOT
					is_close_family_of = ROOT
					has_relation_friend = ROOT
					has_relation_lover = ROOT
					is_courtier_of = ROOT
				}
			}
		}
		custom_tooltip = spn_ev4.0.ring.tt
		add_character_flag = { flag = spn_hide_chased_ringing years = 1 }
		trigger_event = magic_ev.44
		ai_chance = {
			base = 0
			modifier = {
				add = 40
				scope:magic_user = { has_relation_rival = ROOT }
			}
			modifier = {
				add = 40
				faith = { faith_hostility_level = { target = scope:magic_user.faith value >= faith_hostile_level } }
			}
			modifier = { add = 20 has_trait = brave }
			modifier = { add = 20 has_trait = vengeful }
		}
	}
""")
E('events/ev1.txt',
"""		clear_saved_scope = magic_user
		ai_chance = {
			base = 1
		}
	}
	option = {
		name = ev4b.0.c
""",
"""		clear_saved_scope = magic_user
		ai_chance = {
			base = 1
		}
	}
	# 2.37 (Supernatural): Go after them. Creature against caster; never a death (the hide's rule C5).
	option = {
		name = spn_ev4b.0.go
		trigger = {
			spn_is_champion_trigger = yes
			exists = scope:magic_user
			NOT = { scope:magic_user = ROOT }
		}
		custom_tooltip = spn_ev4b.0.go.tt
		save_scope_as = spn_ring_champion
		spn_clash_lean_tooltip_effect = { A = ROOT B = scope:magic_user FORM = no }
		spn_creature_clash_effect = {
			A = ROOT
			B = scope:magic_user
			THEN = spn_hide_ringing_after_effect
			FORM = no
		}
		clear_saved_scope = magic_user
		ai_chance = {
			base = 40
			modifier = { add = 20 has_trait = brave }
			modifier = { add = 20 has_trait = wrathful }
			modifier = { add = -30 has_trait = craven }
		}
	}
	option = {
		name = ev4b.0.c
""")


# =====================================================================================================================
# 2.38 "The Blue Rose" (WORK-ORDER-2.38 §15.1). Twenty-one entries. Each anchor matched once in the mod's tree and in
# Witchcraft 2.18 when the order was written; a miss prints ANCHOR NOT FOUND and writes nothing.
# =====================================================================================================================

# 1 -- Summon Demon: Zecchia answers sometimes (§11.2).
E('events/ev1.txt',
"""			random_list = {
				24 = {
					#minor demon
""",
"""			random_list = {
				8 = {
					# 2.38 (Supernatural): Zecchia, a thief who answers the summoning (WORK-ORDER-2.38 §11.2)
					trigger = {
						has_character_flag = no_complications
						NOT = { exists = global_var:spn_zecchia_busy }
					}
					spn_ms_zecchia_demon_effect = yes
				}
				24 = {
					#minor demon
""")

# 2 -- The Black Grimoire: a name in the margin (§11.2).
E('common/decisions/magic_dec.txt',
"""			else = {
				random_list = {
					80 = {
						trigger = {
							NAND = {
""",
"""			else = {
				random_list = {
					8 = {
						# 2.38 (Supernatural): A Name in the Margin (WORK-ORDER-2.38 §11.2)
						trigger = { NOT = { has_character_flag = spn_knows_zecchia } }
						trigger_event = spn_zecchia.0005
					}
					80 = {
						trigger = {
							NAND = {
""")

# 3 -- The Mage Summit's end: the Order's intents pay (§5.21).
E('common/activities/activity_types/mages_summit.txt',
"""	on_complete = {
""",
"""	on_complete = {
		spn_order_summit_complete_effect = yes # 2.38 (Supernatural): the Order at the Summit (WORK-ORDER-2.38 §5.21)
""")

# 4 -- The council's vote: Temple Magi first, standing, and a member who aspires (§5.9, §5.16).
E('common/script_values/02_magic_values.txt',
"""			any_character_artifact = {
				has_variable = magic1
			}
		}
		add = 50
	}
	add = diplomacy
}
archmage_candidates_score_with_personality_value = {""",
"""			any_character_artifact = {
				has_variable = magic1
			}
		}
		add = 50
	}
	# 2.38 (Supernatural): the Order behind the masks (WORK-ORDER-2.38 §5.9, §5.16)
	if = {
		limit = { spn_is_temple_magus_trigger = yes }
		add = 50
	}
	if = {
		limit = {
			spn_is_order_member_trigger = yes
			exists = var:spn_order_standing
		}
		add = var:spn_order_standing
	}
	if = {
		limit = {
			spn_is_order_member_trigger = yes
			has_character_flag = spn_order_aspires_chair
		}
		add = 20
	}
	add = diplomacy
}
archmage_candidates_score_with_personality_value = {""")

# 5 -- Command Minion: a man bound to the book commands demons (§12.7).
E('common/character_interactions/00_magic_interactions.txt',
"""			OR = {
				AND = {
					has_relation_mminion = scope:recipient
""",
"""			OR = {
				AND = { # 2.38 (Supernatural): bound to the Vade Maecum Infernal (WORK-ORDER-2.38 §12.7)
					has_trait = spn_vade_bound
					scope:recipient = { is_a_demon_trigger = yes }
				}
				AND = {
					has_relation_mminion = scope:recipient
""")

# 6 -- Magic Triangulation: seek the pages of the book (§12.4).
E('events/ev4.txt',
"""		ai_chance = {
			base = 1
		}
	}
}
#new magic triangulation - places
""",
"""		ai_chance = {
			base = 1
		}
	}
	# 2.38 (Supernatural): the Vade Maecum Infernal (WORK-ORDER-2.38 §12.4)
	option = {
		name = spn_ev4.82.pages
		trigger = {
			spn_vade_on_trigger = yes
			any_artifact = {
				OR = {
					has_variable = spn_vade_page
					has_variable = spn_vade_book
				}
				artifact_owner ?= { NOT = { this = root } }
				NOT = { has_variable = spn_page_guarded }
			}
		}
		trigger_event = spn_vade.0200
		ai_chance = {
			base = 1
		}
	}
}
#new magic triangulation - places
""")

# 7 -- Command Minion's hook test: the bound need none (§12.7).
E('common/character_interactions/00_magic_interactions.txt',
"""				text = has_ready_hook_custom
				OR = {
""",
"""				text = has_ready_hook_custom
				OR = {
					has_trait = spn_vade_bound # 2.38 (Supernatural): WORK-ORDER-2.38 §12.7
""")

# 8 -- Command Minion: a greater demon too, for the bound (§12.7).
E('common/character_interactions/00_magic_interactions.txt',
"""							var:magic_manipulator = scope:actor
						}
					}
				}
			}
		}
		scope:recipient = {
			NOT = {
				has_trait = demon2
			}
		}
""",
"""							var:magic_manipulator = scope:actor
						}
					}
				}
			}
		}
		scope:recipient = {
			trigger_if = { # 2.38 (Supernatural): the bound master commands greater demons too (WORK-ORDER-2.38 §12.7)
				limit = { scope:actor = { has_trait = spn_vade_bound } }
				always = yes
			}
			trigger_else = {
				NOT = {
					has_trait = demon2
				}
			}
		}
""")

# 9, 10 -- The Mage Summit: the Order's two intents (§5.21).
E('common/activities/activity_types/mages_summit.txt',
"""	host_intents = {
		intents = { sharing_knowledge_intent political_matters_intent show_superiority_intent }
""",
"""	host_intents = {
		intents = { sharing_knowledge_intent political_matters_intent show_superiority_intent spn_meet_in_the_masks_intent spn_speak_for_the_order_intent } # 2.38 (Supernatural)
""")
E('common/activities/activity_types/mages_summit.txt',
"""	guest_intents = {
		intents = { sharing_knowledge_intent political_matters_intent show_superiority_intent }
""",
"""	guest_intents = {
		intents = { sharing_knowledge_intent political_matters_intent show_superiority_intent spn_meet_in_the_masks_intent spn_speak_for_the_order_intent } # 2.38 (Supernatural)
""")

# 11, 12 -- The Grand Rite: Bring the Coven to the Order (§5.15).
E('common/activities/activity_types/witch_ritual.txt',
"""	host_intents = {
		intents = { worship_devil_intent seek_for_power_intent choose_grandmaster_intent coven_policy_intent }
""",
"""	host_intents = {
		intents = { worship_devil_intent seek_for_power_intent choose_grandmaster_intent coven_policy_intent spn_bring_coven_to_order_intent } # 2.38 (Supernatural)
""")
E('common/activities/activity_types/witch_ritual.txt',
"""	on_complete = {
""",
"""	on_complete = {
		spn_coven_rite_complete_effect = yes # 2.38 (Supernatural): WORK-ORDER-2.38 §5.15
""")

# 15 (before 13: their anchors touch) -- Against the Witch: the war takes relics and pages too (§10).
E('common/casus_belli_types/01_magic_cb.txt',
"""				}
			}
			every_character_artifact = {
				limit = {
					OR = {
						has_variable = magic1
						has_variable = singularity
""",
"""				}
			}
			every_character_artifact = {
				limit = {
					OR = {
						has_variable = magic1
						has_variable = singularity
						has_variable = spn_relic # 2.38 (Supernatural): WORK-ORDER-2.38 §10
						has_variable = spn_vade_page
""")

# 13 -- The witch war breaks a coven: its panel ends with it (§7.3).
E('common/casus_belli_types/01_magic_cb.txt',
"""						remove_house_modifier = witch_coven
""",
"""						remove_house_modifier = witch_coven
						spn_coven_ended_effect = yes # 2.38 (Supernatural): WORK-ORDER-2.38 §7.3
""")

# 14 -- A demon's conquest takes relics and pages too (§10).
E('common/casus_belli_types/01_magic_cb.txt',
"""		#Clean-up adventurer things.
		#scope:attacker = { clean_scandinavian_adventurer_effect = yes }
		scope:defender = {
			every_character_artifact = {
				limit = {
					OR = {
						has_variable = magic1
						has_variable = singularity
""",
"""		#Clean-up adventurer things.
		#scope:attacker = { clean_scandinavian_adventurer_effect = yes }
		scope:defender = {
			every_character_artifact = {
				limit = {
					OR = {
						has_variable = magic1
						has_variable = singularity
						has_variable = spn_relic # 2.38 (Supernatural): WORK-ORDER-2.38 §10
						has_variable = spn_vade_page
""")

# 16 -- Power saturation: the bound master and the Fors Factorum cast without price (§12.7, §5.20).
E('common/scripted_triggers/magic_triggers.txt',
"""can_spend_standard_ps_trigger = {
	OR = {
""",
"""can_spend_standard_ps_trigger = {
	OR = {
		spn_casts_without_price_trigger = yes # 2.38 (Supernatural): WORK-ORDER-2.38 §5.20, §12.7
""")

# 17
E('common/scripted_triggers/magic_triggers.txt',
"""can_spend_huge_ps_trigger = {
	has_trait = archmage
	has_trait_xp = {
		trait = archmage
		track = power_saturation
		value > 19
	}
}""",
"""can_spend_huge_ps_trigger = {
	OR = {
		spn_casts_without_price_trigger = yes # 2.38 (Supernatural): WORK-ORDER-2.38 §5.20, §12.7
		AND = {
			has_trait = archmage
			has_trait_xp = {
				trait = archmage
				track = power_saturation
				value > 19
			}
		}
	}
}""")

# 18, 19, 20 -- the three spends: nothing is taken from one who casts without price.
for _name in ("spend_standard_ps_effect", "spend_huge_ps_effect", "spend_minor_ps_effect"):
    E('common/scripted_effects/00_variety_magic_effects.txt',
"""%s = {
	if = {
""" % _name,
"""%s = {
	if = { # 2.38 (Supernatural): WORK-ORDER-2.38 §5.20, §12.7
		limit = { spn_casts_without_price_trigger = yes }
		custom_tooltip = spn_vade_free_tt
	}
	else_if = {
""" % _name)

# 21 -- The Mage Summit begins: The Temple Sends You (§5.21).
E('common/activities/activity_types/mages_summit.txt',
"""	on_start = {
		#space for invitation event
""",
"""	on_start = {
		#space for invitation event
		spn_order_summit_started_effect = yes # 2.38 (Supernatural): WORK-ORDER-2.38 §5.21
""")

# 22 -- 2.38a: the council button before any council exists says how one forms (Thomas, 9 Oct: a Mage outside any society
# read "can only be formed by a Grand Magus" and did not know what to do). Witchcraft 2.18 has "an archmage" in lower
# case on this line, so a 2.18 merge hand-merges this one.
# 2.39 (WORK-ORDER-2.39 B14, entry 48): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream. It no longer needs the hand merge the note above expects
E('localization/english/event_localization/witch_ep9_l_english.yml',
""" mc_disabled_tooltip:0 "#N High Council can only be formed by an archmage.#!"
 mc_full_name:0 "High Council of Mages"
""",
""" mc_disabled_tooltip:0 "#N The Gnostic Council has not met yet. It sits once a Grand Magus is chosen.#!"
 mc_full_name:0 "Gnostic Council"
""")

# =====================================================================================================================
# 2.38b "The Conclave" (DESIGN-2.38b §3): the Gnostic Council belongs to the Order. With the Order rule On the Mage Summit
# no longer makes a Grand Magus, and only members of the Order sit on the council. With it Off, Witchcraft's own rules.
# =====================================================================================================================

# 23 -- The Summit opens no election while the Order chooses the chair.
E('common/activities/activity_types/mages_summit.txt',
"""				NOT = {
					any_activity = {
						has_variable = elections
					}
				}
			}
			scope:activity = {
				set_variable = elections
			}""",
"""				NOT = {
					any_activity = {
						has_variable = elections
					}
				}
				spn_order_on_trigger = no # 2.38b (Supernatural): the Order elects the Grand Magus (DESIGN-2.38b §3)
			}
			scope:activity = {
				set_variable = elections
			}""")

# 24 -- No speaker proposes himself for the chair.
E('events/ev7.txt',
"""		trigger = {
			has_ms_show_superiority_intent_trigger = yes
			has_trait = archmage
			NOR = {""",
"""		trigger = {
			has_ms_show_superiority_intent_trigger = yes
			has_trait = archmage
			spn_order_on_trigger = no # 2.38b (Supernatural): the Order elects the Grand Magus (DESIGN-2.38b §3)
			NOR = {""")

# 25 -- And if one already had (an old save mid-Summit), the vote does not seat him.
E('common/scripted_effects/00_variety_magic_effects.txt',
"""					else_if = {
						limit = {
							scope:speaker0 = {
								has_character_flag = ms_want_be_archmage_flag
							}
						}""",
"""					else_if = {
						limit = {
							scope:speaker0 = {
								has_character_flag = ms_want_be_archmage_flag
							}
							spn_order_on_trigger = no # 2.38b (Supernatural): the Order elects the Grand Magus (DESIGN-2.38b §3)
						}""")

# 26 -- Invite to the Gnostic Council: members of the Order only.
E('common/character_interactions/00_magic_interactions.txt',
"""	is_valid_showing_failures_only = {
		scope:recipient = {
			custom_description = {
				text = is_mc_member
				NOT = { has_variable = mc_member_var }
			}""",
"""	is_valid_showing_failures_only = {
		scope:recipient = {
			spn_order_council_member_ok_trigger = yes # 2.38b (Supernatural): the council is the Order's (DESIGN-2.38b §3)
			custom_description = {
				text = is_mc_member
				NOT = { has_variable = mc_member_var }
			}""")

# 27 -- Asking for a seat: members of the Order only.
# 2.39 (WORK-ORDER-2.39 B14, entry 53): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream; the 2.31c species gate is in `new` now (L15)
E('common/character_interactions/00_magic_interactions.txt',
"""		scope:actor = {
			custom_description = {
				text = is_incapable_custom
				NOT = { has_trait = incapable }
			}
		}
	}
	icon = icon_mage
""",
"""		scope:actor = {
			custom_description = {
				text = is_incapable_custom
				NOT = { has_trait = incapable }
			}
			spn_order_council_member_ok_trigger = yes # 2.38b (Supernatural): the council is the Order's (DESIGN-2.38b §3)
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_mage
""")

# 28 -- The yearly seat offer: members of the Order only.
E('events/ev10.txt',
"""	lower_right_portrait = global_var:current_archmage_global
	trigger = {
		is_alive = yes
		is_imprisoned = no
		exists = global_var:current_archmage_global""",
"""	lower_right_portrait = global_var:current_archmage_global
	trigger = {
		is_alive = yes
		is_imprisoned = no
		spn_order_council_member_ok_trigger = yes # 2.38b (Supernatural): the council is the Order's (DESIGN-2.38b §3)
		exists = global_var:current_archmage_global""")

# 29 -- The council's HUD buttons: with the Order's council (global spn_order_council_ours), members only. Before a
# council: the placeholder.
E('gui/window_high_council.gui',
"""	visible = "[And( Not( GetGlobalVariable( 'mc_has_been_formed' ).IsSet ), Or(GetPlayer.HasTrait( GetTrait( 'archmage' ) ), GetPlayer.HasTrait( GetTrait( 'true_witch' ) ) ) )]\"""",
"""	visible = "[And( Not( GetGlobalVariable( 'mc_has_been_formed' ).IsSet ), Or( And( Not( GetGlobalVariable( 'spn_order_council_ours' ).IsSet ), Or(GetPlayer.HasTrait( GetTrait( 'archmage' ) ), GetPlayer.HasTrait( GetTrait( 'true_witch' ) ) ) ), GetPlayer.MakeScope.Var( 'spn_order_member' ).IsSet ) )]\"""")

# 30 -- The same for the council's own button once it sits (a revealed council stays visible to all, Witchcraft's rule).
E('gui/window_high_council.gui',
"""	visible = "[Or( And( GetGlobalVariable( 'mc_has_been_formed' ).IsSet, Or(GetPlayer.HasTrait( GetTrait( 'archmage' ) ), GetPlayer.HasTrait( GetTrait( 'true_witch' ) ) ) ), GetGlobalVariable( 'mc_revealed' ).IsSet )]\"""",
"""	visible = "[Or( And( GetGlobalVariable( 'mc_has_been_formed' ).IsSet, Or( And( Not( GetGlobalVariable( 'spn_order_council_ours' ).IsSet ), Or(GetPlayer.HasTrait( GetTrait( 'archmage' ) ), GetPlayer.HasTrait( GetTrait( 'true_witch' ) ) ) ), GetPlayer.MakeScope.Var( 'spn_order_member' ).IsSet ) ), GetGlobalVariable( 'mc_revealed' ).IsSet )]\"""")

# 31 -- 2.38b: the temple helps a member's Magical Research (DESIGN-2.38b §7b): one breakthrough fewer, once.
E('common/scripted_effects/00_magical_research_effects.txt',
"""mr_resolve_research_effect = {
	change_variable = {
		name = mr_required_breakthroughs
		multiply = 25
	}""",
"""mr_resolve_research_effect = {
	if = { # 2.38b (Supernatural): his temple helped (spn_order_research_help), DESIGN-2.38b §7b
		limit = {
			has_character_flag = spn_order_research_help
			exists = var:mr_required_breakthroughs
			var:mr_required_breakthroughs > 1
		}
		change_variable = {
			name = mr_required_breakthroughs
			add = -1
		}
		remove_character_flag = spn_order_research_help
	}
	change_variable = {
		name = mr_required_breakthroughs
		multiply = 25
	}""")


# =====================================================================================================================
# 2.38c: Bound to the Book, completed (Thomas, 9 Oct: "make sure that registers ... that the cost would automatically be
# fulfilled"). The audit found three costs outside Witchcraft's five chokepoints, and three places a demon could still
# refuse a Bound master. spn_casts_without_price_trigger = Bound or Fors Factorum; the demon lines use the trait itself.
# =====================================================================================================================

# 32 -- The Mage Duel's drain after each round: free for one who casts without price.
E('common/scripted_effects/00_mage_duel_effects.txt',
"""remove_mana_after_md_effect = {
	if = {
		limit = {
			OR = {
				has_character_flag = md_winner
				has_character_flag = md_loser
				has_character_flag = md_not_concluded
			}
		}
		if = {
			limit = {
				has_trait = archmage
			}""",
"""remove_mana_after_md_effect = {
	if = {
		limit = {
			OR = {
				has_character_flag = md_winner
				has_character_flag = md_loser
				has_character_flag = md_not_concluded
			}
		}
		if = { # 2.38c (Supernatural): Bound to the Book, magic costs nothing
			limit = { spn_casts_without_price_trigger = yes }
			custom_tooltip = spn_vade_free_tt
		}
		else_if = {
			limit = {
				has_trait = archmage
			}""")

# 33 -- Hecate, "use your power": through the chokepoints (the cost is the same, 20).
E('events/ev4.txt',
"""		name = ev4.86.0.d
		trigger = {
			has_trait = archmage
			has_trait_xp = {
				trait = archmage
				track = power_saturation
				value > 19
			}
		}
		custom_tooltip = ev4.86.0.d_ct
		add_trait_xp = {
			trait = archmage
			track = power_saturation
			value = -20
		}""",
"""		name = ev4.86.0.d
		trigger = {
			has_trait = archmage
			can_spend_huge_ps_trigger = yes # 2.38c (Supernatural): through the chokepoint (Bound casts free)
		}
		custom_tooltip = ev4.86.0.d_ct
		spend_huge_ps_effect = yes # 2.38c (Supernatural): the same 20, unless Bound""")

# 34 -- The Grand Spell cast at once: free for one who casts without price.
E('events/ev9.txt',
"""		name = ev9.92.0.c
		trigger = {
			is_the_choosen_one_trigger = yes
			custom_description = {
				text = power_needed_custom2
				has_trait_xp = {
					trait = archmage
					track = power_saturation
					value > 99
				}
			}""",
"""		name = ev9.92.0.c
		trigger = {
			is_the_choosen_one_trigger = yes
			custom_description = {
				text = power_needed_custom2
				OR = {
					spn_casts_without_price_trigger = yes # 2.38c (Supernatural): Bound casts free
					has_trait_xp = {
						trait = archmage
						track = power_saturation
						value > 99
					}
				}
			}""")
E('events/ev9.txt',
"""			is_the_choosen_one_trigger = yes
		}
		add_trait_xp = {
			trait = archmage
			track = power_saturation
			value = -100
		}

		custom_tooltip = ev9.92.0.c_ct""",
"""			is_the_choosen_one_trigger = yes
		}
		if = { # 2.38c (Supernatural): Bound casts free
			limit = { spn_casts_without_price_trigger = no }
			add_trait_xp = {
				trait = archmage
				track = power_saturation
				value = -100
			}
		}

		custom_tooltip = ev9.92.0.c_ct""")

# 35 -- Summon Demon: a demon answers a Bound summoner as it answers the Scepter (always, no complications).
E('events/ev1.txt',
"""		name = ev12.0.a
		trigger = {
			NOR = {
				any_equipped_character_artifact = {	has_variable = magic_scepter	}""",
"""		name = ev12.0.a
		trigger = {
			NOR = {
				has_trait = spn_vade_bound # 2.38c (Supernatural): demons obey the Bound
				any_equipped_character_artifact = {	has_variable = magic_scepter	}""")
E('events/ev1.txt',
"""		name = ev12.0.c
		trigger = {
			OR = {
				any_equipped_character_artifact = {	has_variable = magic_scepter	}""",
"""		name = ev12.0.c
		trigger = {
			OR = {
				has_trait = spn_vade_bound # 2.38c (Supernatural): demons obey the Bound
				any_equipped_character_artifact = {	has_variable = magic_scepter	}""")

# 36 -- Belial does not turn on a Bound summoner.
E('events/ev1.txt',
"""						has_game_rule = no_demonic_aggression_mode
						has_relation_best_friend = scope:belial""",
"""						has_game_rule = no_demonic_aggression_mode
						has_trait = spn_vade_bound # 2.38c (Supernatural): demons obey the Bound
						has_relation_best_friend = scope:belial""")

# 37 -- Command a Minion: an AI demon always obeys a Bound master.
E('common/character_interactions/00_magic_interactions.txt',
"""	#ai_frequency = 24
	#ai_will_do = {
	#	base = 50
	#}
	auto_accept = no""",
"""	#ai_frequency = 24
	#ai_will_do = {
	#	base = 50
	#}
	auto_accept = { # 2.38c (Supernatural): demons obey the Bound
		scope:actor = { has_trait = spn_vade_bound }
		scope:recipient = {
			is_ai = yes
			is_a_demon_trigger = yes
		}
	}""")


# =====================================================================================================================
# 2.38c: Witchcraft's own bugs, fixed on Thomas's call (9 Oct: "we're only gonna fix the witchcraft part. Base game will
# fix itself"). Each from his 9 Oct error.log; causes in claude/session74. Numbers 38-45.
# =====================================================================================================================
# 1 Shadowstep
E('common/character_interactions/00_magic_interactions.txt',
"""				else = {
					release_from_prison = yes
					scope:actor.imprisoner = {
						if = {
							limit = {
								OR = {
									has_revoke_title_reason = scope:actor
									has_banish_reason = scope:actor
									has_execute_reason = scope:actor
								}
							}
							add_opinion = {
								target = scope:actor
								modifier = escaped_from_prison_crime
							}
						}
						else = {
							add_opinion = {
								target = scope:actor
								modifier = escaped_from_prison_opinion
							}
						}
						save_scope_as = imprisoner
					}
					#custom_tooltip = escape_from_prison_decision_effect_tooltip	#to removing?
					trigger_event = {
						on_action = escape_from_prison
					}
				}
""",
"""				else = {
					# 2.38 (Supernatural): the gaoler is saved while the caster is still his prisoner, then vanilla's escape
					# success event (prison.9001) runs escape_from_prison_effect: opinion, memory, release, and a message to a
					# player gaoler. The old block released first and then fired the escape ATTEMPT on_action, which found no
					# imprisoner and could even roll a failure after the release.
					if = {
						limit = { exists = imprisoner }
						imprisoner = { save_scope_as = imprisoner }
						show_as_tooltip = { release_from_prison = yes }
						trigger_event = prison.9001
					}
					else = {
						release_from_prison = yes
					}
				}
""")

# 2 Witch hunter secret (two blocks)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				after_creation = {
					add_secret = {
						type = secret_witch_hunter
					}
					add_gold = 100
""",
"""				after_creation = {
					# 2.38 (Supernatural): no secret_witch_hunter here. The template gives supernatural_hunter, which the secret's
					# is_valid forbids, so the secret was invalid the moment it was made.
					add_gold = 100
""")
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				after_creation = {
					add_secret = {
						type = secret_witch_hunter
					}
					add_gold = 50
""",
"""				after_creation = {
					# 2.38 (Supernatural): no secret_witch_hunter here (see the landed branch above).
					add_gold = 50
""")

# 4 magic_ev10.5
E('events/ev10.txt',
"""			else = {
				scope:temp_spell_host = {
					change_first_name = var:my_custom_spell_name
				}
			}
			set_variable = {
				name = my_custom_spell
				value = scope:temp_spell_host
			}
""",
"""			# 2.38 (Supernatural): an unreachable else that passed var:my_custom_spell_name to change_first_name as a loc key
			# is removed. The typed name reaches the spell through copy_localized_text in the first branch.
			set_variable = {
				name = my_custom_spell
				value = scope:temp_spell_host
			}
""")

# 5 Demand Submission
# 2.39 (WORK-ORDER-2.39 B14, entry 70): re-anchored on Witchcraft 2.18's own text; the old anchor was the 1.20
# port's output, which the documented order (generator, then port) does not have yet. This entry now makes the
# port's change too
E('common/character_interactions/00_magic_interactions.txt',
"""					if = {
						limit = {
							NOT = {	faith = scope:actor.faith	}
						}
						set_character_faith_with_conversion = scope:actor.faith
					}
""",
"""					if = {
						limit = {
							NOT = {	rite = scope:actor.rite	}	# CK3 1.20: the convert follows the actor's Rite, not only the Faith
							NOT = { faith.religious_head ?= this }
						}
						# 2.38 (Supernatural): vanilla's forced-conversion effect (the one ask_for_conversion uses). The
						# _with_conversion effect applies the convert-UI rules (adult, piety cost, rite knowledge) and refused
						# most recipients.
						convert_to_rite_with_consequences_effect = { RITE = scope:actor.rite }
					}
""")

# 7a no_soul
# 2.39 (WORK-ORDER-2.39 B14, entry 71): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream. Witchcraft 2.18 made the same fix itself; only the mod's comment on the line
# remains
E('common/on_action/yearly2_on_actions.txt',
"""on_action_death_cyro_conclusion = {
	trigger = {
		has_character_modifier = no_soul_modifier
		has_variable = my_soul_owner
""",
"""on_action_death_cyro_conclusion = {
	trigger = {
		has_character_modifier = no_soul_modifier # 2.38 (Supernatural): was has_character_flag = no_soul, which nothing sets
		has_variable = my_soul_owner
""")

# 7b mage_defeated_list
E('events/ev9.txt',
"""		has_variable = mage_defeated_list
		any_in_list = {
			list = mage_defeated_list
""",
"""		has_variable = mage_defeated_list
		any_in_list = {
			variable = mage_defeated_list # 2.38 (Supernatural): a variable list (add_to_variable_list), not a saved list
""")


# 3 can_raid: the Black Fortress (mage_tower_021, flag wc_evil_fortress_flag) exists only in Witchcraft 2.171+; this mod's
# buildings file predates it, so the branch was always false and logged at load. Behaviour unchanged. DROP THIS ENTRY when
# the buildings file is merged from 2.18 (session 67 §8).
E('common/scripted_rules/00_rules_magic_overwritten.txt',
"""can_raid = {
	OR = {
		can_raid_trigger = yes
		AND = {
			is_landed = yes
			any_directly_owned_province = {
				has_building_with_flag = wc_evil_fortress_flag
			}
		}
	}
}""",
"""can_raid = {
	# 2.38 (Supernatural): the Black Fortress branch (has_building_with_flag = wc_evil_fortress_flag) is off until the
	# buildings file is merged from Witchcraft 2.171+; mage_tower_021 carries the flag there. Drop this entry at that merge.
	can_raid_trigger = yes
}""")

# 46 -- The cyrograph's payout on death (live since entry 44): its demon1 branch sat inside a demon2-only limit.
E('common/on_action/yearly2_on_actions.txt',
"""			else = {
				var:my_soul_owner = {
					if = {
						limit = {
							has_trait = demon2
							has_trait_xp = {
								trait = demon2
								track = hell_powers
								value < 100
							}
						}
						send_interface_toast = {
							title = cyro_completed_toast""",
"""			else = {
				var:my_soul_owner = {
					if = {
						limit = {
							OR = { # 2.38 (Supernatural): a demon1 owner takes the perk point below, as ev8.19 gives it
								AND = {
									has_trait = demon2
									has_trait_xp = {
										trait = demon2
										track = hell_powers
										value < 100
									}
								}
								has_trait = demon1
							}
						}
						send_interface_toast = {
							title = cyro_completed_toast""")

# =====================================================================================================================
# 2.38e (Supernatural): one capstone, the AI's paths and necromancy, the magical artifacts' finders, and the Claws.
# The capstone guards themselves ride on the three 2.34 capstone entries above (CAP38E; apply_capstone_bridge lifts a tree
# patched by 2.34-2.38d), so these continue at 50.
# =====================================================================================================================

# 50 -- Teach sorcery (AI): a Warlock or a True Witch is not made a Mage.
E('events/ev7.txt',
"""magic_ev7.130 = {
	hidden = yes
	trigger = {
		is_ai = yes
		NOR = {
			has_trait = incapable
			has_trait = archmage
		}
	}
	immediate = {
		turn_into_mage_effect = yes
""",
"""magic_ev7.130 = {
	hidden = yes
	trigger = {
		is_ai = yes
		NOR = {
			has_trait = incapable
			has_trait = archmage
			has_trait = warlock # 2.38e (Supernatural): one capstone; a Warlock or a True Witch is not made a Mage
			has_trait = true_witch
		}
	}
	immediate = {
		turn_into_mage_effect = yes
""")

# 51 -- Teach sorcery, step by step (AI): the same; the chain ends there.
# 2.39 (WORK-ORDER-2.39 B14, entry 76): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream
E('events/ev7.txt',
"""magic_ev7.131 = {
	hidden = yes
	trigger = {
		is_ai = yes
		NOR = {
			has_trait = incapable
			has_trait = archmage
			has_focus = magic_focus
		}
""",
"""magic_ev7.131 = {
	hidden = yes
	trigger = {
		is_ai = yes
		NOR = {
			has_trait = incapable
			has_trait = archmage
			has_focus = arcane_focus
			has_trait = warlock # 2.38e (Supernatural): one capstone; the last step is the Mage perk
			has_trait = true_witch
		}
""")

# 52 -- The Catalyst: an AI finder who is a Warlock or a True Witch is not also made a Mage.
E('events/ev1.txt',
"""		if = {
			limit = {
				is_ai = yes
				is_adult = yes
				NOT = {
					has_game_rule = min_num_of_mages
				}
			}
			give_witch_secret_or_trait_effect2 = yes
			turn_into_mage_effect = yes
""",
"""		if = {
			limit = {
				is_ai = yes
				is_adult = yes
				NOT = {
					has_game_rule = min_num_of_mages
				}
				NOR = { has_trait = warlock has_trait = true_witch } # 2.38e (Supernatural): one capstone
			}
			give_witch_secret_or_trait_effect2 = yes
			turn_into_mage_effect = yes
""")

# 53 -- create_mage_effect (an AI ruler becomes a Mage): pick one who walks no other path.
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				highest_held_title_tier > 2
				exists = dynasty		
				dynasty={
					NOT={
						has_variable=ev1used
					}
				}
				in_diplomatic_range = scope:hplayer1
				#capital_province = {
				#	OR = {
				#		geographical_region = world_asia_minor
				#		geographical_region = world_europe
				#	}	
				#}
				is_ai = yes
				NOT = { has_trait = zealous }
				NOT = { has_trait = source }
""",
"""				highest_held_title_tier > 2
				exists = dynasty		
				dynasty={
					NOT={
						has_variable=ev1used
					}
				}
				in_diplomatic_range = scope:hplayer1
				#capital_province = {
				#	OR = {
				#		geographical_region = world_asia_minor
				#		geographical_region = world_europe
				#	}	
				#}
				is_ai = yes
				NOT = { has_trait = zealous }
				NOT = { has_trait = source }
				NOR = { has_trait = warlock has_trait = true_witch } # 2.38e (Supernatural): one capstone
""")

# 54 -- create_true_witch_effect (an AI ruler becomes a True Witch): not a Mage or a Warlock.
E('common/scripted_effects/00_variety_magic_effects.txt',
"""					NOR = {
						any_character_artifact = { has_variable = magic1 }
						has_trait = zealous
						has_trait = source
						#has_trait = source2
						#has_trait = source3
						#has_trait = source4
						has_trait = honest
						has_trait = true_witch
					}
""",
"""					NOR = {
						any_character_artifact = { has_variable = magic1 }
						has_trait = zealous
						has_trait = source
						#has_trait = source2
						#has_trait = source3
						#has_trait = source4
						has_trait = honest
						has_trait = true_witch
						is_true_mage = yes # 2.38e (Supernatural): one capstone
						has_trait = warlock
					}
""")

# 55 -- create_extra_coven (the house head takes the True Witch perk): not a Mage or a Warlock.
E('common/scripted_effects/00_variety_magic_effects.txt',
"""create_extra_coven = {
	random_ruler = {
		limit = {
			is_landed_or_landless_administrative = yes
			is_ai = yes
			is_adult = yes
""",
"""create_extra_coven = {
	random_ruler = {
		limit = {
			is_landed_or_landless_administrative = yes
			is_ai = yes
			is_adult = yes
			NOR = { is_true_mage = yes has_trait = warlock } # 2.38e (Supernatural): one capstone; this head is made a True Witch
""")

# 56 -- Enchanted Blood (witchcraft_legacy_5): a Warlock or a True Witch of the house is not made a Mage.
# 2.39 (WORK-ORDER-2.39 B14, entry 81): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream; the 2.31c species gate is in `new` now (L15)
E('common/dynasty_perks/01_magic.txt',
"""					NOR = {
						has_trait = archmage
						has_trait = witch_hunter
					}
""",
"""					# 2.31c -- every_dynasty_member, so this walks the whole house. Gated here rather than
					# inside turn_into_mage_effect, which the summoning rituals call on characters they
					# create themselves and which must keep working.
					spn_is_valid_supernatural_target = yes
					NOR = {
						has_trait = archmage
						has_trait = supernatural_hunter
						has_trait = warlock # 2.38e (Supernatural): one capstone
						has_trait = true_witch
					}
""")

# 57 -- The magic legend's completion: its owner is made a Mage only if he walks no other path.
# 2.39 (WORK-ORDER-2.39 B14, entry 82): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream; the 2.31c species gate is in `new` now (L15)
E('common/legends/legend_types/01_magic_legends.txt',
"""					turn_into_mage_effect = yes
""",
"""					# 2.31c -- same reasoning as the witchcraft legacy: gate the caller, not the effect.
					if = {
						limit = {
							spn_is_valid_supernatural_target = yes
							NOR = { has_trait = warlock has_trait = true_witch } # 2.38e (Supernatural): one capstone
						}
						turn_into_mage_effect = yes
					}
""")

# 58 -- Travel to the Stars, the notes: a Warlock or a True Witch is not made a Mage.
E('events/ev11.txt',
"""		if = {
			limit = {
				is_true_mage = no
			}
			hidden_effect = {
				if = {
					limit = {
						has_trait = archmage
					}
					remove_trait = archmage
				}
			}
			turn_into_mage_effect = yes
		}
		else = {
""",
"""		if = {
			limit = {
				is_true_mage = no
				NOR = { has_trait = warlock has_trait = true_witch } # 2.38e (Supernatural): one capstone
			}
			hidden_effect = {
				if = {
					limit = {
						has_trait = archmage
					}
					remove_trait = archmage
				}
			}
			turn_into_mage_effect = yes
		}
		else_if = {
			# 2.38e (Supernatural): a Warlock or a True Witch reads the notes and learns the teleportation spell only (a false
			# Mage among them too: the tracks below belong to a true Mage)
			limit = { is_true_mage = no }
			if = {
				limit = {
					NOT = {
						has_character_flag = teleportation_spell_flag
					}
				}
				custom_tooltip = gain_magic_teleportation_spell_txt_dot
				hidden_effect = {
					add_character_flag = teleportation_spell_flag
				}
			}
		}
		else = {
""")

# 59 -- Magical Research, choose the topic (magic_ev11.34) option a.
E('events/ev11.txt',
"""				value = var:drawn_option1
			}
			mr_launch_effect = yes
		}
	}
""",
"""				value = var:drawn_option1
			}
			mr_launch_effect = yes
		}
		ai_chance = { # 2.38e (Supernatural): the AI takes up necromancy mostly when its nature fits
			base = 100
			modifier = {
				factor = 0.1
				OR = {
					AND = {
						var:drawn_option1 ?= flag:necromancy
						NOR = { has_trait = necromancer has_trait = warlock } # mr_necromancy_effect gives them no trait
					}
					var:drawn_option1 ?= flag:lich # mr_lich_effect adds necromancer
				}
				spn_dark_nature_trigger = no # sadistic, callous, vengeful, lunatic or possessed (zz_spn_order_triggers.txt)
			}
		}
	}
""")

# 60 -- Magical Research, choose the topic (magic_ev11.34) option b.
E('events/ev11.txt',
"""				value = var:drawn_option2
			}
			mr_launch_effect = yes
		}
	}
""",
"""				value = var:drawn_option2
			}
			mr_launch_effect = yes
		}
		ai_chance = { # 2.38e (Supernatural): the AI takes up necromancy mostly when its nature fits
			base = 100
			modifier = {
				factor = 0.1
				OR = {
					AND = {
						var:drawn_option2 ?= flag:necromancy
						NOR = { has_trait = necromancer has_trait = warlock } # mr_necromancy_effect gives them no trait
					}
					var:drawn_option2 ?= flag:lich # mr_lich_effect adds necromancer
				}
				spn_dark_nature_trigger = no # sadistic, callous, vengeful, lunatic or possessed (zz_spn_order_triggers.txt)
			}
		}
	}
""")

# 61 -- Magical Research, choose the topic (magic_ev11.34) option c.
E('events/ev11.txt',
"""				value = var:drawn_option3
			}
			mr_launch_effect = yes
		}
	}
""",
"""				value = var:drawn_option3
			}
			mr_launch_effect = yes
		}
		ai_chance = { # 2.38e (Supernatural): the AI takes up necromancy mostly when its nature fits
			base = 100
			modifier = {
				factor = 0.1
				OR = {
					AND = {
						var:drawn_option3 ?= flag:necromancy
						NOR = { has_trait = necromancer has_trait = warlock } # mr_necromancy_effect gives them no trait
					}
					var:drawn_option3 ?= flag:lich # mr_lich_effect adds necromancer
				}
				spn_dark_nature_trigger = no # sadistic, callous, vengeful, lunatic or possessed (zz_spn_order_triggers.txt)
			}
		}
	}
""")

# 62 -- Magical Research, choose the topic, option d (never necromancy or lich; a weight so all five are set).
E('events/ev11.txt',
"""				value = var:drawn_option4
			}
			mr_launch_effect = yes
		}
		
	}
""",
"""				value = var:drawn_option4
			}
			mr_launch_effect = yes
		}
		
		ai_chance = { # 2.38e (Supernatural): every option of this event has a weight now, equal to options a-c before their modifier
			base = 100
		}
	}
""")

# 63 -- Magical Research, choose the topic, option e (switch intents).
E('events/ev11.txt',
"""			trigger_event = {
				id = magic_ev11.34
				days = 11
			}
		}
	}
""",
"""			trigger_event = {
				id = magic_ev11.34
				days = 11
			}
		}
		ai_chance = { # 2.38e (Supernatural): every option of this event has a weight now, equal to options a-c before their modifier
			base = 100
		}
	}
""")

# 64 -- The demon's reward (magic_ev.16), option b: the necromancer trait and a skeleton host.
# 2.39 (WORK-ORDER-2.39 B14, entry 89): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream
E('events/ev1.txt',
"""		ai_chance = {
			base = 10
			modifier = {
				add = 40
				OR = {
					has_trait = necromancer
					has_trait = necromancer2
					has_trait = corrupted
				}
			}
		}
	}

	option = {
		name = ev16.0.c
""",
"""		ai_chance = {
			base = 10
			modifier = {
				add = 40
				OR = {
					has_trait = necromancer
					has_trait = warlock
					has_trait = corrupted
				}
			}
			modifier = { # 2.38e (Supernatural): the AI takes the necromancer trait mostly when its nature fits
				factor = 0.1
				NOR = {
					has_trait = necromancer # no new trait for them (the option's own guard)
					has_trait = warlock
					has_trait = corrupted # Witchcraft's own +40 lean above
				}
				spn_dark_nature_trigger = no # sadistic, callous, vengeful, lunatic or possessed (zz_spn_order_triggers.txt)
			}
		}
	}

	option = {
		name = ev16.0.c
""")

# 65 -- Magical Experiments, the death project (magic_ev7.112): grants necromancer on success.
E('events/ev7.txt',
"""		hidden_effect = {
			add_character_flag = me_death_project_progress
			trigger_event = {
				id = magic_ev7.114
				days = { 10 20 }
			}
		}
		ai_chance = {
			base = 10
		}
	}
	option = {
		name = me_ascendency_option
""",
"""		hidden_effect = {
			add_character_flag = me_death_project_progress
			trigger_event = {
				id = magic_ev7.114
				days = { 10 20 }
			}
		}
		ai_chance = {
			base = 10
			modifier = { # 2.38e (Supernatural): a cannibal who is no necromancer gains the trait here; mostly when his nature fits
				factor = 0.1
				NOR = {
					has_trait = necromancer
				}
				spn_dark_nature_trigger = no # sadistic, callous, vengeful, lunatic or possessed (zz_spn_order_triggers.txt)
			}
		}
	}
	option = {
		name = me_ascendency_option
""")

# 66 -- Magical Artifacts (magic_ev.99), 'Guaranteed for the player' after the players / 'Player's Area': courtiers and adventurers can find one.
# 2.39 (WORK-ORDER-2.39 B14, entry 91): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream
E('events/ev1.txt',
"""				random_ruler = {
					limit = {
						is_landed_or_landless_administrative = yes	
						primary_title = { is_mercenary_company = no }	
						highest_held_title_tier>1
						exists = dynasty		
						dynasty={
							NOT={
								has_variable=ev1used
							}
						}
						in_diplomatic_range = scope:player0
					}
					random_list = {
						#necro
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = necronomicon } }
							}
							
							trigger_event = magic_ev.57
							trigger_event = magic_ev.1
						}
						#ring
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = magic_ring0 } }
							}
""",
"""				# 2.38e (Supernatural): the finder can be a courtier or a landless adventurer, not only a landed ruler. One ruler is
				# picked as before (or an adventurer), then the finder: the ruler himself (3 in 4) or an adult courtier of a
				# dynasty that has found none (1 in 4). The random_ruler now only chooses; the finder runs the list below.
				random_ruler = {
					limit = {
						OR = {
							AND = {
								is_landed_or_landless_administrative = yes
								primary_title = { is_mercenary_company = no }
								highest_held_title_tier > 1
							}
							is_landless_adventurer = yes
						}
						OR = {
							spn_magic_art_finder_ok_trigger = yes
							any_courtier = { spn_magic_art_courtier_ok_trigger = yes }
						}
						# 2.30 bugfix: guarded -- unset in observer mode
						trigger_if = {
							limit = { exists = scope:player0 }
							in_diplomatic_range = scope:player0
						}
					}
					spn_magic_art_pick_finder_effect = yes # zz_spn_relic_effects.txt: himself 3 in 4, a courtier 1 in 4
				}
				scope:spn_magic_art_finder ?= {
					random_list = {
						#necro
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = blackgrimoire } }
							}
							
							trigger_event = magic_ev.57
							trigger_event = magic_ev.1
						}
						#ring
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = magic_ring0 } }
								is_ruler = yes # 2.38e (Supernatural): the ring's after-block seats Merlin at the finder's court (employer = root)
							}
""")

# 67 -- Magical Artifacts (magic_ev.99), 'Random Distribution' (the default): the same.
# 2.39 (WORK-ORDER-2.39 B14, entry 92): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream
E('events/ev1.txt',
"""				random_ruler = {
					limit = {
						is_landed_or_landless_administrative = yes	
						primary_title = { is_mercenary_company = no }	
						highest_held_title_tier>1
						exists = dynasty		
						dynasty={
							NOT={
								has_variable=ev1used
							}
						}
					}
					random_list = {
						#necro
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = necronomicon } }
							}
							
							trigger_event = magic_ev.57
							trigger_event = magic_ev.1
						}
						#ring
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = magic_ring0 } }
							}
""",
"""				# 2.38e (Supernatural): the finder can be a courtier or a landless adventurer, not only a landed ruler. One ruler is
				# picked as before (or an adventurer), then the finder: the ruler himself (3 in 4) or an adult courtier of a
				# dynasty that has found none (1 in 4). The random_ruler now only chooses; the finder runs the list below.
				random_ruler = {
					limit = {
						OR = {
							AND = {
								is_landed_or_landless_administrative = yes
								primary_title = { is_mercenary_company = no }
								highest_held_title_tier > 1
							}
							is_landless_adventurer = yes
						}
						OR = {
							spn_magic_art_finder_ok_trigger = yes
							any_courtier = { spn_magic_art_courtier_ok_trigger = yes }
						}
					}
					spn_magic_art_pick_finder_effect = yes # zz_spn_relic_effects.txt: himself 3 in 4, a courtier 1 in 4
				}
				scope:spn_magic_art_finder ?= {
					random_list = {
						#Grimoire
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = blackgrimoire } }
							}
							
							trigger_event = magic_ev.57
							trigger_event = magic_ev.1
						}
						#ring
						1 = {
							trigger = {
								NOT = { any_artifact = { has_variable = magic_ring0 } }
								is_ruler = yes # 2.38e (Supernatural): the ring's after-block seats Merlin at the finder's court (employer = root)
							}
""")

# 68 -- Healing (extra_healing_effect, the Ring of Life's heal, the lich, the potion, the monkey demon) took the Horned God's Claws.
E('common/scripted_effects/00_magic_advanced_effects.txt',
"""	if = { limit = { has_character_modifier = magic_claws_modifier }
		remove_character_modifier = magic_claws_modifier
	}
	if = { limit = { has_trait = one_eyed }
""",
"""	# 2.38e (Supernatural): the Claws are the Horned God's gift (magic_ev11.112/.118, magic_ev9.99), not a wound. Witchcraft already
	# commented this out of full_healing_effect and the potion interaction; this copy was missed (player report, Oct 2026).
	#if = { limit = { has_character_modifier = magic_claws_modifier }
	#	remove_character_modifier = magic_claws_modifier
	#}
	if = { limit = { has_trait = one_eyed }
""")

# =====================================================================================================================
# 2.38f (Supernatural): from Thomas's 233-year run (867 start). Four Witchcraft defects in error.log, and the True Witch
# spawner that the Order's Mages had shut off.
# =====================================================================================================================

# 69 -- The murder (magic_ev.54): the secret named the spouse after the spouse was dead (a null target, and a dozen
# vanilla secret errors after it). The secret first, then the death.
E('events/ev1.txt',
"""		name = ev54.0.a
		root.primary_spouse = {
			death = {
				death_reason = death_murder
				killer = scope:target
			}
			
		}
		hidden_effect = {
			scope:target = {
				add_secret = {
					type = secret_murder
					target = root.primary_spouse
				}
			}
		}
""",
"""		name = ev54.0.a
		hidden_effect = { # 2.38f (Supernatural): the secret first, while the spouse is alive to be named in it
			scope:target = {
				add_secret = {
					type = secret_murder
					target = root.primary_spouse
				}
			}
		}
		root.primary_spouse = {
			death = {
				death_reason = death_murder
				killer = scope:target
			}
			
		}
""")

# 70 -- magic_ev6.17 (Asmodeus asks for your heir): a character with no player heir, or no heir at all, read a null
# scope, and "as you wish" then killed nobody and still gave Kinslayer. The event needs an heir to be about.
E('events/ev6.txt',
"""	trigger = {
		is_alive = yes
	}
	immediate = {
		root.player_heir = {
			save_scope_as = hier
		}
		if = {
			limit = {
				NOT = {
					exists = scope:hier
				}
			}
			primary_heir = {
				save_scope_as = hier
			}
		}
""",
"""	trigger = {
		is_alive = yes
		OR = { # 2.38f (Supernatural): no heir, nothing to ask for
			exists = player_heir
			exists = primary_heir
		}
	}
	immediate = {
		root.player_heir ?= {
			save_scope_as = hier
		}
		if = {
			limit = {
				NOT = {
					exists = scope:hier
				}
			}
			primary_heir ?= {
				save_scope_as = hier
			}
		}
""")

# 71 -- The demon child (magic_ev2.26 option c): the child could already be dead.
E('events/ev2.txt',
"""		name = ev2.26.c
		custom_tooltip = ev2.26.c_ct
		trigger_event = magic_ev.18
		hidden_effect = {
			scope:demon_child = {
				death = natural
			}
		}
""",
"""		name = ev2.26.c
		custom_tooltip = ev2.26.c_ct
		trigger_event = magic_ev.18
		hidden_effect = {
			scope:demon_child ?= {
				if = { # 2.38f (Supernatural): the child may already be dead
					limit = { is_alive = yes }
					death = natural
				}
			}
		}
""")

# 72 -- Summoning Moloch: a summoner who died in the summoning still had a flag written on him.
E('common/scripted_effects/00_summoning_magic_effects.txt',
"""	if = {
		limit = {
			NOT = {
				has_character_flag = ms_met_moloch
			}
		}
		trigger_event = magic_ev3.66
		add_character_flag = ms_met_moloch
	}
	else = {
		trigger_event = magic_ev9.76
	}
""",
"""	if = {
		limit = {
			is_alive = yes # 2.38f (Supernatural): the summoner may not have survived it
			NOT = {
				has_character_flag = ms_met_moloch
			}
		}
		trigger_event = magic_ev3.66
		add_character_flag = ms_met_moloch
	}
	else_if = {
		limit = { is_alive = yes }
		trigger_event = magic_ev9.76
	}
""")

# 73 -- The yearly spawner made True Witches only while the world had too few Mages. The Order's Mages fill that count, so
# no True Witch was made for two centuries (Thomas's run: 86 Mages, 1 True Witch). True Witches now have their own count,
# the same size as the Mages' (num_of_mages_limit_value, from the game rule).
E('common/scripted_effects/00_variety_magic_effects.txt',
"""			random_list = {
				1 = {
					create_true_witch_effect = yes
				}
				1 = {
					create_pure_wandering_true_witch_effect = yes
				}
			}
		}
	}
}""",
"""		}
		# 2.38f (Supernatural): True Witches on their own count (the Order's Mages no longer shut this off).
		if = {
			limit = {
				NOT = {
					has_game_rule = min_num_of_mages
				}
				any_living_character = {
					has_trait = true_witch
					is_ai = yes
					count < num_of_mages_limit_value
				}
			}
			random_list = {
				1 = {
					create_true_witch_effect = yes
				}
				1 = {
					create_pure_wandering_true_witch_effect = yes
				}
			}
		}
	}
}""")

# =====================================================================================================================
# 2.38h (Supernatural): from Thomas's 1178 run (152 years). Four more Witchcraft defects in error.log.
# =====================================================================================================================

# 74 -- The dark champion's special task ends after he died in a mage duel (magic_ev10.146): flags on a dead man.
E('common/court_positions/tasks/01_magic_court_positions_tasks.txt',
"""	on_end = {
		remove_character_flag = ready_for_special_mission
		clear_dc_mission_flags = yes
	}
""",
"""	on_end = {
		if = { # 2.38h (Supernatural): he may have died on the mission
			limit = { is_alive = yes }
			remove_character_flag = ready_for_special_mission
			clear_dc_mission_flags = yes
		}
	}
""")

# 75 -- Steal a life (magic_ev.5): the immediate can find no one to drain, and the options then read an unset scope. Each
# read is made safe; the spell still works on the caster (the perk's lifestealer), it simply drains no one.
# 2.39 (WORK-ORDER-2.39 B14, entry 100): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream
E('events/ev1.txt',
"""		mark_as_black_magic_caster_effect = { L = 1 }
		add_character_modifier = lifestealer_modifier
		scope:potential_sacrifice = {
			add_character_modifier = lifestealed_modifier
		}
""",
"""		mark_as_black_magic_caster_effect = { L = 1 }
		add_character_modifier = lifestealer_modifier
		scope:potential_sacrifice ?= { # 2.38h (Supernatural): there may be no one to drain
			add_character_modifier = lifestolen_modifier
		}
""")
E('events/ev1.txt',
"""			modifier = {
				add = -90
				scope:potential_sacrifice = {
					NOT = {
						has_trait = callous
""",
"""			modifier = {
				add = -90
				scope:potential_sacrifice ?= { # 2.38h (Supernatural)
					NOT = {
						has_trait = callous
""")
# 2.39 (WORK-ORDER-2.39 B14, entry 102): re-anchored on Witchcraft 2.18's own text; the old anchor held the mod's
# text and never matched upstream
E('events/ev1.txt',
"""		mark_as_black_magic_caster_effect = { L = 1 }
		add_character_modifier = lifestealed_modifier
		scope:potential_sacrifice = {
			add_character_modifier = lifestealer_modifier
		}
""",
"""		mark_as_black_magic_caster_effect = { L = 1 }
		add_character_modifier = lifestolen_modifier
		scope:potential_sacrifice ?= { # 2.38h (Supernatural): there may be no one to drain
			add_character_modifier = lifestealer_modifier
		}
""")

# 76 -- Cut the schemes (magic_ev10.18): the agent could be dead by the time he was to be imprisoned.
E('events/ev10.txt',
"""								if = {
									limit = {
										exists = scope:hagent
									}
									imprison = {
""",
"""								if = {
									limit = {
										scope:hagent ?= { is_alive = yes } # 2.38h (Supernatural): he may be dead
									}
									imprison = {
""")

# 76b -- The same, in the event's two other branches.
E('events/ev10.txt',
"""						if = {
							limit = {
								exists = scope:hagent
							}
							imprison = {
""",
"""						if = {
							limit = {
								scope:hagent ?= { is_alive = yes } # 2.38h (Supernatural): he may be dead
							}
							imprison = {
""")
E('events/ev10.txt',
"""				if = {
					limit = {
						exists = scope:hagent
					}
					imprison = {
""",
"""				if = {
					limit = {
						scope:hagent ?= { is_alive = yes } # 2.38h (Supernatural): he may be dead
					}
					imprison = {
""")

# 77 -- Embezzle from the council (magic_ev10.70 option e): when the embezzler is the Grand Magus himself, the secret
# was his own (owner and target the same). It names the next officer instead, or no one.
E('events/ev10.txt',
"""		name = ev10.70.e
		trigger = {
			mc_gold_global_avaiable_trigger = yes
		}
		if = {
			limit = {
				exists = global_var:current_archmage_global
			}
			give_or_update_embezzler_secret_effect = {
				TARGET = global_var:current_archmage_global
				STAKE = mc_minor_gold_value
			}
		}
		else_if = {
			limit = {
				exists = global_var:current_black_mage_global
			}
""",
"""		name = ev10.70.e
		trigger = {
			mc_gold_global_avaiable_trigger = yes
		}
		if = {
			limit = {
				exists = global_var:current_archmage_global
				NOT = { global_var:current_archmage_global = root } # 2.38h (Supernatural): not a secret about himself
			}
			give_or_update_embezzler_secret_effect = {
				TARGET = global_var:current_archmage_global
				STAKE = mc_minor_gold_value
			}
		}
		else_if = {
			limit = {
				exists = global_var:current_black_mage_global
				NOT = { global_var:current_black_mage_global = root } # 2.38h (Supernatural)
			}
""")

# =====================================================================================================================
# 2.39 (Supernatural) -- package P6 (WORK-ORDER-2.39)
# =====================================================================================================================
# ---------------------------------------------------------------------------------------------------------------------
# 2.39 B14 (WORK-ORDER-2.39) -- Supernatural's hand edits in Witchcraft-origin files that the generator did not know.
# GENERATED by tool/pkgs/P6/b14_register.py from Witchcraft 2.18 and the 2.38 mod. Each `old` is Witchcraft 2.18's own
# text (after the entries above), each `new` the mod's text, so on the mod every entry reads as already present. On a
# fresh Witchcraft copy they rebuild the mod's text; tool/pristine_test.py proves it byte for byte.
# 148 entries; 66 species gates (spn_is_valid_supernatural_target) among them; the other gates sit in re-anchored
# entries 53 (#27), 81 (#56) and 82 (#57).
# ---------------------------------------------------------------------------------------------------------------------

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in against_the_witch_war (mod line 913)
E('common/casus_belli_types/01_magic_cb.txt',
"""											NOT = { has_trait = witch }
										}
""",
"""											NOT = { has_trait = witch }
											# 2.31c -- this writes the trait RAW, so it is the one witch door that does not
											# pass through give_witch_secret_or_trait_effect2 and its gate. An AI winning
											# this war converts every character of every shunning faith at once, which
											# with the AGOT patch loaded meant dragons and the walking dead among them.
											spn_is_valid_supernatural_target = yes
										}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in cast_curse (mod line 43)
E('common/character_interactions/00_magic_interactions.txt',
"""		#			}
		#		}
		#	}
		#}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""",
"""		#			}
		#		}
		#	}
		#}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in magic_domination (mod line 328)
E('common/character_interactions/00_magic_interactions.txt',
"""						liege.location = liege.capital_province
					}
				}
			}
		}
	}
	icon = icon_magic
""",
"""						liege.location = liege.capital_province
					}
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in magic_healing (mod line 640)
E('common/character_interactions/00_magic_interactions.txt',
"""		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_friendly

	cooldown_against_recipient = { months = 3 } 
""",
"""		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_favorites # 2.38a (Supernatural): the Supernatural menu (was interaction_category_friendly)

	cooldown_against_recipient = { months = 6 } 
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in cast_powerfull_curse (mod line 872)
E('common/character_interactions/00_magic_interactions.txt',
"""				
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""",
"""				
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in banish_demon (mod line 1135)
E('common/character_interactions/00_magic_interactions.txt',
"""		#			has_character_modifier = touched_divinity_modifier
		#		}
		#	}
		#}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""",
"""		#			has_character_modifier = touched_divinity_modifier
		#		}
		#	}
		#}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in consume_child (mod line 1305)
E('common/character_interactions/00_magic_interactions.txt',
"""			}
		}
	}
	icon = icon_cann
""",
"""			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_cann
""")

# 2.39 B14 -- register: consume_child: SUPERNATURAL, spn_mark_menace_effect, spn_menace_marked_recently, 2.35 (mod line 1326)
E('common/character_interactions/00_magic_interactions.txt',
"""	on_accept = {
		scope:actor = {
			hidden_effect = {
				random_list = {
""",
"""	on_accept = {
		scope:actor = {
			# SUPERNATURAL 2.35 PART TWO -- ADDED, one block, nothing below changed. (W-W2, order §3.3, §12.)
			# A child is gone. That is a body, not a rumour, so the county remembers it as a `kill` -- and the
			# dedupe flag this leaves is what stops spawn_witch_hunter_full_chance_effect writing a second,
			# quieter mark for the same night.
			if = {
				limit = {
					NOT = { has_character_flag = spn_menace_marked_recently }
					exists = location
					location = { exists = county }
				}
				spn_mark_menace_effect = {
					COUNTY = location.county
					CULPRIT = this
					KIND = witch
					SEVERITY = kill
				}
			}
			hidden_effect = {
				random_list = {
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in use_singularity (mod line 2127)
E('common/character_interactions/00_magic_interactions.txt',
"""				NOT = {	has_variable = pclash	}
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""",
"""				NOT = {	has_variable = pclash	}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in death_wish (mod line 2504)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_trait = immortal2
				}
			}
		}
""",
"""					has_trait = immortal2
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in teach_sorcery (mod line 2666)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_character_flag = arcane_unlocked_flag
				}
			}
		}
	}
""",
"""					has_character_flag = arcane_unlocked_flag
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in witch_trial (mod line 2807)
E('common/character_interactions/00_magic_interactions.txt',
"""		}	
	}
	#is_valid_showing_failures_only = {
	#	
""",
"""		}	
	}
	is_valid_showing_failures_only = {
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	#is_valid_showing_failures_only = {
	#	
""")

# 2.39 B14 -- register: stop_the_witch: supernatural_hunter (mod line 2868)
E('common/character_interactions/00_magic_interactions.txt',
"""				has_trait_xp = {
					trait = witch_hunter
					value > 29
""",
"""				has_trait_xp = {
					trait = supernatural_hunter
					track = witch_hunting
					value > 29
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in stop_the_witch (mod line 2894)
E('common/character_interactions/00_magic_interactions.txt',
"""			custom_description = {
				text = has_hook_on_you_custom
				NOT = { has_hook = scope:actor }
			}
		}
	}
""",
"""			custom_description = {
				text = has_hook_on_you_custom
				NOT = { has_hook = scope:actor }
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in fed_dark_blade_interaction (mod line 2975)
E('common/character_interactions/00_magic_interactions.txt',
"""		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""",
"""		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in demand_submission_cgm_interaction (mod line 3158)
E('common/character_interactions/00_magic_interactions.txt',
"""			}
		}	
	}
	icon = icon_grandmaster_coven
""",
"""			}
		}	
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_grandmaster_coven
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in send_agent_cgm_interaction (mod line 3432)
E('common/character_interactions/00_magic_interactions.txt',
"""			is_landed_or_landless_administrative = yes
		}
""",
"""			is_landed_or_landless_administrative = yes
		}
	}
	is_valid_showing_failures_only = {
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in command_minion_interaction (mod line 3712)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_trait = demon2
				}
			}
		}
	}
""",
"""					has_trait = demon2
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in power_strike (mod line 5012)
E('common/character_interactions/00_magic_interactions.txt',
"""		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	category = interaction_category_hostile

""",
"""		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	category = interaction_category_hostile

""")

# 2.39 B14 -- register: power_strike: supernatural_hunter (mod line 5356)
E('common/character_interactions/00_magic_interactions.txt',
"""				OR = {
					has_trait = witch_hunter
					any_secret = {
""",
"""				OR = {
					has_trait = supernatural_hunter
					any_secret = {
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in teach_spells (mod line 5453)
E('common/character_interactions/00_magic_interactions.txt',
"""				NOT = { has_trait = incapable }
			}
		}
	}
	icon = icon_learning
	common_interaction = yes
""",
"""				NOT = { has_trait = incapable }
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_learning
	common_interaction = yes
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in aura_boost (mod line 5539)
E('common/character_interactions/00_magic_interactions.txt',
"""				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_friendly

	cooldown_against_recipient = { years = 1 } 
""",
"""				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_favorites # 2.38a (Supernatural): the Supernatural menu (was interaction_category_friendly)

	cooldown_against_recipient = { years = 1 } 
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in bless_land (mod line 5777)
E('common/character_interactions/00_magic_interactions.txt',
"""				NOT = {	has_variable = pclash	}
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
""",
"""				NOT = {	has_variable = pclash	}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in shadowstep_spell (mod line 5922)
E('common/character_interactions/00_magic_interactions.txt',
"""				}
			}
		}
		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_friendly
	desc = shadowstep_spell_desc
""",
"""				}
			}
		}
		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_favorites # 2.38a (Supernatural): the Supernatural menu (was interaction_category_friendly)
	desc = shadowstep_spell_desc
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in plague_spell (mod line 6147)
E('common/character_interactions/00_magic_interactions.txt',
"""				
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
	category = interaction_category_hostile

	cooldown_against_recipient = { years = 5 } 
	cooldown = { years = 1 } 
""",
"""				
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
	category = interaction_category_hostile

	cooldown_against_recipient = { years = 5 } 
	cooldown = { years = 1 } 
""")

# 2.39 B14 -- register: plague_spell: SUPERNATURAL, spn_mark_menace_effect, spn_menace_marked_recently, 2.35 (mod line 6178)
E('common/character_interactions/00_magic_interactions.txt',
"""			save_scope_as = magic_user
			
			hidden_effect = {
""",
"""			save_scope_as = magic_user
			# SUPERNATURAL 2.35 PART TWO -- ADDED, one block, nothing below changed. (W-W2, order §3.3, §12.)
			# A plague leaves bodies, so this county's mark is a `kill`, and the dedupe flag it leaves keeps
			# the spawn effect's quieter `prowl` mark from doubling it.
			if = {
				limit = {
					NOT = { has_character_flag = spn_menace_marked_recently }
					exists = location
					location = { exists = county }
				}
				spn_mark_menace_effect = {
					COUNTY = location.county
					CULPRIT = this
					KIND = witch
					SEVERITY = kill
				}
			}

			hidden_effect = {
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in hipercognition (mod line 6353)
E('common/character_interactions/00_magic_interactions.txt',
"""				can_spend_standard_ps_trigger = yes
			}
		}
		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_friendly

""",
"""				can_spend_standard_ps_trigger = yes
			}
		}
		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_favorites # 2.38a (Supernatural): the Supernatural menu (was interaction_category_friendly)

""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in firestorm_spell (mod line 6562)
E('common/character_interactions/00_magic_interactions.txt',
"""				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
	category = interaction_category_hostile

	cooldown_against_recipient = { years = 5 } 
	cooldown = { years = 1 } 
""",
"""				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
	category = interaction_category_hostile

	cooldown_against_recipient = { years = 5 } 
	cooldown = { years = 1 } 
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in mana_siphon_spell (mod line 6744)
E('common/character_interactions/00_magic_interactions.txt',
"""			}
		}
	}
	icon = icon_ps
""",
"""			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_ps
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in mage_duel (mod line 7193)
E('common/character_interactions/00_magic_interactions.txt',
"""				text = has_antimagic_seal
				is_antimagic_trigger = no
			}
		}
	}
""",
"""				text = has_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in mind_scan (mod line 8210)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_character_modifier = master_psionic_modifier
				}
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""",
"""					has_character_modifier = master_psionic_modifier
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in use_raw_magic (mod line 8320)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_trait = demon2
					has_trait = yaga
				}
			}
		}
	}
""",
"""					has_trait = demon2
					has_trait = yaga
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: start_corruption_interaction: supernatural_hunter (mod line 8479)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_trait = corrupted
					has_trait = witch_hunter2
				}
""",
"""					has_trait = corrupted
					has_trait = supernatural_hunter
				}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in start_corruption_interaction (mod line 8506)
E('common/character_interactions/00_magic_interactions.txt',
"""			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}

""",
"""			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}

""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in special_champion_mission (mod line 8780)
E('common/character_interactions/00_magic_interactions.txt',
"""				is_at_war = no
			}
		}
	}
	icon = icon_dark_champion
""",
"""				is_at_war = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_dark_champion
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in soul_transfer_spell (mod line 9023)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_trait = incapable
				}
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""",
"""					has_trait = incapable
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in aura_reading (mod line 9108)
E('common/character_interactions/00_magic_interactions.txt',
"""				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	category = interaction_category_hostile
""",
"""				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	category = interaction_category_hostile
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in cyro_proposal_interaction (mod line 9237)
E('common/character_interactions/00_magic_interactions.txt',
"""					has_character_modifier = no_soul_modifier
				}
			}
		}
	}
""",
"""					has_character_modifier = no_soul_modifier
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in tornado_spell (mod line 9564)
E('common/character_interactions/00_magic_interactions.txt',
"""			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
	category = interaction_category_hostile

	#cooldown_against_recipient = { years = 5 } 
""",
"""			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
	category = interaction_category_hostile

	#cooldown_against_recipient = { years = 5 } 
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in drink_magic_potion_interaction (mod line 9710)
E('common/character_interactions/00_magic_interactions.txt',
"""			}
		}	
	}
	
""",
"""			}
		}	
	}
	is_valid_showing_failures_only = {
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in upgrade_amulet_interaction (mod line 10784)
E('common/character_interactions/00_magic_interactions.txt',
"""					is_equipped = no
				}
			}
		}
	}

	on_accept = {
""",
"""					is_equipped = no
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}

	on_accept = {
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in body_adaptation (mod line 10967)
E('common/character_interactions/00_magic_interactions.txt',
"""			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_demon
""",
"""			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_demon
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in demon_annihilation (mod line 11361)
E('common/character_interactions/00_magic_interactions.txt',
"""				}
			}
		}
	}
	icon = icon_demon
	common_interaction = no
""",
"""				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_demon
	common_interaction = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in invite_to_high_council_interaction (mod line 11611)
E('common/character_interactions/00_magic_interactions.txt',
"""				#	is_alive = yes
				#}
			}
		}
	}
""",
"""				#	is_alive = yes
				#}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in remove_from_high_council_interaction (mod line 12209)
E('common/character_interactions/00_magic_interactions.txt',
"""				}
			}
		}
	}
	icon = icon_archmage
	ai_maybe = no
""",
"""				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_archmage
	ai_maybe = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in demand_submission_archmage_interaction (mod line 12359)
E('common/character_interactions/00_magic_interactions.txt',
"""				NOT = { has_variable = mc_member_var }
			}
		}
""",
"""				NOT = { has_variable = mc_member_var }
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in ask_mc_for_support_interaction (mod line 12648)
E('common/character_interactions/00_magic_interactions.txt',
"""				}
			}
		}
	}
	icon = icon_archmage
	#ai_maybe = no
""",
"""				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_archmage
	#ai_maybe = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in magic_inception_interaction (mod line 13064)
E('common/character_interactions/00_magic_interactions.txt',
"""				text = has_magic_immunity
				is_ai = yes
			}
		}
	}
""",
"""				text = has_magic_immunity
				is_ai = yes
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in antimagic_seal (mod line 13419)
E('common/character_interactions/00_magic_interactions.txt',
"""				has_immunity_for_antimagic_seal = no
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""",
"""				has_immunity_for_antimagic_seal = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in threaten_with_magic_interaction (mod line 13568)
E('common/character_interactions/00_magic_interactions.txt',
"""			NOT = { has_strong_hook = scope:actor }
		}
""",
"""			NOT = { has_strong_hook = scope:actor }
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in join_mages_summit (mod line 14276)
E('common/character_interactions/00_magic_interactions.txt',
"""			#is_in_army = no
		}
""",
"""			#is_in_army = no
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in thorn_walls_spell (mod line 14363)
E('common/character_interactions/00_magic_interactions.txt',
"""		}
		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_friendly

	cooldown_against_recipient = { years = 2 } 
""",
"""		}
		scope:actor = {
			custom_description = {
				text = have_antimagic_seal
				is_antimagic_trigger = no
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = yes
	interface_priority = 90
	category = interaction_category_favorites # 2.38a (Supernatural): the Supernatural menu (was interaction_category_friendly)

	cooldown_against_recipient = { years = 2 } 
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in ask_tw_for_initiation_interaction (mod line 14488)
E('common/character_interactions/00_magic_interactions.txt',
"""			is_witch_hunter = no
		}
""",
"""			is_witch_hunter = no
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in shot_from_cover_interaction (mod line 14762)
E('common/character_interactions/00_magic_interactions.txt',
"""			}
		}
	}
	icon = icon_crossbowmen
""",
"""			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_crossbowmen
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in earthquake_spell (mod line 14862)
E('common/character_interactions/00_magic_interactions.txt',
"""			}
		}
		scope:actor = {
			custom_description = {
				text = power_needed_custom
				can_spend_standard_ps_trigger = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""",
"""			}
		}
		scope:actor = {
			custom_description = {
				text = power_needed_custom
				can_spend_standard_ps_trigger = yes
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in stop_the_cataclysm_spell (mod line 14990)
E('common/character_interactions/00_magic_interactions.txt',
"""						situation_current_phase = impact
					}
				}
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
""",
"""						situation_current_phase = impact
					}
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
	popup_on_receive = no
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in teleportation_spell (mod line 15112)
E('common/character_interactions/00_magic_interactions.txt',
"""					is_paused = no
				}
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""",
"""					is_paused = no
				}
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in use_nyx_powers_interaction (mod line 15170)
E('common/character_interactions/00_magic_interactions.txt',
"""	is_valid_showing_failures_only = {
		scope:recipient = {
			is_imprisoned = no
		}
	}
	icon = icon_magic
""",
"""	is_valid_showing_failures_only = {
		scope:recipient = {
			is_imprisoned = no
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in psychic_surgery_spell (mod line 15243)
E('common/character_interactions/00_magic_interactions.txt',
"""			has_physical_contanct2 = yes
		}
		scope:actor = {
			custom_description = {
				text = power_needed_custom
				can_spend_standard_ps_trigger = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""",
"""			has_physical_contanct2 = yes
		}
		scope:actor = {
			custom_description = {
				text = power_needed_custom
				can_spend_standard_ps_trigger = yes
			}
		}
		scope:recipient = {
			custom_description = {
				text = has_magic_immunity
				spn_is_valid_supernatural_target = yes
			}
		}
	}
	icon = icon_magic
	common_interaction = no
	interface_priority = 90
""")

# 2.39 B14 -- register: dark_champion_court_position: supernatural_hunter (mod line 573)
E('common/court_positions/types/01_court_positions_magic.txt',
"""			limit = {
				has_trait = witch_hunter2
			}
""",
"""			limit = {
				has_trait = supernatural_hunter
			}
""")

# 2.39 B14 -- register: dark_champion_court_position: supernatural_hunter (mod line 666)
E('common/court_positions/types/01_court_positions_magic.txt',
"""				has_trait = golem
				has_trait = witch_hunter2
				custom_description = {
""",
"""				has_trait = golem
				has_trait = supernatural_hunter
				custom_description = {
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in cult_priest_camp_officer (mod line 1071)
E('common/court_positions/types/01_court_positions_magic.txt',
"""						is_witch_trigger = no
					}
""",
"""						is_witch_trigger = no
						# 2.31c -- raw add_trait, so the gate on give_witch_secret_or_trait_effect2 does not
						# cover it, and AI lieges fill court positions every year.
						spn_is_valid_supernatural_target = yes
					}
""")

# 2.39 B14 -- register: esoteric_training_decision: supernatural_hunter (mod line 1260)
E('common/decisions/magic_dec.txt',
"""			}
			has_trait = witch_hunter2
		}
""",
"""			}
			has_trait_xp = {
				trait = supernatural_hunter
				track = witch_hunting
				value >= 25
			}
		}
""")

# 2.39 B14 -- register: esoteric_training_decision: supernatural_hunter (mod line 1283)
E('common/decisions/magic_dec.txt',
"""			limit = {
				has_trait = witch_hunter2
				is_witch_trigger = no
""",
"""			limit = {
				has_trait = supernatural_hunter
				is_witch_trigger = no
""")

# 2.39 B14 -- register: esoteric_training_decision: supernatural_hunter (mod line 1345)
E('common/decisions/magic_dec.txt',
"""						NOR = {
							has_trait = witch_hunter
							has_character_modifier = novice_witch_hunter_modifier
""",
"""						NOR = {
							has_trait = supernatural_hunter
							has_character_modifier = novice_witch_hunter_modifier
""")

# 2.39 B14 -- register: claim_yaga_title_decision: supernatural_hunter, supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 2156)
E('common/decisions/magic_dec.txt',
"""		}
		NOT = {	has_trait = yaga	}
		has_witch_house_trigger = yes
""",
"""		}
		NOR = {	#Added NOR instead of NOT due to a error request in SPN Discord for being able to claim title as a supernatural
			has_trait = yaga
			has_trait = supernatural_vampire
			has_trait = supernatural_werewolf
			has_trait = supernatural_hybrid
			has_trait = supernatural_hunter
		}
		has_witch_house_trigger = yes
""")

# 2.39 B14 -- register: become_fallen_hunter_decision: supernatural_hunter, 2.35 (mod line 2650)
E('common/decisions/magic_dec.txt',
"""	}
	is_shown = {
		has_trait = witch_hunter
		any_character_artifact = {
			has_variable = magic1
		}
		is_imprisoned = no
""",
"""	}
	# 2.35 -- the catalyst requirement moved out of is_shown. It used to make the whole decision VANISH the
	# moment the artifact left your inventory -- stolen, given away, lost on death -- with no explanation.
	# is_shown still gates on the hunter trait and nothing else, so a werewolf or a vampire never sees this
	# at all; a hunter without a catalyst sees it greyed out with the reason on it.
	is_shown = {
		has_trait = supernatural_hunter
	}

	is_valid = {
		is_imprisoned = no
		custom_tooltip = {
			text = become_fallen_hunter_needs_catalyst_tt
			any_character_artifact = {
				has_variable = magic1
			}
		}
""")

# 2.39 B14 -- register: yearly_global_pulse: spn_xp_sys (mod line 7)
E('common/on_action/yearly2_on_actions.txt',
"""		#magic_ev2.71	#sleeps singularity - disabled
		magic_ev5.25	#xp lich system
		magic_ev9.1		#cult caravan conversion
""",
"""		#magic_ev2.71	#sleeps singularity - disabled
		#magic_ev5.25	#xp demon system
		spn_xp_sys.1000 #Supernaturals gain XP for their trait tracks
		magic_ev9.1		#cult caravan conversion
""")

# 2.39 B14 -- register: on_action_death_witch: supernatural_hunter (mod line 885)
E('common/on_action/yearly2_on_actions.txt',
"""						add_trait_xp = {
							trait = witch_hunter
							value = 60
""",
"""						add_trait_xp = {
							trait = supernatural_hunter
							track = witch_hunting
							value = 60
""")

# 2.39 B14 -- register: on_action_death_witch: supernatural_hunter (mod line 903)
E('common/on_action/yearly2_on_actions.txt',
"""						add_trait_xp = {
							trait = witch_hunter
							value = 30
""",
"""						add_trait_xp = {
							trait = supernatural_hunter
							track = witch_hunting
							value = 30
""")

# 2.39 B14 -- register: on_action_death_witch: supernatural_hunter (mod line 918)
E('common/on_action/yearly2_on_actions.txt',
"""						add_trait_xp = {
							trait = witch_hunter
							value = 20
""",
"""						add_trait_xp = {
							trait = supernatural_hunter
							track = witch_hunting
							value = 20
""")

# 2.39 B14 -- register: on_action_death_witch: supernatural_hunter (mod line 930)
E('common/on_action/yearly2_on_actions.txt',
"""						add_trait_xp = {
							trait = witch_hunter
							value = 10
""",
"""						add_trait_xp = {
							trait = supernatural_hunter
							track = witch_hunting
							value = 10
""")

# 2.39 B14 -- register: on_action_death_witch_hunter: supernatural_hunter (mod line 958)
E('common/on_action/yearly2_on_actions.txt',
"""		has_trait_xp = {
			trait = witch_hunter
			value > 99
""",
"""		has_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value > 99
""")

# 2.39 B14 -- register: corruption: SUPERNATURAL, spn_mark_menace_effect, spn_menace_marked_recently, 2.35 (mod line 572)
E('common/schemes/scheme_types/corruption_scheme.txt',
"""				limit = { exists = scope:scheme_successful }
				if = {
""",
"""				limit = { exists = scope:scheme_successful }
				# ==========================================================================================
				# SUPERNATURAL 2.35 PART TWO -- ADDED, one block, nothing below changed. (W-W3, order §3.2, §12.)
				#
				# A corruption succeeded: somebody's mind has been quietly turned in a county that has no
				# idea it happened. Nobody is dead, so this is a `prowl` -- the place is simply getting
				# stranger, and a hunter who knows what that feels like can come and look.
				#
				# The mark is on the OWNER, in the owner's county, because the owner is the one who did it.
				# ==========================================================================================
				if = {
					limit = {
						NOT = { has_character_flag = spn_menace_marked_recently }
						exists = location
						location = { exists = county }
					}
					spn_mark_menace_effect = {
						COUNTY = location.county
						CULPRIT = this
						KIND = witch
						SEVERITY = prowl
					}
				}
				if = {
""")

# 2.39 B14 -- register: corruption: supernatural_hunter (mod line 643)
E('common/schemes/scheme_types/corruption_scheme.txt',
"""							add_trait_xp = {
								trait = witch_hunter
								value = { 10 55 }
""",
"""							add_trait_xp = {
								trait = supernatural_hunter
								track = witch_hunting
								value = { 10 55 }
""")

# 2.39 B14 -- register: wh_attraction_value: supernatural_hunter (mod line 1447)
E('common/script_values/02_magic_values.txt',
"""					OR = {
						has_trait = witch_hunter2
						has_trait = grandmaster_coven
""",
"""					OR = {
						has_trait = supernatural_hunter
						has_trait = grandmaster_coven
""")

# 2.39 B14 -- register: wh_attraction_value: SUPERNATURAL, spn_hunt_witch_strength_value, 2.35 (mod line 1623)
E('common/script_values/02_magic_values.txt',
"""				add = -1
			}
		}
		else = {
""",
"""				add = -1
			}
			# ==================================================================================================
			# SUPERNATURAL 2.35 PART TWO -- ADDED, one term, nothing above changed. (Order §6.2, §12.)
			#
			# This value already reads everything Thomas asked a witch's "strength" to be made of -- magic
			# artifacts, black magic, a coven, open practice, an archmage's name, a tyrant's reputation. He
			# guessed the design that already existed. The single thing it did not read was raw magical
			# POTENTIAL, which is his "powerful source of energy": a witch can be quiet, own nothing, join
			# nothing, and still be the most dangerous person in the province.
			#
			# my_smp_value is has_trait_xp(source|magic_potential), 0-100, so this is 0 to 4 on a scale whose
			# other terms are ones and twos. Deliberately the largest single term available, and deliberately
			# the one that is hardest to hide.
			#
			# Supernatural also reads this value as the witch culprit's strength on the hunt
			# (spn_hunt_witch_strength_value), so the same number now decides how hard she is to find as well
			# as how likely anyone is to look.
			add = { value = my_smp_value divide = 25 }
		}
		else = {
""")

# 2.39 B14 -- register: astaroth_demon_character: supernatural_hunter (mod line 307)
E('common/scripted_character_templates/01_magic_character_templates.txt',
"""	trait = giant
	trait = witch_hunter
""",
"""	trait = giant
	trait = supernatural_hunter
	trait = witch_hunter
""")

# 2.39 B14 -- register: witch_hunter_character: supernatural_hunter (mod line 761)
E('common/scripted_character_templates/01_magic_character_templates.txt',
"""	}
	#trait = witch_hunter
""",
"""	}
	trait = supernatural_hunter
	#trait = witch_hunter
""")

# 2.39 B14 -- register: witch_hunter_knight_character: supernatural_hunter (mod line 786)
E('common/scripted_character_templates/01_magic_character_templates.txt',
"""	trait = holy_warrior
	trait = gallant
	trait = lifestyle_blademaster
""",
"""	trait = holy_warrior
	trait = supernatural_hunter
	trait = lifestyle_blademaster
""")

# 2.39 B14 -- register: psychic_surgery_spell_effect: supernatural_hunter (mod line 3104)
E('common/scripted_effects/00_magic_spells_effects.txt',
"""					remove_trait = witch_hunter
				}
				add_trait_force_tooltip = witch_hunter2
			}
			else_if = {
""",
"""					remove_trait = witch_hunter
				}
				add_trait_force_tooltip = supernatural_hunter   # was witch_hunter2 (retired witchcraft trait) -> unified supernatural_hunter
			}
			else_if = {
""")

# 2.39 B14 -- register: psychic_surgery_spell_effect: supernatural_hunter (mod line 3120)
E('common/scripted_effects/00_magic_spells_effects.txt',
"""					}
				}
				add_trait_force_tooltip = witch_hunter2
			}
			give_witch_secret_or_trait_effect2 = yes
""",
"""					}
				}
				add_trait_force_tooltip = supernatural_hunter   # was witch_hunter2 (retired witchcraft trait) -> unified supernatural_hunter
			}
			give_witch_secret_or_trait_effect2 = yes
""")

# 2.39 B14 -- register: turn_into_true_witch_effect: supernatural_hunter (mod line 2677)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""	if = {
		limit = {
			NOR = {
				has_trait = witch_hunter
				has_character_modifier = novice_witch_hunter_modifier
				has_trait = true_witch
""",
"""	if = {
		limit = {
			NOR = {
				has_trait = supernatural_hunter
				has_trait = witch_hunter
				has_character_modifier = novice_witch_hunter_modifier
				has_trait = true_witch
""")

# 2.39 B14 -- register: turn_into_mage_effect: supernatural_hunter (mod line 2784)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""		limit = {
			NOR = {
				has_trait = witch_hunter
				has_character_modifier = novice_witch_hunter_modifier
			}
""",
"""		limit = {
			NOR = {
				has_trait = supernatural_hunter
				has_character_modifier = novice_witch_hunter_modifier
			}
""")

# 2.39 B14 -- register: create_mage_effect: supernatural_hunter (mod line 3473)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""						has_trait = witch_hunter
						has_trait = archmage
""",
"""						has_trait = witch_hunter
						has_trait = supernatural_hunter
						has_trait = archmage
""")

# 2.39 B14 -- register: spawn_witch_hunter_full_chance_effect: SUPERNATURAL, spn_mark_menace_effect, spn_menace_marked_recently, 2.35 (mod line 4433)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""	$EMPL$ = { save_scope_as = empl }
	hidden_effect_new_object = {
""",
"""	$EMPL$ = { save_scope_as = empl }
	# ==========================================================================================================
	# SUPERNATURAL 2.35 PART TWO -- ADDED, one block at the top, nothing below changed. (W-W2, order §3.3, §12.)
	#
	# THE BRIDGE, in one place. Thomas: "I would get insta-arrested and then put on trial and then killed more
	# or less out of complete thin air, which is why I typically turn the W-Hunters off in the game rules."
	#
	# The spawn is deliberately LEFT ALONE this pass -- upstream's behaviour is upstream's. What is added is
	# the thing that was missing on the other side of it: a county that remembers. After this, casting a big
	# spell does what feeding does. It writes a mark, the lord notices at three, and a hunter can come and
	# LOOK -- which means the caster can see it coming, and can cover it up with the same five answers every
	# other creature in this mod gets.
	#
	# ONE BLOCK RATHER THAN TEN. The order's §12 lists this as ten separate hunks at the ten ungated call
	# sites in 00_magic_interactions.txt. Putting it in the shared effect instead is strictly narrower --
	# one added block instead of ten edits, in a file already on the permitted list -- it cannot miss a call
	# site, and it covers the ev10 callers too. Recorded in the session doc as a deliberate narrowing.
	#
	# SEVERITY is prowl here: nobody was found in an alley. The two spells that DO leave a body (consume_child
	# and plague_spell) write their own `kill` mark first, and the incident-dedupe flag that mark leaves is
	# what makes this one skip -- so a killing spell is one incident, not two.
	if = {
		limit = {
			scope:empl = {
				NOT = { has_character_flag = spn_menace_marked_recently }
				exists = location
				location = { exists = county }
			}
		}
		spn_mark_menace_effect = {
			COUNTY = scope:empl.location.county
			CULPRIT = scope:empl
			KIND = witch
			SEVERITY = prowl
		}
	}
	hidden_effect_new_object = {
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in give_witch_secret_or_trait_effect2 (mod line 9757)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""	if = {
		limit = {
			NOR = {
				has_trait = witch
""",
"""	if = {
		limit = {
			# 2.31c -- THE GATE BELONGS HERE, NOT ONLY ON THE INTERACTIONS.
			# This effect is the single door to becoming a witch and it is called from about a hundred
			# places. The interaction callers were all gated; the AI ones were not -- the place-of-power
			# sweep (turn_place_of_power_owner_into_witch_effect), the magic casus belli
			# (01_magic_cb.txt) and the court-position hook (01_court_positions_magic.txt) all walked
			# straight past. In a playset with the AGOT compatibility patch that meant the AI could make
			# a wight a witch. Gating the write instead of the decision closes every caller at once.
			#
			# COSTS NOTHING ON ITS OWN: Supernatural ships spn_is_valid_supernatural_target as
			# `always = yes`. Only the AGOT patch gives it teeth, and only where the patch is loaded.
			spn_is_valid_supernatural_target = yes

			NOR = {
				has_trait = witch
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in turn_place_of_power_owner_into_witch_effect (mod line 11799)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				has_power_place_trigger = yes
				is_witch_trigger = no
			}
		}
""",
"""				has_power_place_trigger = yes
				is_witch_trigger = no
				# 2.31c -- the write below is already gated, but without this the sweep can spend its one
				# pick a year on someone it will then refuse, and nothing happens that year.
				spn_is_valid_supernatural_target = yes
			}
		}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in turn_place_of_power_owner_into_witch_effect (mod line 11809)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				has_power_place_trigger = yes
				is_witch_trigger = no
			}
			give_witch_secret_or_trait_effect2 = yes
""",
"""				has_power_place_trigger = yes
				is_witch_trigger = no
				spn_is_valid_supernatural_target = yes
			}
			give_witch_secret_or_trait_effect2 = yes
""")

# 2.39 B14 -- register: demon_escapes_effect: SUPERNATURAL, spn_mark_menace_effect, 2.35 (mod line 12197)
E('common/scripted_effects/00_variety_magic_effects.txt',
"""				target_character = scope:this0
			}
		}
	}
}
""",
"""				target_character = scope:this0
			}
		}
		# ==================================================================================================
		# SUPERNATURAL 2.35 PART TWO -- ADDED, one call, nothing above changed. (D-W1, order §3.2, §12.)
		#
		# This is the canonical "a demon is loose in the world" path and it was already shaped like a loose
		# monster: it gives the escapee a landless adventurer title, a nemesis relation and a murder scheme
		# against the man who let it out. Everything except a county that remembers -- which is now the one
		# thing the Supernatural hunt needs in order to be able to come and look for it.
		#
		# The mark goes on the SUMMONER's county, because that is where it happened and where the bodies
		# will be. Guarded so it cannot fire without a county to write on.
		# ==================================================================================================
		if = {
			limit = {
				exists = scope:demon
				exists = scope:this0
				scope:this0 = { exists = location }
				scope:this0.location = { exists = county }
			}
			spn_mark_menace_effect = {
				COUNTY = scope:this0.location.county
				CULPRIT = scope:demon
				KIND = demon
				SEVERITY = kill
			}
		}
	}
}
""")

# 2.39 B14 -- register: age_ranked_health_vulnerability_threshold_trigger: supernatural_hunter, supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 45)
E('common/scripted_triggers/20_health_overwritten_triggers.txt',
"""		}
		is_a_demon_trigger = yes
""",
"""		}
		has_trait = supernatural_vampire
		has_trait = supernatural_werewolf
		has_trait = supernatural_hybrid
		has_trait = supernatural_hunter
		is_a_demon_trigger = yes
""")

# 2.39 B14 -- register: immune_to_epidemic: supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 75)
E('common/scripted_triggers/20_health_overwritten_triggers.txt',
"""		has_trait = golem
	}
""",
"""		has_trait = golem
		has_trait = supernatural_vampire
		has_trait = supernatural_werewolf
		has_trait = supernatural_hybrid
	}
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in can_be_cursed_trigger (mod line 2)
E('common/scripted_triggers/magic_triggers.txt',
"""can_be_cursed_trigger = {
	NOR = {
""",
"""can_be_cursed_trigger = {
	# 2.31c -- magic_ev2.61 lets an AI court mage choose its own victim from its liege's rivals and
	# nemeses, and the powerful-curse branch writes add_trait = immortal2 onto them. This is the one
	# curse that picks a target without a player clicking a gated interaction.
	spn_is_valid_supernatural_target = yes

	NOR = {
""")

# 2.39 B14 -- register: has_basic_magic_prot_trigger: supernatural_hunter (mod line 110)
E('common/scripted_triggers/magic_triggers.txt',
"""has_basic_magic_prot_trigger = {
	OR = {
		has_perk = protective_runes_perk
		has_perk = mage_tower_p2_perk
		is_a_demon_trigger = yes
		has_trait = golem
		has_trait = witch_hunter
		has_character_modifier = aura_boost1_modifier
		has_character_modifier = aura_boost2_modifier
		any_equipped_character_artifact = {	has_variable = magic_ring	}
		AND = {
			any_parent = { has_perk = protective_runes_perk }
			NOT = { is_child_of = scope:actor }
""",
"""has_basic_magic_prot_trigger = {
	OR = {
		has_perk = protective_runes_perk
		has_perk = mage_tower_p2_perk
		is_a_demon_trigger = yes
		has_trait = golem
		has_trait = supernatural_hunter
		has_character_modifier = aura_boost1_modifier
		has_character_modifier = aura_boost2_modifier
		any_equipped_character_artifact = {	has_variable = magic_ring	}
		AND = {
			any_parent = { has_perk = protective_runes_perk }
			NOT = { is_child_of = scope:actor }
""")

# 2.39 B14 -- register: has_basic_magic_prot_trigger2: supernatural_hunter (mod line 150)
E('common/scripted_triggers/magic_triggers.txt',
"""has_basic_magic_prot_trigger2 = {
	OR = {
		has_perk = protective_runes_perk
		has_perk = mage_tower_p2_perk
		is_a_demon_trigger = yes
		has_trait = golem
		has_trait = witch_hunter
		has_character_modifier = aura_boost1_modifier
		has_character_modifier = aura_boost2_modifier
		any_equipped_character_artifact = {	has_variable = magic_ring	}
		AND = {
			any_parent = { has_perk = protective_runes_perk }
			NOT = { is_child_of = scope:owner }
""",
"""has_basic_magic_prot_trigger2 = {
	OR = {
		has_perk = protective_runes_perk
		has_perk = mage_tower_p2_perk
		is_a_demon_trigger = yes
		has_trait = golem
		has_trait = supernatural_hunter
		has_character_modifier = aura_boost1_modifier
		has_character_modifier = aura_boost2_modifier
		any_equipped_character_artifact = {	has_variable = magic_ring	}
		AND = {
			any_parent = { has_perk = protective_runes_perk }
			NOT = { is_child_of = scope:owner }
""")

# 2.39 B14 -- register: has_any_basic_magic_prot_trigger: supernatural_hunter (mod line 192)
E('common/scripted_triggers/magic_triggers.txt',
"""		has_perk = protective_runes_perk
		has_perk = mage_tower_p2_perk
		is_a_demon_trigger = yes
		has_trait = golem
		has_trait = witch_hunter
		has_character_modifier = aura_boost1_modifier
		has_character_modifier = aura_boost2_modifier
		any_equipped_character_artifact = {	has_variable = magic_ring	}
		any_parent = { has_perk = protective_runes_perk }
""",
"""		has_perk = protective_runes_perk
		has_perk = mage_tower_p2_perk
		is_a_demon_trigger = yes
		has_trait = golem
		has_trait = supernatural_hunter
		has_character_modifier = aura_boost1_modifier
		has_character_modifier = aura_boost2_modifier
		any_equipped_character_artifact = {	has_variable = magic_ring	}
		any_parent = { has_perk = protective_runes_perk }
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in has_immunity_for_regular_curse (mod line 1110)
E('common/scripted_triggers/magic_triggers.txt',
"""has_immunity_for_regular_curse = {
	OR = {
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_curse_terrain_cancel_negative_supply
""",
"""has_immunity_for_regular_curse = {
	OR = {
		# SPECIES GATE -- see common/scripted_triggers/zz_spn_species_triggers.txt. Whatever is not a
		# person is immune to everything, so every consumer of this family -- interactions, events and
		# task contracts alike -- inherits the answer without being edited one at a time.
		spn_is_valid_supernatural_target = no
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_curse_terrain_cancel_negative_supply
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in has_immunity_for_powerful_curse (mod line 1128)
E('common/scripted_triggers/magic_triggers.txt',
"""has_immunity_for_powerful_curse = {
	OR = {
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_curse2_terrain_cancel_negative_supply
""",
"""has_immunity_for_powerful_curse = {
	OR = {
		# SPECIES GATE -- see common/scripted_triggers/zz_spn_species_triggers.txt. Whatever is not a
		# person is immune to everything, so every consumer of this family -- interactions, events and
		# task contracts alike -- inherits the answer without being edited one at a time.
		spn_is_valid_supernatural_target = no
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_curse2_terrain_cancel_negative_supply
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in has_immunity_for_magic_domination (mod line 1146)
E('common/scripted_triggers/magic_triggers.txt',
"""has_immunity_for_magic_domination = {
	OR = {
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_domination_terrain_cancel_negative_supply
""",
"""has_immunity_for_magic_domination = {
	OR = {
		# SPECIES GATE -- see common/scripted_triggers/zz_spn_species_triggers.txt. Whatever is not a
		# person is immune to everything, so every consumer of this family -- interactions, events and
		# task contracts alike -- inherits the answer without being edited one at a time.
		spn_is_valid_supernatural_target = no
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_domination_terrain_cancel_negative_supply
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in has_immunity_for_mind_scan (mod line 1163)
E('common/scripted_triggers/magic_triggers.txt',
"""has_immunity_for_mind_scan = {
	OR = {
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_mind_scan_terrain_cancel_negative_supply
""",
"""has_immunity_for_mind_scan = {
	OR = {
		# SPECIES GATE -- see common/scripted_triggers/zz_spn_species_triggers.txt. Whatever is not a
		# person is immune to everything, so every consumer of this family -- interactions, events and
		# task contracts alike -- inherits the answer without being edited one at a time.
		spn_is_valid_supernatural_target = no
		any_equipped_character_artifact = {
			has_artifact_modifier = immunity_mind_scan_terrain_cancel_negative_supply
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in has_immunity_for_death_wish (mod line 1179)
E('common/scripted_triggers/magic_triggers.txt',
"""has_immunity_for_death_wish = {
	OR = {
		is_antimagic_trigger = yes
		has_character_modifier = master_defence_modifier
""",
"""has_immunity_for_death_wish = {
	OR = {
		# SPECIES GATE -- see common/scripted_triggers/zz_spn_species_triggers.txt. Whatever is not a
		# person is immune to everything, so every consumer of this family -- interactions, events and
		# task contracts alike -- inherits the answer without being edited one at a time.
		spn_is_valid_supernatural_target = no
		is_antimagic_trigger = yes
		has_character_modifier = master_defence_modifier
""")

# 2.39 B14 -- register: the 2.31c species gate (spn_is_valid_supernatural_target) in has_immunity_for_antimagic_seal (mod line 1190)
E('common/scripted_triggers/magic_triggers.txt',
"""has_immunity_for_antimagic_seal = {
	OR = {
		is_antimagic_trigger = yes
		has_perk = magical_creature_perk
""",
"""has_immunity_for_antimagic_seal = {
	OR = {
		# SPECIES GATE -- see common/scripted_triggers/zz_spn_species_triggers.txt. Whatever is not a
		# person is immune to everything, so every consumer of this family -- interactions, events and
		# task contracts alike -- inherits the answer without being edited one at a time.
		spn_is_valid_supernatural_target = no
		is_antimagic_trigger = yes
		has_perk = magical_creature_perk
""")

# 2.39 B14 -- register: is_witch_hunter: supernatural_hunter (mod line 1258)
E('common/scripted_triggers/magic_triggers.txt',
"""		has_trait = witch_hunter
		any_secret = {
""",
"""		has_trait = witch_hunter
		has_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value > 25
		}
		any_secret = {
""")

# 2.39 B14 -- register: secret_witch_hunter: supernatural_hunter (mod line 104)
E('common/secret_types/01_magic_secret_types.txt',
"""				has_trait = witch_hunter
				has_trait = witch_hunter2
			}
""",
"""				has_trait = witch_hunter
				has_trait = supernatural_hunter
			}
""")

# 2.39 B14 -- register: laamp_magic_1008: supernatural_hunter (mod line 1582)
E('common/task_contracts/laamp_magic_contracts.txt',
"""				has_trait = witch_hunter
				has_trait = witch_hunter2
			}
""",
"""				has_trait = witch_hunter
				has_trait = supernatural_hunter	#witch_hunter2
			}
""")

# 2.39 B14 -- register: demon0: supernatural_hunter, supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 372)
E('common/traits/00_traits_magic.txt',
"""	}
	desc = trait_demon0_desc
""",
"""	}
	opposites = {
		supernatural_hybrid
		supernatural_werewolf
		supernatural_vampire
		#supernatural_hunter
		witch_hunter
	}
	desc = trait_demon0_desc
""")

# 2.39 B14 -- register: demon1: supernatural_hunter, supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 424)
E('common/traits/00_traits_magic.txt',
"""	ai_boldness = 50
	compatibility = {
		witch = 10
		true_witch = 10
		witch_hunter = -30
	}
	desc = trait_demon_desc
	flag = is_immortal
}

""",
"""	ai_boldness = 50
	compatibility = {
		witch = 10
		true_witch = 10
		witch_hunter = -30
	}
	opposites = {
		supernatural_hybrid
		supernatural_werewolf
		supernatural_vampire
		#supernatural_hunter
		witch_hunter
	}
	desc = trait_demon_desc
	flag = is_immortal
}

""")

# 2.39 B14 -- register: demon2: supernatural_hunter, supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 605)
E('common/traits/00_traits_magic.txt',
"""	compatibility = {
		witch = 10
		true_witch = 10
		witch_hunter = -30
	}
	desc = trait_demon_desc
	flag = is_immortal
}

true_witch = {
""",
"""	compatibility = {
		witch = 10
		true_witch = 10
		witch_hunter = -30
	}
	opposites = {
		supernatural_hybrid
		supernatural_werewolf
		supernatural_vampire
		#supernatural_hunter
		witch_hunter
	}
	desc = trait_demon_desc
	flag = is_immortal
}

true_witch = {
""")

# 2.39 B14 -- register: true_witch: supernatural_hunter (mod line 654)
E('common/traits/00_traits_magic.txt',
"""		demon2 = 10
	}
	opposites = {
		witch_hunter
	}
}
""",
"""		demon2 = 10
	}
	opposites = {
		supernatural_hunter
		witch_hunter
	}
}
""")

# 2.39 B14 -- register: yaga: supernatural_hunter, supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 700)
E('common/traits/00_traits_magic.txt',
"""	}
	flag = is_immortal
}
""",
"""	}
	flag = is_immortal	
	opposites = {
		supernatural_hunter
		supernatural_hybrid
		supernatural_vampire
		supernatural_werewolf
	}
}
""")

# 2.39 B14 -- register: necromancer: supernatural_hunter, supernatural_vampire (mod line 1213)
E('common/traits/00_traits_magic.txt',
"""	compatibility = {
		true_witch = 10
		demon1 = 10
		demon2 = 10
		witch_hunter = -50
	}
	opposites = {
		witch_hunter
""",
"""	compatibility = {
		supernatural_vampire = 5
		true_witch = 10
		demon1 = 10
		demon2 = 10
		supernatural_hunter = -50
		witch_hunter = -50
	}
	opposites = {
		supernatural_hunter
		witch_hunter
""")

# 2.39 B14 -- register: warlock: supernatural_hunter (mod line 1284)
E('common/traits/00_traits_magic.txt',
"""	}
	flag = is_immortal
	#opposites = {
	#	witch_hunter
	#	incapable
	#	cancer
	#	ill
	#	measles
	#	maimed
	#	infertile
	#	infirm
	#	lovers_pox
	#	gout_ridden
	#	consumption
	#	typhus
	#	bubonic_plague
	#	smallpox
	#	dysentery
	#	ergotism
	#	disfigured
	#	measles
	#}
}
""",
"""	}
	
	opposites = {
		supernatural_hunter
		witch_hunter
		incapable
	}
}
""")

# 2.39 B14 -- register: golem: supernatural_hybrid, supernatural_vampire, supernatural_werewolf (mod line 1325)
E('common/traits/00_traits_magic.txt',
"""	#	disfigured
	#	measles
	#}
}
immortal1 = {
""",
"""	#	disfigured
	#	measles
		supernatural_vampire
		supernatural_werewolf
		supernatural_hybrid
		demon0
		demon1
		warlock
		necromancer
	}
}
immortal1 = {
""")

# 2.39 B14 -- register: magic_ev.99: 2.30 (mod line 19)
E('events/ev1.txt',
"""	immediate = {
		random_living_character = {
			limit = {
				is_ai = no
			}
			save_scope_as = player0
""",
"""	immediate = {
		# 2.30 bugfix: was random_living_character (every living character scanned, every pulse) and
		# in observer mode it found nobody, leaving scope:player0 unset -- 14,000+ errors in one
		# evening's log. random_player is the same characters, without the scan.
		random_player = {
			save_scope_as = player0
""")

# 2.39 B14 -- register: magic_ev.2: supernatural_hunter (mod line 912)
E('events/ev1.txt',
"""								has_trait = witch_hunter
								any_secret = { type = secret_witch }
""",
"""								has_trait = witch_hunter
								has_trait = supernatural_hunter
								any_secret = { type = secret_witch }
""")

# 2.39 B14 -- register: magic_ev.4: supernatural_hunter (mod line 1359)
E('events/ev1.txt',
"""		add_trait_xp = {
			trait = witch_hunter
			value = 5
""",
"""		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 5
""")

# 2.39 B14 -- register: magic_ev.44: supernatural_hunter (mod line 1637)
E('events/ev1.txt',
"""	#		NOT = {
	#			has_trait = witch_hunter
	#		}
""",
"""	#		NOT = {
	#			has_trait = supernatural_hunter
	#		}
""")

# 2.39 B14 -- register: magic_ev10.116: SUPERNATURAL, spn_mark_menace_effect, 2.35 (mod line 24427)
E('events/ev10.txt',
"""		else = {
			add_prestige = -100
		}
	}
	option = {
		name = ev10.83.c
""",
"""		else = {
			add_prestige = -100
		}
		# ==================================================================================================
		# SUPERNATURAL 2.35 PART TWO -- ADDED, one block, nothing above changed. (D-W2, order §3.2, §12.)
		#
		# A demon destroyed a village. That is the most legible thing a demon does to a county in the entire
		# Witchcraft layer and until now it left no trace anybody could follow: development fell, the lord
		# lost legitimacy, and nothing in the world knew WHY or WHO.
		#
		# scope:tprov is the county (saved at ev10.txt:24280) and scope:demon1 is what did it. The chain's
		# second half, magic_ev10.117, is the same night and takes no second mark -- the incident-dedupe flag
		# this leaves on the demon is what guarantees that.
		# ==================================================================================================
		if = {
			limit = {
				exists = scope:demon1
				exists = scope:tprov
			}
			spn_mark_menace_effect = {
				COUNTY = scope:tprov
				CULPRIT = scope:demon1
				KIND = demon
				SEVERITY = kill
			}
		}
	}
	option = {
		name = ev10.83.c
""")

# 2.39 B14 -- register: magic_ev10.119: SUPERNATURAL, spn_mark_menace_effect, spn_menace_marked_recently, 2.35 (mod line 24607)
E('events/ev10.txt',
"""		name = ev10.119.a
		if = {
""",
"""		name = ev10.119.a
		# SUPERNATURAL 2.35 PART TWO -- ADDED, one block, nothing below changed. (D-W4, order §3.2, §12.)
		# A demonic courtier has been at work in the county it lives in. Nobody has been found in an alley,
		# so this is a `prowl`: the place is quietly getting worse and the lord can see it in his own numbers
		# before anybody can tell him why.
		if = {
			limit = {
				exists = scope:demon1
				exists = location
				location = { exists = county }
				scope:demon1 = { NOT = { has_character_flag = spn_menace_marked_recently } }
			}
			spn_mark_menace_effect = {
				COUNTY = location.county
				CULPRIT = scope:demon1
				KIND = demon
				SEVERITY = prowl
			}
		}
		if = {
""")

# 2.39 B14 -- register: magic_ev10.134: supernatural_hybrid, supernatural_vampire (mod line 25656)
E('events/ev10.txt',
"""		di_astaroth_setup = yes
		stress_impact = {
			craven = major_stress_gain
		}
""",
"""		di_astaroth_setup = yes
		stress_and_fulfillment_impact = { craven = major_stress_gain }
	}

	option = { name = ev10.134.a }  # I'll grab my sword!
	option = { name = ev10.134.b }  # Quickly, to the window!

	# NEW — Vampiric escape (needs some vampirism XP)
	option = {
		name = ev10.134.vamp_escape
		trigger = {
			OR = {
				has_trait = supernatural_vampire
				has_trait = supernatural_hybrid
			}
			OR = {
				has_trait_xp = { trait = supernatural_vampire track = vampirism value > 30 }
				has_trait_xp = { trait = supernatural_hybrid  track = hybrid_vampirism value > 30 }
			}
		}
		custom_tooltip = ev10.134.vamp_escape_tt
		add_character_flag = escaped_astaroth
		trigger_event = { id = magic_ev10.1344 }  # block form is safest
		ai_chance = {
			base = 40
			modifier = { add = 10 has_trait = shrewd }
			modifier = { add = -15 has_trait = brave }
		}
""")

# 2.39 B14 -- register: magic_ev10.134: supernatural_werewolf (mod line 25687)
E('events/ev10.txt',
"""	option = {
		name = ev10.134.a
	}
""",
"""	option = {
		name = ev10.134.wolf_escape
		trigger = {
			has_trait = supernatural_werewolf
			has_trait_xp = { trait = supernatural_werewolf track = lycanthropy value > 30 }
		}
		custom_tooltip = ev10.134.wolf_escape_tt
		add_character_flag = escaped_astaroth
		trigger_event = { id = magic_ev10.1344 }  # block form is safest
		ai_chance = {
			base = 35
			modifier = { add = 20 has_trait = athletic }   # if you use it; otherwise omit
			modifier = { add = 10 prowess > 12 }
			modifier = { add = -10 has_trait = stubborn }
		}
	}
""")

# 2.39 B14 -- register: magic_ev10.134: supernatural_hunter (mod line 25705)
E('events/ev10.txt',
"""	option = {
		name = ev10.134.b
	}
""",
"""	option = {
		name = ev10.134.hunter_escape
		trigger = {
			has_trait = supernatural_hunter
			OR = {
				has_trait_xp = { trait = supernatural_hunter track = monster_hunting value > 30 }
				has_trait_xp = { trait = supernatural_hunter track = witch_hunting   value > 30 }
				prowess > 14
			}
		}
		custom_tooltip = ev10.134.hunter_escape_tt
		add_character_flag = escaped_astaroth
		trigger_event = { id = magic_ev10.1344 }  # block form is safest
		ai_chance = {
			base = 30
			modifier = { add = 15 has_trait = shrewd }
			modifier = { add = 10 prowess > 14 }
			modifier = { add = -10 has_trait = reckless }
		}
	}
""")

# 2.39 B14 -- register: magic_ev2.5: supernatural_hunter (mod line 1348)
E('events/ev2.txt',
"""		NOT = {	has_character_flag = special_magic_character	}
		NOT = { has_trait = witch_hunter }
		OR = {
""",
"""		NOT = {	has_character_flag = special_magic_character	}
		NOT = { has_trait = supernatural_hunter }
		OR = {
""")

# 2.39 B14 -- register: magic_ev2.16: supernatural_hunter (mod line 2911)
E('events/ev2.txt',
"""		create_witch_hunter2_amulet_artifact_effect = yes
		add_trait_xp = {
			trait = witch_hunter
			value = 90
		}
		#random_list = {
""",
"""		create_witch_hunter2_amulet_artifact_effect = yes
				add_trait_xp = {
					trait = supernatural_hunter
					track = witch_hunting
					value = 90
				}

		#random_list = {
""")

# 2.39 B14 -- register: magic_ev2.16: supernatural_hunter (mod line 3015)
E('events/ev2.txt',
"""			add_trait_xp = {
				trait = witch_hunter
				value = 10
""",
"""			add_trait_xp = {
				trait = supernatural_hunter
				track = witch_hunting
				value = 10
""")

# 2.39 B14 -- register: magic_ev2.24: supernatural_hunter (mod line 4380)
E('events/ev2.txt',
"""					add_trait_xp = {
						trait = witch_hunter
						value = 70
""",
"""					add_trait_xp = {
						trait = supernatural_hunter
						track = witch_hunting
						value = 70
""")

# 2.39 B14 -- register: magic_ev2.77: supernatural_hunter (mod line 8667)
E('events/ev2.txt',
"""						is_a_demon_trigger = yes
						has_trait = witch_hunter
						#has_trait = zealous
""",
"""						is_a_demon_trigger = yes
						has_trait = supernatural_hunter
						#has_trait = zealous
""")

# 2.39 B14 -- register: magic_ev2.83: 2.32 (mod line 9088)
E('events/ev2.txt',
"""		
		#debug unstable source?
		#random_living_character = {
""",
"""		
		# 2.32 -- DEBUG SCAFFOLDING, was LIVE and firing every pulse in the shipped mod.
		# Upstream Witchcraft has this block commented out; the live version is our own
		# divergence and almost certainly unintentional -- it walked every living character
		# each pulse and silently wiped source instability off one of them, quietly undoing
		# the mechanic it belongs to. Restored to upstream's state.
		#random_living_character = {
""")

# 2.39 B14 -- register: magic_ev3.341: supernatural_hunter (mod line 4316)
E('events/ev3.txt',
"""					add_trait_xp = {
						trait = witch_hunter
						value = 80
""",
"""					add_trait_xp = {
						trait = supernatural_hunter
						track = witch_hunting
						value = 80
""")

# 2.39 B14 -- register: magic_ev3.64: supernatural_hunter (mod line 6817)
E('events/ev3.txt',
"""					has_trait_xp = {
						trait = witch_hunter
						value < 90
""",
"""					has_trait_xp = {
						trait = supernatural_hunter
						track = witch_hunting
						value < 90
""")

# 2.39 B14 -- register: magic_ev3.64: supernatural_hunter (mod line 6864)
E('events/ev3.txt',
"""			add_trait_xp = {
				trait = witch_hunter
				value = 5
""",
"""			add_trait_xp = {
				trait = supernatural_hunter
				track = witch_hunting
				value = 5
""")

# 2.39 B14 -- register: magic_ev4.1: supernatural_hunter (mod line 15)
E('events/ev4.txt',
"""	trigger = {
		has_trait = witch_hunter
		has_trait_xp = {
			trait = witch_hunter
			value > 4
""",
"""	trigger = {
		has_trait = supernatural_hunter
		has_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value > 4
""")

# 2.39 B14 -- register: magic_ev4.1: supernatural_hunter (mod line 35)
E('events/ev4.txt',
"""				add_trait_xp = {
					trait = witch_hunter
					value = 70
""",
"""				add_trait_xp = {
					trait = supernatural_hunter
					track = witch_hunting
					value = 70
""")

# 2.39 B14 -- register: magic_ev4.2: supernatural_hunter (mod line 245)
E('events/ev4.txt',
"""						add_trait_xp = {
							trait = witch_hunter
							value = 10
""",
"""						add_trait_xp = {
							trait = supernatural_hunter
							track = witch_hunting
							value = 10
""")

# 2.39 B14 -- register: magic_ev4.5: supernatural_hunter (mod line 582)
E('events/ev4.txt',
"""					add_trait_xp = {
						trait = witch_hunter
						value = 5
""",
"""					add_trait_xp = {
						trait = supernatural_hunter
						track = witch_hunting
						value = 5
""")

# 2.39 B14 -- register: magic_ev4.6: supernatural_hunter (mod line 697)
E('events/ev4.txt',
"""				add_trait_xp = {
					trait = witch_hunter
					value = 5
""",
"""				add_trait_xp = {
					trait = supernatural_hunter
					track = witch_hunting
					value = 5
""")

# 2.39 B14 -- register: magic_ev4.9: supernatural_hunter (mod line 996)
E('events/ev4.txt',
"""
	immediate = {
		add_trait_xp = {
			trait = witch_hunter
			value = 10
		}
		random_secret = {
""",
"""
	immediate = {
		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 10
		}
		random_secret = {
""")

# 2.39 B14 -- register: magic_ev4.12: supernatural_hunter (mod line 1458)
E('events/ev4.txt',
"""		#enough
		name = ev4.12.0.a
		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = witch_hunter
			value = 5
		}
	}
	after = {
""",
"""		#enough
		name = ev4.12.0.a
		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 5
		}
	}
	after = {
""")

# 2.39 B14 -- register: magic_ev4.25: supernatural_hunter (mod line 2670)
E('events/ev4.txt',
"""	}
	immediate = {
		add_trait_xp = {
			trait = witch_hunter
			value = 10
		}
	}
""",
"""	}
	immediate = {
		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 10
		}
	}
""")

# 2.39 B14 -- register: magic_ev4.31: supernatural_hunter (mod line 3131)
E('events/ev4.txt',
"""		custom_tooltip = ev4.31.0.d
		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = witch_hunter
			value = 5
		}
		cp:councillor_spymaster = {
""",
"""		custom_tooltip = ev4.31.0.d
		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 5
		}
		cp:councillor_spymaster = {
""")

# 2.39 B14 -- register: magic_ev4.32: supernatural_hunter (mod line 3188)
E('events/ev4.txt',
"""		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = witch_hunter
			value = 10
		}
""",
"""		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 10
		}
""")

# 2.39 B14 -- register: magic_ev4.39: supernatural_hunter (mod line 3931)
E('events/ev4.txt',
"""		#enough
		name = ev4.12.0.a
		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = witch_hunter
			value = 5
		}
	}
}
""",
"""		#enough
		name = ev4.12.0.a
		custom_tooltip = ev4.5.0.a_ct
		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 5
		}
	}
}
""")

# 2.39 B14 -- register: magic_ev7.19: supernatural_hunter (mod line 3314)
E('events/ev7.txt',
"""				#	limit = {
				#		has_trait = witch_hunter
				#	}
				#	remove_trait = witch_hunter
				#}
""",
"""				#	limit = {
				#		has_trait = supernatural_hunter
				#	}
				#	remove_trait = supernatural_hunter
				#}
""")

# 2.39 B14 -- register: magic_ev8.4: supernatural_hunter (mod line 728)
E('events/ev8.txt',
"""		add_trait_xp = {
			trait = witch_hunter
			value = 10
""",
"""		add_trait_xp = {
			trait = supernatural_hunter
			track = witch_hunting
			value = 10
""")

# 2.39 B14 -- register: magic_ev8.18: 2.32 (mod line 1326)
E('events/ev8.txt',
"""				OR = {
					has_trait = depressed
					has_trait = depressed_1
""",
"""				OR = {
					# 2.32 -- `depressed` is not a trait (the real ones are depressed_1 and
					# depressed_genetic, both already listed below). Dead OR arm, removed.
					has_trait = depressed_1
""")

# 2.39 B14 -- register: magic_ev9.41: supernatural_hunter (mod line 3489)
E('events/ev9.txt',
"""		scope:employer = {
			add_trait = witch_hunter
			hidden_effect = {
				add_trait_xp = {
					trait = witch_hunter
					value = 80
				}
""",
"""		scope:employer = {
			add_trait = supernatural_hunter
			hidden_effect = {
				add_trait_xp = {
					trait = supernatural_hunter
					track = witch_hunting
					value = 40
				}
""")

# 2.39 B14 -- register: trait_witch_hunter2: supernatural_hunter (mod line 5)
E('localization/english/event_localization/witch_ep7_l_english.yml',
""" ev8.1.0.c:0 "I'd better get on with something else."
 trait_witch_hunter2:0 "Fallen Witch Hunter"
 trait_witch_hunter2_desc:0 "This witch hunter abandoned his mission, seduced by power and a thirst for knowledge, became like those he once fought."
 wh2_eso_terrain_cancel_negative_supply:0 "$witchcraft_legacy_2_ct$"
 court_position_witch_hunter2_trait:0 "[GetTrait('witch_hunter2').GetName( ROOT.Char )]"
 trait_source_0:0 "Spark of Talent"
""",
""" ev8.1.0.c:0 "I'd better get on with something else."
#trait_witch_hunter2:0 "Fallen Witch Hunter"          # trait retired -> supernatural_hunter; loc key kept commented for reference
#trait_witch_hunter2_desc:0 "This witch hunter abandoned their mission, seduced by power and a thirst for knowledge, ultimately becoming like those they once hunted."
 wh2_eso_terrain_cancel_negative_supply:0 "$witchcraft_legacy_2_ct$"
 court_position_witch_hunter2_trait:0 "[GetTrait('supernatural_hunter').GetName( ROOT.Char )]"
 trait_source_0:0 "Spark of Talent"
""")

# 2.39 B14 -- register: ultimate_spell_blackgrimoire: 2.32 (mod line 639)
E('localization/english/event_localization/witch_ep8_l_english.yml',
' ultimate_spell_hecate_modifier:0 "$hecate_support_modifier$"',
""" ultimate_spell_hecate_modifier:0 "$hecate_support_modifier$"
# 2.32 -- the code asks for these WITHOUT the _modifier suffix
 ultimate_spell_blackgrimoire:0 "$blackgrimoire$"
 ultimate_spell_catalyst:0 "$magic_catalyst$"
""")


# =====================================================================================================================
# 2.39 (Supernatural) -- package P1 (WORK-ORDER-2.39)
# =====================================================================================================================
# 2.39 B2 -- the Mage capstone prints its one-path warning, as the Warlock (warlock_perk_tt) and the True Witch
# (true_witch_perk_tt) already do. No `if` wrapper: can_be_picked already refuses the other two paths, so the warning can
# always show. Rides after entry 137 (the Mage's memory), whose own text ends on the `#custom_tooltip = mage_p4_perk_ctt` line.
E("common/lifestyle_perks/00_magic_1_arcane_tree_perks.txt",
"""		#custom_tooltip = mage_p4_perk_ctt
		#custom_tooltip = mtriangulation_discount_ct
""",
"""		#custom_tooltip = mage_p4_perk_ctt
		custom_tooltip = archmage_perk_tt # 2.39 (Supernatural): one path only (WORK-ORDER-2.39 B2)
		#custom_tooltip = mtriangulation_discount_ct
""")

# 2.39 B3 B (28b) -- the yearly Council Invitation (magic_ev10.65) arrives up to a year after it was sent; never to one
# who has been seated since (or made Grand Magus, who carries mc_member_var too). Rides after E28; E28 itself is unchanged,
# and the new line goes AFTER E28's text so E28 still reads as "already present" on every later run.
E("events/ev10.txt",
"""		spn_order_council_member_ok_trigger = yes # 2.38b (Supernatural): the council is the Order's (DESIGN-2.38b §3)
		exists = global_var:current_archmage_global
		OR = {
""",
"""		spn_order_council_member_ok_trigger = yes # 2.38b (Supernatural): the council is the Order's (DESIGN-2.38b §3)
		exists = global_var:current_archmage_global
		NOT = { has_variable = mc_member_var } # 2.39 (Supernatural): not one who already sits (WORK-ORDER-2.39 B3 B)
		OR = {
""")

# 2.39 B3 C -- the secret meeting needs four different people: a man in two seats loops it for ever. The decision refuses
# to start with a duplicate (spn_council_seats_distinct_trigger, zz_spn_council_triggers.txt).
E("common/decisions/magic_dec.txt",
"""		is_imprisoned = no
		custom_description = {
			text = mc_has_free_slots""",
"""		is_imprisoned = no
		custom_description = { # 2.39 (Supernatural): four seats, four people (WORK-ORDER-2.39 B3 C)
			text = spn_council_seats_distinct_tt
			spn_council_seats_distinct_trigger = yes
		}
		custom_description = {
			text = mc_has_free_slots""")

# 2.39 B3 C -- and a meeting already looping (a 2.38 save) ends at its next turn. The only thing that frees a stuck save:
# the loop runs on the scopes saved when the meeting began, so emptying a seat cannot stop it.
E("events/ev10.txt",
"""magic_ev10.81 = {
	title = ev10.81.title
""",
"""magic_ev10.81 = {
	title = ev10.81.title
	trigger = { spn_council_meeting_roles_distinct_trigger = yes } # 2.39 (Supernatural): four people, or the meeting ends (WORK-ORDER-2.39 B3 C)
""")

# 2.39 B3 E -- Witchcraft's own gap in the Summit's "Council of Mages" (magic_ev7.105): a speaker who is not on the
# council and chose one of the Order's two Summit intents (E9/E10) can be left with no option. A fallback option is
# considered only when no other option is valid (vanilla events/_events.info), so the speaker can always answer.
# Witchcraft's own text "I have no proposals." (ev10.86.d) is reused; no new key.
E("events/ev7.txt",
"""	after = {
		trigger_event = magic_ev7.106
	}
}
""",
"""	option = { # 2.39 (Supernatural): a speaker with nothing else to propose can always answer (WORK-ORDER-2.39 B3 E)
		name = ev10.86.d
		fallback = yes
	}
	after = {
		trigger_event = magic_ev7.106
	}
}
""")


# =====================================================================================================================
# 2.39 (Supernatural) -- package P2 (WORK-ORDER-2.39)
# =====================================================================================================================
# 2.39 F17 U1 -- "The Ringing" (magic_ev.4): a wiped wolf who hears it counts a ring and may remember (spn_ringing_heard_effect).
E('events/ev1.txt',
"""	immediate = {
		save_scope_as = watcher
""",
"""	immediate = {
		save_scope_as = watcher
		spn_ringing_heard_effect = yes # 2.39 (Supernatural): the wolf remembers (WORK-ORDER-2.39 F17 U1; zz_spn_mind_effects.txt)
""")

# 2.39 F17 U2 -- the Draught of a Clear Mind is a guarded mind everywhere Witchcraft asks has_immunity_for_magic_domination.
# The anchor deliberately stays clear of the species gate at the top of the same OR (B14).
E('common/scripted_triggers/magic_triggers.txt',
"""		has_perk = natural_immunity_perk
		is_antimagic_trigger = yes
	}
}
has_immunity_for_mind_scan = {""",
"""		has_perk = natural_immunity_perk
		has_character_modifier = spn_clear_mind_modifier # 2.39 (Supernatural): the Draught of a Clear Mind (WORK-ORDER-2.39 F17 U2)
		is_antimagic_trigger = yes
	}
}
has_immunity_for_mind_scan = {""")

# 2.39 F17 U3 -- the Draught in Witchcraft's Create Potion menu (magic_ev2.41): three years, like the brews beside it.
E('events/ev2.txt',
"""	option = {
		name = ev2.41.d
""",
"""	# 2.39 (Supernatural): the Draught of a Clear Mind (WORK-ORDER-2.39 F17 U3). Sparing on purpose: base 1 like its
	# neighbours, +4 for one who knows a vampire's or an Order member's secret, +2 for a defector.
	option = {
		name = spn_ev2.41.mind
		send_interface_toast = {
			title = ev2.41.title
			add_character_modifier = {
				modifier = spn_clear_mind_modifier
				years = 3
			}
		}
		ai_chance = {
			base = 1
			modifier = {
				add = 4
				any_known_secret = {
					OR = {
						secret_type = spn_secret_vampire
						secret_type = spn_secret_hybrid
						secret_type = spn_secret_blue_rose
					}
				}
			}
			modifier = {
				add = 2
				has_character_flag = spn_order_defector
			}
		}
	}
	option = {
		name = ev2.41.d
""")

# 2.39 F17 U4 -- the same Draught in the alchemist's menu (magic_ev9.66): three years, like every potion in it (red team L5).
E('events/ev9.txt',
"""	option = {
		name = ev9.66.0.a
""",
"""	# 2.39 (Supernatural): the Draught of a Clear Mind (WORK-ORDER-2.39 F17 U4). Three years, as in magic_ev2.41.
	option = {
		name = spn_ev2.41.mind
		send_interface_toast = {
			title = ev2.41.title
			add_character_modifier = {
				modifier = spn_clear_mind_modifier
				years = 3
			}
		}
		ai_chance = {
			base = 1
			modifier = {
				add = 4
				any_known_secret = {
					OR = {
						secret_type = spn_secret_vampire
						secret_type = spn_secret_hybrid
						secret_type = spn_secret_blue_rose
					}
				}
			}
			modifier = {
				add = 2
				has_character_flag = spn_order_defector
			}
		}
	}
	option = {
		name = ev9.66.0.a
""")


# =====================================================================================================================
# 2.39 (Supernatural) -- package P3 (WORK-ORDER-2.39)
# =====================================================================================================================
# 2.39 F11 (1) -- the council's war on hunters, "Find them and kill them" (magic_ev10.84 option a): with the Order on, the
# Adeptus Major also goes to the hunters on the Order's watch list (spn_order_council_hunters_effect, re-checked at send).
E('events/ev10.txt',
"""		custom_tooltip = ev10.84.a_ct
		custom_tooltip = witch_hunters_vacations_ct
		add_character_flag = amage_rep1_bmage_rep1_flag
""",
"""		custom_tooltip = ev10.84.a_ct
		custom_tooltip = witch_hunters_vacations_ct
		add_character_flag = amage_rep1_bmage_rep1_flag
		hidden_effect = { spn_order_council_hunters_effect = yes } # 2.39 (Supernatural): the Adeptus Major, to the hunters the Order watches (WORK-ORDER-2.39 F11)
""")

# 2.39 F11 (1) -- the same, for "The Council will set bounties on the heads of hunters" (magic_ev10.84 option c). Before
# Witchcraft's own random deaths among AI witch hunters, so the send never reads a man killed in the same moment.
E('events/ev10.txt',
"""		hidden_effect = {
			witch_hunter_vacations_effect = { Y = 3 }
			every_living_character = {
				limit = {
					is_witch_hunter = yes
""",
"""		hidden_effect = {
			witch_hunter_vacations_effect = { Y = 3 }
			spn_order_council_hunters_effect = yes # 2.39 (Supernatural): the Adeptus Major, to the hunters the Order watches (WORK-ORDER-2.39 F11)
			every_living_character = {
				limit = {
					is_witch_hunter = yes
""")

# 2.39 F11 (2) -- A Sister on Trial: at the trial's start, beside its first event (witch_trial on_accept). Witchcraft decides
# the trial in immediate events, so the Order's answer is an aftermath (spn_order.1007, 3-7 days later, to her Temple Magus).
E('common/character_interactions/00_magic_interactions.txt',
"""				scope:recipient = {
					custom_tooltip = witch_trial_ct2
				}
				trigger_event = magic_ev3.54
""",
"""				scope:recipient = {
					custom_tooltip = witch_trial_ct2
				}
				trigger_event = magic_ev3.54
				spn_order_trial_begun_effect = yes # 2.39 (Supernatural): an Order member on trial; her Temple Magus hears of it (WORK-ORDER-2.39 F11)
""")


# =====================================================================================================================
# 2.39 (Supernatural) -- package P7 (WORK-ORDER-2.39)
# =====================================================================================================================
# 2.39 F12 I1 -- a motion before the council. The forum is Witchcraft's own "second part" of the secret meeting
# (magic_ev10.85); a third option opens The Council's Business (spn_order.1000): Imperium, or the Great Respondeo when one
# is due (F13). Hidden with the Order rule Off (spn_council_motion_available_trigger starts with spn_order_on_trigger).
E('events/ev10.txt',
"""		add_internal_flag = special
		trigger_event = magic_ev10.94
		ai_chance = {
			base = 0
		}
	}
}
#secret meeting! - loremaster proposal""",
"""		add_internal_flag = special
		trigger_event = magic_ev10.94
		ai_chance = {
			base = 0
		}
	}
	option = { # 2.39 (Supernatural): a motion before the council -- Imperium, or a council work (WORK-ORDER-2.39 F12, F13)
		name = spn_ev10_85_motion
		trigger = { spn_council_motion_available_trigger = yes }
		hidden_effect = { set_variable = { name = spn_imp_in_meeting value = yes days = 60 } }
		trigger_event = spn_order.1000
		ai_chance = {
			base = 0
			modifier = { add = 1 has_trait = ambitious }
			modifier = { add = 1 has_trait = arrogant }
			modifier = { add = 1 has_character_flag = mc_crisises_flag }
			modifier = { add = 2 spn_council_work_due_trigger = yes can_spend_huge_ps_trigger = yes } # when a work is due and he can cast it
			modifier = { factor = 0 OR = { has_trait = content has_trait = humble } }
		}
	}
}
#secret meeting! - loremaster proposal""")

# 2.39 F12 I2 -- a Grand Magus who holds Imperium manages the council's funds himself (entry 77 already covers his
# embezzling). Inert with the Order rule Off (spn_imperium_holds_trigger needs it On).
E('common/decisions/magic_dec.txt',
"""	is_shown = {
		exists = global_var:current_admin_global
		global_var:current_admin_global = ROOT
		is_imprisoned = no
	}""",
"""	is_shown = {
		OR = { # 2.39 (Supernatural): Imperium (WORK-ORDER-2.39 F12)
			AND = {
				exists = global_var:current_admin_global
				global_var:current_admin_global = ROOT
			}
			spn_imperium_holds_trigger = yes
		}
		is_imprisoned = no
	}""")

# 2.39 F12 I3 -- Imperium opens Witchcraft's Demand Submission for its term (the Summit's "extraordinary privileges" open
# it for good). The anchor keeps the tab after "scope:actor = {" that is in the file (written \t below). Inert with the Order rule Off.
E('common/character_interactions/00_magic_interactions.txt',
"""		exists = global_var:archmage_can_deman_submision
		scope:actor = {\t
			is_imprisoned = no""",
"""		OR = { # 2.39 (Supernatural): Imperium (WORK-ORDER-2.39 F12)
			exists = global_var:archmage_can_deman_submision
			scope:actor = { spn_imperium_holds_trigger = yes }
		}
		scope:actor = {\t
			is_imprisoned = no""")

# 2.39 F12 I4 -- a seat holder's death can bring a refused Imperium back (the show's Bennett). Witchcraft's remover runs
# first on death (yearly2_on_actions.txt loads before zz_spn_order_on_actions.txt) and erases mc_member_var, so the call
# sits HERE, before remove_from_mc_effect (red team H2). The vote itself waits 7 days (spn_order.1008). Not for the Grand
# Magus himself; nothing with the Order rule Off; nothing unless a refusal is on record.
E('common/on_action/yearly2_on_actions.txt',
"""on_action_mc_remover = {
	trigger = {
		has_variable = mc_member_var
	}
	effect = {
		remove_from_mc_effect = yes""",
"""on_action_mc_remover = {
	trigger = {
		has_variable = mc_member_var
	}
	effect = {
		if = { # 2.39 (Supernatural): a seat holder's death is a crisis for a refused Imperium (WORK-ORDER-2.39 F12, I4)
			limit = {
				spn_order_on_trigger = yes
				NOT = { global_var:current_archmage_global ?= this }
			}
			spn_imperium_crisis_effect = { CRISIS = flag:death }
		}
		remove_from_mc_effect = yes""")


# =====================================================================================================================
# 2.39 (Supernatural) -- package P5 (WORK-ORDER-2.39)
# =====================================================================================================================
# 2.39 F3 -- the witness misfire. set_spell_id is the line every Witchcraft spell runs first (25 interactions, 7 decisions,
# the Powerful Curse and the Tornado, the court-mage and corruption events; the Touch of Nyarlathotep already counts casts
# here). One call into Supernatural's own roll, inside Witchcraft's own hidden_effect, so no tooltip can ever show odds.
# The roll, its guards (the caster only, a witness, the book not destroyed, not the duel or a demon's making, once a day)
# and its event are Supernatural's: common/scripted_effects/zz_spn_misfire_effects.txt (WORK-ORDER-2.39 F3).
E('common/scripted_effects/00_variety_magic_effects.txt',
"""set_spell_id = {
	hidden_effect = {
		set_variable = {
			name = spell_id
			value = $ID$
		}
""",
"""set_spell_id = {
	hidden_effect = {
		set_variable = {
			name = spell_id
			value = $ID$
		}
		spn_vade_misfire_roll_effect = yes # 2.39 (Supernatural): a witness's spell may go wrong while any part of the Vade Maecum survives
""")


# =====================================================================================================================
# 2.39 (Supernatural) -- package P9 (WORK-ORDER-2.39)
# =====================================================================================================================
# Supernatural 2.39 -- package P9 upstream entries (WORK-ORDER-2.39 F9). Five entries, two files. Each `old` matches once
# in Witchcraft 2.18 (ref/wc) and, except the registration entry (whose `new` is the mod's own 2.35 text), once in 2.38.

# 2.39 F9 -- register the 2.35 spn_was_mortal block in make_demon_effect. It was a hand edit the generator never knew
# (WORK-ORDER-2.39 2, redteam R1): a fresh Witchcraft copy would have lost it. old = Witchcraft 2.18's own text, new =
# the mod's text since 2.35, unchanged. In the 2.38 tree it reports "already present". The F9 gate below never touches
# these lines, so this entry still matches after it (the generator stays re-runnable).
E("common/scripted_effects/00_variety_magic_effects.txt",
"""		healing_old_age_effect = yes
	}
}

send_tornado_notification_effect = {
""",
"""		healing_old_age_effect = yes
		# SUPERNATURAL 2.35 PART TWO -- ADDED, one line, nothing above changed. (Order §5.4, §12.)
		#
		# THERE WAS A PERSON HERE. Every path that MAKES a demon out of somebody runs this effect -- the
		# demon0 maturation (magic_ev3.75, magic_ev2.38), the magic eruption, the Ascendancy project,
		# Abraxas's courtier -- and no path that SUMMONS one does, because a summoned demon is created from
		# a character template and never comes through here.
		#
		# So this flag is the whole of the question exorcism turns on: the ones who were made can be given
		# back, and the ones who were only ever smoke wearing a body cannot. It changes nothing about how
		# the demon behaves, and nothing upstream reads it.
		add_character_flag = spn_was_mortal
	}
}

send_tornado_notification_effect = {
""")

# 2.39 F9 -- Mortals Becoming Demons: the gate in make_demon_effect. Every path that MAKES a demon out of a living
# character runs this effect (the demon-blooded heir at 20-21 magic_ev3.75, "The truth about me" magic_ev2.38, the
# eruption magic_ev7.11, the Ascendancy project magic_ev7.117, the Bael letter's courtier magic_ev5.60). The name stays
# for every caller and becomes the gate; Witchcraft's body stays exactly as it is, line for line, under a name of its
# own. That is on purpose: wrapping it in place would re-indent every line, and the registration entry above must still
# match the body after this one has run, so the generator stays re-runnable. Only the effect's first line is anchored.
E("common/scripted_effects/00_variety_magic_effects.txt",
"""make_demon_effect = {
	if = {
		limit = {
			has_trait = golem
""",
"""# 2.39 (Supernatural): WORK-ORDER-2.39 F9, the rule "Supernatural: Mortals Becoming Demons". Under Players Only an AI
# character is never made a demon here, and a demon-blooded one keeps demon0. Default is exactly 2.38.
make_demon_effect = {
	if = {
		limit = { spn_may_become_demon_trigger = yes } # 2.39 (Supernatural): zz_spn_mortal_demons_triggers.txt
		spn_make_demon_body_effect = yes
	}
}
# 2.39 (Supernatural): Witchcraft's make_demon_effect body, unchanged line for line, under its own name. Callers use
# make_demon_effect, never this.
spn_make_demon_body_effect = {
	if = {
		limit = {
			has_trait = golem
""")

# 2.39 F9 -- Mortals Becoming Demons: create_mage_effect, the "badass" branch's 10% demon. An existing AI ruler is made
# a world Mage here, so under Players Only this never makes a demon.
E("common/scripted_effects/00_variety_magic_effects.txt",
"""					random = {
						chance = 10
						add_trait = demon1
					}
""",
"""					random = {
						chance = 10
						if = {
							limit = { spn_may_become_demon_trigger = yes } # 2.39 (Supernatural): F9, Mortals Becoming Demons
							add_trait = demon1
						}
					}
""")

# 2.39 F9 -- Mortals Becoming Demons: magical_research_for_ai_effect, an AI mage's own research outcome (a raw demon1).
E("common/scripted_effects/00_variety_magic_effects.txt",
"""							is_or_will_be_a_demon_trigger = no
							has_trait_xp = {
								trait = archmage
								track = secret_knowledge
								value > 50
""",
"""							is_or_will_be_a_demon_trigger = no
							spn_may_become_demon_trigger = yes # 2.39 (Supernatural): F9, Mortals Becoming Demons
							has_trait_xp = {
								trait = archmage
								track = secret_knowledge
								value > 50
""")

# 2.39 F9 -- Mortals Becoming Demons: Ascendancy research (mr_ascendancy_effect, a raw demon1). A player always passes,
# so the project's tooltip (show_as_tooltip of this effect) still says what it does.
E("common/scripted_effects/00_magical_research_effects.txt",
"""mr_ascendancy_effect = {
	add_trait = demon1
""",
"""mr_ascendancy_effect = {
	if = {
		limit = { spn_may_become_demon_trigger = yes } # 2.39 (Supernatural): F9, Mortals Becoming Demons
		add_trait = demon1
	}
""")


# =====================================================================================================================
# 2.39 (Supernatural) -- package PB (WORK-ORDER-2.39)
# =====================================================================================================================
# 2.39 Boot 1 (16 Oct) -- the Gnostic Council's secrecy (tool/pkgs/PB/HANDOFF.md). With the Order rule On the council is the
# Order's (2.38b), and its HUD button is shown to members only (entries 29 and 30). Three of Witchcraft's own council
# actions did not follow that rule: Thomas, a witch outside the Order, saw "Make a donation to the Gnostic Council", and its
# tooltip named every seat holder. "Ask the Grand Magus for support" and "Ask for a seat on the Gnostic Council" are shown
# on one portrait only, the Grand Magus's, so they pointed at him (the B6 rule). spn_order_council_known_trigger
# (common/scripted_triggers/zz_spn_council_known_triggers.txt) is true without the Order's council, once Witchcraft has
# revealed it (mc_revealed), and for a member. Witchcraft's own tests are kept; one line is added to each is_shown.

# The donation (Witchcraft: any witch, or anyone once the council is revealed).
E("common/decisions/magic_dec.txt",
"""	is_shown = {
		mc_gold_global_exists_trigger = yes
		is_imprisoned = no
		OR = {
			is_witch_trigger = yes
			exists = global_var:mc_revealed
		}
""",
"""	is_shown = {
		mc_gold_global_exists_trigger = yes
		is_imprisoned = no
		OR = {
			is_witch_trigger = yes
			exists = global_var:mc_revealed
		}
		spn_order_council_known_trigger = yes # 2.39 (Supernatural): with the Order's council, its own members only (Boot 1, 16 Oct)
""")

# Ask the Grand Magus for support (Witchcraft: any donor, on the Grand Magus's portrait).
E("common/character_interactions/00_magic_interactions.txt",
"""		global_var:current_archmage_global = scope:recipient
		scope:actor = {	
			is_imprisoned = no
			has_character_modifier = mc_supporter_modifier
		}
""",
"""		global_var:current_archmage_global = scope:recipient
		scope:actor = {	
			is_imprisoned = no
			has_character_modifier = mc_supporter_modifier
			spn_order_council_known_trigger = yes # 2.39 (Supernatural): with the Order's council, its own members only (Boot 1, 16 Oct)
		}
""")

# Ask for a seat on the Gnostic Council (Witchcraft: any Mage or Yaga, on the Grand Magus's portrait). 2.38b's entry 27
# already greys it for a non-member; now a non-member does not see it at all.
E("common/character_interactions/00_magic_interactions.txt",
"""		global_var:current_archmage_global = scope:recipient
		scope:actor = {	
			is_imprisoned = no
			OR = {
				has_trait = archmage
				has_trait = yaga
			}
			NOT = { has_variable = mc_member_var }
		}
""",
"""		global_var:current_archmage_global = scope:recipient
		scope:actor = {	
			is_imprisoned = no
			OR = {
				has_trait = archmage
				has_trait = yaga
			}
			NOT = { has_variable = mc_member_var }
			spn_order_council_known_trigger = yes # 2.39 (Supernatural): with the Order's council, its own members only (Boot 1, 16 Oct)
		}
""")

# 2.39 Boot 2 (16 Oct) -- the mage duel's AI (tool/pkgs/PB/HANDOFF.md). Thomas, an Order Magistratus, was challenged by
# Count Merlin again and again and declined each time ("Why do you want to fight me? We're both mages."). Witchcraft's AI
# gave +50 for merely being the stronger mage, so a strong AI mage challenged every weaker one in reach about every year.
# The AI now needs a reason, built from Witchcraft's own weights (spn_mage_duel_ai_motive_trigger,
# common/scripted_triggers/zz_spn_mage_duel_triggers.txt), and a refused challenge is remembered for five years. A player
# may still challenge anyone, as before.
E("common/character_interactions/00_magic_interactions.txt",
"""	ai_frequency = 24
	ai_will_do = {
		base = 0
		modifier = {
			add = 50
			scope:actor.overall_magic_power_value > scope:recipient.overall_magic_power_p1_value
		}
""",
"""	ai_frequency = 24
	ai_will_do = {
		base = 0
		modifier = { # 2.39 (Supernatural): no challenge without a reason (Boot 2, 16 Oct)
			add = -1000
			spn_mage_duel_ai_motive_trigger = no
		}
		modifier = { # 2.39 (Supernatural): a refused challenge is not repeated for five years (Boot 2, 16 Oct)
			add = -1000
			scope:actor = {
				has_opinion_modifier = {
					target = scope:recipient
					modifier = spn_refused_mage_duel_opinion
				}
			}
		}
		modifier = {
			add = 50
			scope:actor.overall_magic_power_value > scope:recipient.overall_magic_power_p1_value
		}
""")

E("common/character_interactions/00_magic_interactions.txt",
"""		flag = mage_duel_forced
		localization = MAGE_DUEL_O3b
	}
""",
"""		flag = mage_duel_forced
		localization = MAGE_DUEL_O3b
	}
	on_decline = { # 2.39 (Supernatural): an AI challenger remembers a refusal (Boot 2, 16 Oct)
		scope:actor = {
			if = {
				limit = { is_ai = yes }
				add_opinion = {
					target = scope:recipient
					modifier = spn_refused_mage_duel_opinion
				}
			}
		}
	}
""")

# ======================================================================================================================
# 2.39 (Thomas's call, 16 Oct) -- WITCHCRAFT'S AI NEEDS A REASON. After the mage duel Thomas asked for "any other AI in the
# witchcraft part of the mod that would improve things". An audit of every Witchcraft interaction, decision, scheme and
# AI effect (HANDOFF §8) found AI that stole, warred, dominated or made enemies for power, strength or chance alone,
# sometimes anywhere in the world, and one on_action that singled out players. The reasons are in
# common/scripted_triggers/zz_spn_239_ai_motive_triggers.txt. Witchcraft's weights are otherwise kept.
# ======================================================================================================================

# The artifact thief (magic_ev2.10, from the yearly magic_ev2.1): an AI mage or witch picked any holder of a magic item in
# range, a friend or kin included. Now only someone it has a reason to rob (a grudge, or its own greed or ambition).
E("events/ev2.txt",
"""		any_living_character = {
			NOT = { this = root }
			any_character_artifact = { has_variable = magic1 }
			in_diplomatic_range = root
		}
""",
"""		any_living_character = {
			NOT = { this = root }
			any_character_artifact = { has_variable = magic1 }
			in_diplomatic_range = root
			spn_ai_artifact_motive_trigger = { ACTOR = root } # 2.39 (Supernatural): a reason to rob him (Thomas, 16 Oct)
		}
""")
E("events/ev2.txt",
"""		random_living_character = {
			limit = {
				any_character_artifact = { has_variable = magic1 }
				NOT = { root = this }
				in_diplomatic_range = root
			}
			save_scope_as = target
		}
""",
"""		random_living_character = {
			limit = {
				any_character_artifact = { has_variable = magic1 }
				NOT = { root = this }
				in_diplomatic_range = root
				spn_ai_artifact_motive_trigger = { ACTOR = root } # 2.39 (Supernatural): a reason to rob him (Thomas, 16 Oct)
			}
			weight = { # 2.39 (Supernatural): the one he wants most is the likeliest (Boot 3, 16 Oct)
				base = 0
				modifier = { add = spn_ai_artifact_desire_value }
			}
			save_scope_as = target
		}
""")
# Its war for the item: a just character no longer counts as more warlike (Witchcraft gave brave OR just +10).
E("events/ev2.txt",
"""			modifier = {
				add = 10
				OR = {
					has_trait = brave
					has_trait = just
				}
			}
			modifier = {
				add = 50
				max_military_strength > scope:target.max_military_strength
			}
""",
"""			modifier = {
				add = 10
				has_trait = brave # 2.39 (Supernatural): was brave or just (Thomas, 16 Oct)
			}
			modifier = { # 2.39 (Supernatural): the just, the content and the compassionate do not go to war for a trinket
				add = -50
				OR = {
					has_trait = just
					has_trait = content
					has_trait = compassionate
				}
			}
			modifier = {
				add = 50
				max_military_strength > scope:target.max_military_strength
			}
""")

# "Striving for magic power" (ai_striving_for_magic_power_effect, magic_ev10.156): the AI claimed a random magic item in
# range, or else ANYWHERE in the world, then went after it (war, abduction, domination, theft, mercenaries). Now only in
# range, and only from someone it has a reason to rob.
E("common/scripted_effects/00_variety_magic_effects.txt",
"""	if = {
		limit = {
			any_artifact = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				NOT = { any_artifact_claimant = { THIS = ROOT } }
				artifact_owner = { in_diplomatic_range = ROOT NOT = { has_strong_hook = ROOT } }
			}
		}
		random_artifact = {
			limit = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				NOT = { any_artifact_claimant = { THIS = ROOT } }
				artifact_owner = { in_diplomatic_range = ROOT NOT = { has_strong_hook = ROOT } }
			}
			save_scope_as = art1
		}
	}
	else_if = {
		limit = {
			any_artifact = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				NOT = { any_artifact_claimant = { THIS = ROOT } }
				artifact_owner = { NOT = { has_strong_hook = ROOT } }
			}
		}
		random_artifact = {
			limit = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				NOT = { any_artifact_claimant = { THIS = ROOT } }
				artifact_owner = { NOT = { has_strong_hook = ROOT } }
			}
			save_scope_as = art1
		}
	}
""",
"""	# 2.39 (Supernatural): in range only (no longer anywhere in the world), and only from someone it has a reason to rob
	# (Thomas, 16 Oct).
	random_artifact = {
		limit = {
			has_variable = magic1
			NOT = { artifact_owner = ROOT }
			NOT = { any_artifact_claimant = { THIS = ROOT } }
			artifact_owner = {
				in_diplomatic_range = ROOT
				NOT = { has_strong_hook = ROOT }
				spn_ai_artifact_motive_trigger = { ACTOR = ROOT }
			}
		}
		save_scope_as = art1
	}
""")
# Its second step goes after an item it already claims. A claim is its reason, but not against someone it now spares.
E("common/scripted_effects/00_variety_magic_effects.txt",
"""			any_claimed_artifact = { has_variable = magic1 artifact_owner = { in_diplomatic_range = ROOT } }
		}
		random_claimed_artifact = {
			limit = { has_variable = magic1 artifact_owner = { in_diplomatic_range = ROOT } }
""",
"""			any_claimed_artifact = { has_variable = magic1 artifact_owner = { in_diplomatic_range = ROOT NOT = { spn_ai_spares_trigger = { ACTOR = ROOT } } } } # 2.39 (Supernatural)
		}
		random_claimed_artifact = {
			limit = { has_variable = magic1 artifact_owner = { in_diplomatic_range = ROOT NOT = { spn_ai_spares_trigger = { ACTOR = ROOT } } } } # 2.39 (Supernatural)
""")
# Its domination branch ran magic_domination through run_interaction, which skips the interaction's own -200 against a
# player: at a player only with a real grudge now (a rivalry or a war; Thomas, Boot 3: "only if it makes sense").
E("common/scripted_effects/00_variety_magic_effects.txt",
"""		else_if = {	#domination
			limit = {
				scope:oart2 = {
					is_powerful_being = no
""",
"""		else_if = {	#domination
			limit = {
				scope:oart2 = {
					OR = { # 2.39 (Supernatural): a player only with a real grudge; run_interaction skips magic_domination's own -200 (Thomas, 16 Oct)
						is_ai = yes
						has_relation_rival = ROOT
						has_relation_nemesis = ROOT
						is_at_war_with = ROOT
					}
					is_powerful_being = no
""")

# The artifact seeker (ai_artifact_seeker_effect, magic_ev11.199 every 3-4 years): the same, with two more fallbacks to
# ANY magic item in the world, claimed or not. Now in range only: a reason to rob, or a claim it already holds.
E("common/scripted_effects/00_variety_magic_effects.txt",
"""	random_artifact = {
		limit = {
			has_variable = magic1
			NOT = { artifact_owner = ROOT }
			NOT = { any_artifact_claimant = { THIS = ROOT } }
			artifact_owner = { in_diplomatic_range = ROOT NOT = { has_strong_hook = ROOT } }
		}
		save_scope_as = art1
	}
	if = {
		limit = {
			NOT = {
				exists = scope:art1
			}
		}
		random_artifact = {
			limit = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				NOT = { any_artifact_claimant = { THIS = ROOT } }
				artifact_owner = { NOT = { has_strong_hook = ROOT } }
			}
			save_scope_as = art1
		}
	}
	if = {
		limit = {
			NOT = {
				exists = scope:art1
			}
		}
		random_artifact = {
			limit = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				artifact_owner = { NOT = { has_strong_hook = ROOT } }
			}
			save_scope_as = art1
		}
	}
""",
"""	# 2.39 (Supernatural): in range only (no longer anywhere in the world): someone it has a reason to rob, else an item
	# it already claims from someone it does not spare (Thomas, 16 Oct).
	random_artifact = {
		limit = {
			has_variable = magic1
			NOT = { artifact_owner = ROOT }
			NOT = { any_artifact_claimant = { THIS = ROOT } }
			artifact_owner = {
				in_diplomatic_range = ROOT
				NOT = { has_strong_hook = ROOT }
				spn_ai_artifact_motive_trigger = { ACTOR = ROOT }
			}
		}
		save_scope_as = art1
	}
	if = {
		limit = {
			NOT = {
				exists = scope:art1
			}
		}
		random_artifact = {
			limit = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				any_artifact_claimant = { THIS = ROOT }
				artifact_owner = {
					in_diplomatic_range = ROOT
					NOT = { has_strong_hook = ROOT }
					NOT = { spn_ai_spares_trigger = { ACTOR = ROOT } }
				}
			}
			save_scope_as = art1
		}
	}
""")
E("common/scripted_effects/00_variety_magic_effects.txt",
"""		else_if = {	#domination
			limit = {
				scope:oart1 = {
					is_powerful_being = no
""",
"""		else_if = {	#domination
			limit = {
				scope:oart1 = {
					OR = { # 2.39 (Supernatural): a player only with a real grudge; run_interaction skips magic_domination's own -200 (Thomas, 16 Oct)
						is_ai = yes
						has_relation_rival = ROOT
						has_relation_nemesis = ROOT
						is_at_war_with = ROOT
					}
					is_powerful_being = no
""")

# "The human must die!" (magic_ev2.14): a demon with no rival made any landed mage in the WORLD its rival, pressed a claim
# on one of his counties, and told him so (magic_ev2.4); a witch hunter qualified only if he was a player. Now someone in
# its reach whom it does not like, AI or player alike.
E("events/ev2.txt",
"""					AND = {
						has_trait = witch_hunter
						is_ai = no
					}
				}
				NOR = {
					has_relation_best_friend = root
""",
"""					has_trait = witch_hunter # 2.39 (Supernatural): any witch hunter, not only a player (Thomas, 16 Oct)
				}
				in_diplomatic_range = root # 2.39 (Supernatural): in its reach, not anywhere in the world
				NOT = { # 2.39 (Supernatural): not someone it likes
					reverse_opinion = {
						target = root
						value >= medium_positive_opinion
					}
				}
				NOR = {
					has_relation_best_friend = root
""")

# Demand Submission, the Grand Magus (demand_submission_archmage_interaction): base 10 to any mage or witch in range, a
# popup that pauses, and a refusal gives him an imprisonment reason for ten years. Now he needs a reason: ill will, a
# rivalry, or an ambitious or arrogant nature.
E("common/character_interactions/00_magic_interactions.txt",
"""	ai_frequency = 24
	ai_will_do = {
		base = 10
		modifier = {
			add = -10
""",
"""	ai_frequency = 24
	ai_will_do = {
		base = 10
		modifier = { # 2.39 (Supernatural): a reason to demand it (Thomas, 16 Oct)
			add = -1000
			scope:actor = {
				NOR = {
					opinion = {
						target = scope:recipient
						value < 0
					}
					has_relation_rival = scope:recipient
					has_relation_nemesis = scope:recipient
					spn_ai_domineering_trigger = yes
				}
			}
		}
		modifier = {
			add = -10
""")
# His answer to a refusal (magic_ev10.78) had no AI weights, so a calm Grand Magus sent the Black Mage after a refuser as
# often as a vengeful one. That arrest can end in a duel to the death.
E("events/ev10.txt",
"""		name = ev10.78.a
""",
"""		name = ev10.78.a
		ai_chance = { # 2.39 (Supernatural): by his nature (Thomas, 16 Oct)
			base = 40
			modifier = {
				add = 30
				OR = {
					has_trait = vengeful
					has_trait = arrogant
				}
			}
		}
""")
E("events/ev10.txt",
"""		name = ev10.78.b
""",
"""		name = ev10.78.b
		ai_chance = { # 2.39 (Supernatural): by his nature (Thomas, 16 Oct)
			base = 40
			modifier = {
				add = 60
				OR = {
					has_trait = forgiving
					has_trait = compassionate
				}
			}
			modifier = {
				add = -30
				has_trait = vengeful
			}
		}
""")
E("events/ev10.txt",
"""		name = ev10.78.c
""",
"""		name = ev10.78.c
		ai_chance = { # 2.39 (Supernatural): by his nature; the arrest can end in a duel to the death (Thomas, 16 Oct)
			base = 5
			modifier = {
				add = 45
				OR = {
					has_trait = vengeful
					has_trait = wrathful
					has_trait = sadistic
				}
			}
			modifier = {
				factor = 0
				OR = {
					has_trait = forgiving
					has_trait = compassionate
				}
			}
		}
""")

# Demand Submission, the coven's grandmaster (demand_submission_cgm_interaction): a flat 50, nothing else. Now weighed
# like the Grand Magus's: ill will and a domineering nature raise it; a friend or a lover is left alone.
E("common/character_interactions/00_magic_interactions.txt",
"""	ai_will_do = {
		base = 50
	}
""",
"""	ai_will_do = {
		base = 10 # 2.39 (Supernatural): was a flat 50 (Thomas, 16 Oct)
		modifier = {
			add = 20
			scope:actor = {
				opinion = {
					target = scope:recipient
					value < 0
				}
			}
		}
		modifier = {
			add = 20
			scope:actor = { spn_ai_domineering_trigger = yes }
		}
		modifier = {
			add = -100
			scope:recipient = {
				OR = {
					has_relation_friend = scope:actor
					has_relation_best_friend = scope:actor
					has_relation_lover = scope:actor
					has_relation_soulmate = scope:actor
				}
			}
		}
	}
""")

# Consume Child (consume_child): any AI cannibal witch, base 50 every two years, at a courtier, guest, prisoner or ward
# under 16, a player's child included. Now it is the cruel who do it, never to their own kin or a ward in their care,
# and never to a player's child without a grudge against that parent ("no dying out of nowhere"). Final pass (17 Oct,
# review C3): nor to a player who is himself a child (a child ruler taken in a siege, say).
E("common/character_interactions/00_magic_interactions.txt",
"""	ai_frequency = 24

	ai_will_do = {
		base = 50
		modifier = {
			add = -150
""",
"""	ai_frequency = 24

	ai_will_do = {
		base = 10 # 2.39 (Supernatural): was 50 (Thomas, 16 Oct)
		modifier = { # 2.39 (Supernatural): the cruel
			add = 40
			scope:actor = {
				OR = {
					has_trait = sadistic
					has_trait = callous
				}
			}
		}
		modifier = { # 2.39 (Supernatural): never the AI's own kin
			add = -1000
			scope:recipient = { is_close_or_extended_family_of = scope:actor }
		}
		modifier = { # 2.39 (Supernatural): not a ward in its care
			add = -100
			scope:recipient = { has_relation_guardian = scope:actor }
		}
		modifier = { # 2.39 (Supernatural): never a player who is himself a child (final pass, 17 Oct)
			add = -1000
			scope:recipient = { is_ai = no }
		}
		modifier = { # 2.39 (Supernatural): a player's child, unless the AI has a grudge against that parent
			add = -1000
			scope:recipient = {
				any_parent = {
					is_ai = no
					NOR = {
						has_relation_rival = scope:actor
						has_relation_nemesis = scope:actor
						is_at_war_with = scope:actor
					}
				}
			}
		}
		modifier = {
			add = -150
""")

# An inquisitor joining a war on an archmage (mage_war2_on_action): only when the archmage was a player, and with no
# reason but the office. Now any archmage, and only a zealous inquisitor or one with contempt for him.
E("common/on_action/yearly2_on_actions.txt",
"""		scope:defender = {
			has_trait = archmage
			is_ai = no
		}
		any_ruler = {
			has_character_modifier = inq_modifier
			is_at_war = no
			is_imprisoned = no
			in_diplomatic_range = scope:defender
""",
"""		scope:defender = {
			has_trait = archmage # 2.39 (Supernatural): any archmage, not only a player (Thomas, 16 Oct)
		}
		any_ruler = {
			has_character_modifier = inq_modifier
			is_at_war = no
			is_imprisoned = no
			in_diplomatic_range = scope:defender
			OR = { # 2.39 (Supernatural): a reason to join
				has_trait = zealous
				opinion = {
					target = scope:defender
					value <= medium_negative_opinion
				}
			}
""")
E("common/on_action/yearly2_on_actions.txt",
"""			limit = {
				has_character_modifier = inq_modifier
				is_at_war = no
				is_imprisoned = no
				in_diplomatic_range = scope:defender
""",
"""			limit = {
				has_character_modifier = inq_modifier
				is_at_war = no
				is_imprisoned = no
				in_diplomatic_range = scope:defender
				OR = { # 2.39 (Supernatural): a reason to join (Thomas, 16 Oct)
					has_trait = zealous
					opinion = {
						target = scope:defender
						value <= medium_negative_opinion
					}
				}
""")
# The seeker's first step (review of round 3, MEDIUM): once per 25 years it took a magic item outright from any AI owner in
# the WORLD, its own kin included. Now in range, and only from someone it has a reason to rob.
E("common/scripted_effects/00_variety_magic_effects.txt",
"""		add_character_modifier = {
			modifier = artifact_hunter
			years = 25
		}
		random_artifact = {
			limit = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				artifact_owner = {
					is_ai = yes
""",
"""		add_character_modifier = {
			modifier = artifact_hunter
			years = 25
		}
		random_artifact = {
			limit = {
				has_variable = magic1
				NOT = { artifact_owner = ROOT }
				artifact_owner = {
					is_ai = yes
					in_diplomatic_range = ROOT # 2.39 (Supernatural): in range, and a reason to rob him (Thomas, 16 Oct)
					spn_ai_artifact_motive_trigger = { ACTOR = ROOT }
""")
# The seeker's Domination never took the item (Witchcraft bug, recorded in round 3; Thomas: "patch that bug", 16 Oct).
# magic_ev10.157 seizes scope:art2 from scope:oart2 two weeks after the spell, the names "striving for power" saves. The
# seeker saves art1/oart1, so the event's trigger failed and the Dominated owner kept the item. The seeker now hands the
# event its item and owner under the names it reads. It only reaches this branch with a reason (spn_ai_artifact_motive_trigger
# or a claim from someone it does not spare), and a player only with a rivalry, a nemesis or a war.
E("common/scripted_effects/00_variety_magic_effects.txt",
"""				recipient = scope:oart1
				execute_threshold = accept
			}
			trigger_event = {
				id = magic_ev10.157
				days = 14
			}
""",
"""				recipient = scope:oart1
				execute_threshold = accept
			}
			scope:art1 = { save_scope_as = art2 } # 2.39 (Supernatural): magic_ev10.157 reads art2/oart2 (Thomas, 16 Oct)
			scope:oart1 = { save_scope_as = oart2 }
			trigger_event = {
				id = magic_ev10.157
				days = 14
			}
""")


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

# =====================================================================================================================
# 2.38 "The Blue Rose" -- three passes (WORK-ORDER-2.38 §15.2). Each is idempotent and prints what it did.
# =====================================================================================================================

# ---- apply_strip_perks: Pulveris Memoria strips the magic perks (§5.10 step 3). Regenerated from the perk files present,
# so it follows Witchcraft's renamed trees (2.18: 00_magic_1_witch_tree, 00_magic_2_magic_tree, 00_magic_3_demon_tree).
# The demon tree is never touched (demons cannot join).
STRIP_PERKS_OUT = "common/scripted_effects/zz_spn_order_strip_perks.txt"
def apply_strip_perks():
    import glob
    perks = []
    for path in sorted(glob.glob("common/lifestyle_perks/00_magic_*_perks.txt")):
        if "demon" in os.path.basename(path): continue
        s = read(path).lstrip("﻿")
        for m in re.finditer(r'(?m)^([a-z0-9_]+)\s*=\s*\{', s):
            perks.append(m.group(1))
    if not perks:
        print("STRIP PERKS: no magic perk files found; nothing written (hand merge)"); return
    nl = "\r\n"
    out = ["# Supernatural 2.38 -- GENERATED by apply_upstream_edits.py (apply_strip_perks). Do not edit by hand.",
           "# Pulveris Memoria takes back every magic perk (WORK-ORDER-2.38 §5.10). The demon tree is not touched.",
           "spn_order_strip_perks_effect = {"]
    for p in perks:
        out += ["\tif = {", "\t\tlimit = { has_perk = %s }" % p, "\t\tremove_perk = %s" % p, "\t}"]
    out.append("}")
    text = "﻿" + nl.join(out) + nl
    old = read(STRIP_PERKS_OUT) if os.path.exists(STRIP_PERKS_OUT) else None
    if old == text: return
    write(STRIP_PERKS_OUT, text); print("wrote %s (%d perks)" % (STRIP_PERKS_OUT, len(perks)))

# ---- apply_coven_hooks: every road Witchcraft takes to a coven also opens its panel (§7.2, C8). Expected 5: four line
# adds and one block add (create_extra_coven). Any other count is reported and nothing is written.
COVEN_HOOK = "spn_coven_started_effect = yes # 2.38 (Supernatural): the coven's panel"
def apply_coven_hooks():
    path = "common/scripted_effects/00_variety_magic_effects.txt"
    if not os.path.exists(path): print("MISSING FILE", path); return
    s = read(path); nl = nl_of(s); lines = s.split(nl)
    out = []; i = 0; sites = 0; added = 0
    while i < len(lines):
        ln = lines[i]; out.append(ln)
        m1 = re.match(r'^(\s*)add_house_modifier = witch_coven\s*$', ln)
        m2 = re.match(r'^(\s*)add_house_modifier = \{\s*$', ln)
        if m1:
            sites += 1
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if nxt.strip() != COVEN_HOOK:
                out.append(m1.group(1) + COVEN_HOOK); added += 1
            i += 1; continue
        if m2 and i + 2 < len(lines) and re.match(r'^\s*modifier = witch_coven\s*$', lines[i + 1]) and lines[i + 2].strip() == "}":
            sites += 1
            out.append(lines[i + 1]); out.append(lines[i + 2])
            nxt = lines[i + 3] if i + 3 < len(lines) else ""
            if nxt.strip() != COVEN_HOOK:
                out.append(m2.group(1) + COVEN_HOOK); added += 1
            i += 3; continue
        i += 1
    if sites != 5:
        print("COVEN HOOKS: found %d sites, expected 5 -- hand merge; nothing written" % sites); return
    if added:
        write(path, nl.join(out)); print("hooked %s (%d of 5 coven sites)" % (path, added))

# ---- apply_council_names: Rycie's council, as the Order names it (§5.9, C7). English value text only; [..] and $..$ are
# never touched; idempotent.
COUNCIL_FILES_GLOB = "localization/english/event_localization/witch_*_l_english.yml"
COUNCIL_UPPER = [("High Council of Mages", "Gnostic Council"), ("High Council", "Gnostic Council"),
                 ("an Archmage", "a Grand Magus"), ("Archmagess", "Grand Magus"), ("Archmage", "Grand Magus"),
                 ("Lore Master", "Keeper of the Reliquary"), ("a Black Mage", "an Adeptus Major"), ("Black Mage", "Adeptus Major"),
                 ("Council Administrator", "Chancellor")]
# Lower case means the office only in these lines (each read when the order was built); elsewhere "archmage" is any mage.
COUNCIL_LOWER = {
    "ev7.85.d": [("As a future archmage", "As a future Grand Magus")],
    "ev7.85.d2": [("As an archmage", "As a Grand Magus")],
    "ev7.105.c": [("We need an archmage", "We need a Grand Magus")],
    "ev7.105.d": [("As the archmage", "As the Grand Magus")],
    "DS_WANT_BE_ARCHMAGE": [("I want to be an archmage", "I want to be the Grand Magus")],
    "ev10.62.a_ct": [("position of archmage", "position of Grand Magus")],
    "ev10.63.desc": [("office of archmage", "office of Grand Magus")],
    "ev10.66.desc": [("become an archmage", "become the Grand Magus")],
    "ev10.68.e": [("a much better archmage", "a much better Grand Magus")],
    "ev10.71.desc": [("Being an archmage", "Being the Grand Magus")],
    "ev10.73.desc": [("the current archmage", "the current Grand Magus")],
    "ev10.73.c": [("the archmage is the right leader", "the Grand Magus is the right leader")],
    "ev10.78.c": [("The black mage should", "The Adeptus Major should")],
    "ev10.78.c_ct": [("The black mage will", "The Adeptus Major will")],
    "ev10.79.a": [("As you wish, archmage.", "As you wish, Grand Magus.")],
    "ev10.81.desc2": [("the archmage wants", "the Grand Magus wants")],
    "ev10.88.desc0": [("the archmage shifts", "the Grand Magus shifts")],
    "ACTOR_IS_ARCHMAGE": [("You are the archmage", "You are the Grand Magus")],
    "ev11.81.desc2b": [("the archmage in person", "the Grand Magus in person")],
}
def _council_text(val, pairs):
    # Replace outside [...] and $...$ only.
    parts = re.split(r'(\[[^\]]*\]|\$[^$]*\$)', val)
    for i in range(0, len(parts), 2):
        for a, b in pairs:
            parts[i] = parts[i].replace(a, b)
    return "".join(parts)
def apply_council_names():
    import glob
    files = sorted(glob.glob(COUNCIL_FILES_GLOB))
    if not files: print("COUNCIL NAMES: no Witchcraft English loc found"); return
    changed_total = 0; seen_lower = set()
    for path in files:
        s = read(path); nl = nl_of(s); lines = s.split(nl); changed = 0
        for i, ln in enumerate(lines):
            m = re.match(r'^(\s*)([^\s:#][^:]*):(\d*) ?"(.*)"(\s*)$', ln)
            if not m: continue
            key, val = m.group(2), m.group(4)
            new = _council_text(val, COUNCIL_UPPER)
            if key == "mc_admin_modifier_desc" and new.startswith("Administrator "):
                new = "The Chancellor " + new[len("Administrator "):]
            if key in COUNCIL_LOWER:
                seen_lower.add(key)
                new = _council_text(new, COUNCIL_LOWER[key])
            if new != val:
                lines[i] = '%s%s:%s "%s"%s' % (m.group(1), key, m.group(3), new, m.group(5)); changed += 1
                print("renamed %s: %s" % (key, new[:110]))
        if changed:
            write(path, nl.join(lines)); changed_total += changed
    missing = sorted(set(COUNCIL_LOWER) - seen_lower)
    if missing: print("COUNCIL NAMES: lower-case keys not found (hand check): " + ", ".join(missing))
    if changed_total: print("council names: %d lines" % changed_total)

# ---- apply_interaction_menu (2.38a): Witchcraft's friendly and diplomacy interactions go in the Supernatural menu
# (interaction_category_favorites, which Supernatural names "Supernatural"), as Supernatural's own magic actions do since
# 2.37. Hostile spells stay under Hostile and the witch trial under Prison, as Supernatural's own hostile actions do.
# Idempotent: a key already in the menu is skipped; a key not found is printed.
MENU_FILE = "common/character_interactions/00_magic_interactions.txt"
MENU_KEYS = [
    # friendly (Personal)
    "magic_healing", "teach_sorcery", "teach_spells", "aura_boost", "bless_land", "shadowstep_spell", "hipercognition",
    "drink_magic_potion_interaction", "upgrade_amulet_interaction", "body_adaptation", "thorn_walls_spell",
    "stop_the_cataclysm_spell", "teleportation_spell", "use_nyx_powers_interaction",
    # diplomacy
    "demand_submission_cgm_interaction", "command_minion_interaction", "mana_siphon_spell", "mage_duel",
    "cyro_proposal_interaction", "invite_to_high_council_interaction", "appoint_me_to_high_council_interaction",
    "remove_from_high_council_interaction", "demand_submission_archmage_interaction", "ask_mc_for_support_interaction",
    "threaten_with_magic_interaction", "join_mages_summit", "ask_tw_for_initiation_interaction",
]
def apply_interaction_menu():
    if not os.path.exists(MENU_FILE): print("MISSING FILE", MENU_FILE); return
    s = read(MENU_FILE); nl = nl_of(s); moved = 0; missing = []
    for key in MENU_KEYS:
        m = re.search(r'(?m)^' + re.escape(key) + r' = \{', s)
        if not m: missing.append(key); continue
        end = re.search(r'(?m)^\}', s[m.end():])
        body_end = m.end() + (end.start() if end else len(s) - m.end())
        body = s[m.end():body_end]
        c = re.search(r'(?m)^\tcategory = (interaction_category_[a-z_]+)', body)
        if not c: missing.append(key); continue
        if c.group(1) == "interaction_category_favorites": continue
        new = "\tcategory = interaction_category_favorites # 2.38a (Supernatural): the Supernatural menu (was " + c.group(1) + ")"
        body = body[:c.start()] + new + body[c.end():]
        s = s[:m.end()] + body + s[body_end:]; moved += 1
    if moved:
        write(MENU_FILE, s); print("menu: %d interactions into the Supernatural menu" % moved)
    if missing: print("MENU: not found (hand check): " + ", ".join(missing))


# ---- apply_capstone_bridge (2.38e): the three 2.34 capstone entries now carry the one-capstone guard (CAP38E). A tree
# patched by 2.34-2.38d holds their old text; lift it to the new one before apply_pairs, so the entry reads as present
# instead of asking for a hand merge. Silent when there is nothing to lift. Idempotent.
def apply_capstone_bridge():
    for path, old, new in EDITS:
        for block in CAP38E.values():
            if block not in new or not os.path.exists(path): continue
            s = read(path); nl = nl_of(s)
            legacy = new.replace(block, "").replace("\n", nl); n = new.replace("\n", nl)
            if n not in s and s.count(legacy) == 1:
                write(path, s.replace(legacy, n)); print("bridged", path)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
    apply_capstone_bridge()  # 2.38e
    ok, skipped, missing = apply_pairs()
    apply_weights()
    apply_loc_fix()
    apply_strip_perks()      # 2.38 (§15.2)
    apply_coven_hooks()      # 2.38 (§15.2)
    apply_council_names()    # 2.38 (§15.2)
    apply_interaction_menu() # 2.38a
    print("done: %d applied, %d already present, %d need a hand merge" % (ok, skipped, missing))
    sys.exit(1 if missing else 0)
