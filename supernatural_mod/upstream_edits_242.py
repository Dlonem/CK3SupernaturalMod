"""
Supernatural 2.42 -- the release's edits to Witchcraft-origin files (WORK-ORDER-2.42 v3).
Loaded by apply_upstream_edits.py (register(E)); same (file, old, new) entries, same rules: idempotent, anchor-checked.
"""
V = 'common/scripted_effects/00_variety_magic_effects.txt'
T = 'common/scripted_triggers/magic_triggers.txt'
D = 'common/decisions/magic_dec.txt'
I = 'common/character_interactions/00_magic_interactions.txt'
TR = 'common/traits/00_traits_magic.txt'

def _wl_gain(value):
    return ("\telse_if = { # 2.42 (Supernatural): the Warlock's own pool (WORK-ORDER-2.42 v3, 6). A Mage who is also a Warlock stays on the Mage's\n"
            "\t\tlimit = { has_trait = warlock }\n"
            "\t\tadd_trait_xp = {\n\t\t\ttrait = warlock\n\t\t\ttrack = power_saturation\n\t\t\tvalue = " + value + "\n\t\t}\n\t}\n")

def _wl_spend(tt, value):
    return ("\telse_if = { # 2.42 (Supernatural): the Warlock pays from his own pool\n"
            "\t\tlimit = { has_trait = warlock }\n"
            "\t\tcustom_tooltip = " + tt + "\n"
            "\t\thidden_effect = {\n\t\t\tadd_trait_xp = {\n\t\t\t\ttrait = warlock\n\t\t\t\ttrack = power_saturation\n\t\t\t\tvalue = " + value + "\n\t\t\t}\n\t\t}\n\t}\n")

def register(E):
    # ---- 6, step 1: the three gains -------------------------------------------------------------------
    for val in ("gain_standard_ps_value", "{ gain_source_ps_value gain_huge_ps_value }", "gain_huge_ps_value"):
        old = "\t\t\tvalue = " + val + "\n\t\t}\n\t}\n\telse_if = {\n"
        E(V, old, "\t\t\tvalue = " + val + "\n\t\t}\n\t}\n" + _wl_gain(val) + "\telse_if = {\n")
    # ---- the three spends -----------------------------------------------------------------------------
    for tt, val in (("mana_loss_ct", "-10"), ("mana_loss_ct2", "-20"), ("mana_minor_loss_ct", "-5")):
        old = ("\t\tcustom_tooltip = " + tt + "\n\t\thidden_effect = {\n\t\t\tadd_trait_xp = {\n\t\t\t\ttrait = archmage\n"
               "\t\t\t\ttrack = power_saturation\n\t\t\t\tvalue = " + val + "\n\t\t\t}\n\t\t}\n\t}\n")
        E(V, old, old + _wl_spend(tt, val))
    # ---- the triggers ---------------------------------------------------------------------------------
    E(T,
"""				value > 9
			}
		}
	}
}
can_spend_huge_ps_trigger = {
""",
"""				value > 9
			}
		}
		AND = { # 2.42 (Supernatural): the Warlock's own pool
			has_trait = warlock
			NOT = { has_trait = archmage } # he pays from the Mage's pool (spend_*_ps_effect), so that is the one that counts
			has_trait_xp = { trait = warlock track = power_saturation value > 9 }
		}
	}
}
can_spend_huge_ps_trigger = {
""")
    # can_spend_huge_ps_trigger: the Warlock arm rides on the 2.38 entry (#17) in apply_upstream_edits.py, whose text it sits inside
    E(T,
"""				value < 100
			}
		}
		NOR = {
			has_trait = archmage
			has_character_modifier = power_saturated1
""",
"""				value < 100
			}
		}
		AND = { # 2.42 (Supernatural): a Warlock can take more until his own pool is full
			has_trait = warlock
			NOT = { has_trait = archmage }
			has_trait_xp = { trait = warlock track = power_saturation value < 100 }
		}
		NOR = {
			has_trait = archmage
			has_trait = warlock # 2.42 (Supernatural): judged by his pool above, never by the one charge
			has_character_modifier = power_saturated1
""")
    # ---- 6, step 2: metamagic --------------------------------------------------------------------------
    E(V,
"""							track = power_saturation
							value = 10
						}
					}
					else_if = {
						limit = {
							NOR = {
""",
"""							track = power_saturation
							value = 10
						}
					}
					else_if = { # 2.42 (Supernatural): the Warlock's own pool
						limit = { has_trait = warlock }
						add_trait_xp = { trait = warlock track = power_saturation value = 10 }
					}
					else_if = {
						limit = {
							NOR = {
""")
    # ---- 6, step 3: his own source ---------------------------------------------------------------------
    E(D,
"""		has_perk = forbidden_ritual_p7_perk
		is_imprisoned = no
		can_be_power_saturated_trigger = yes
""",
"""		OR = { # 2.42 (Supernatural): the Warlock has his own way to the ritual (WORK-ORDER-2.42 v3, 6 step 3)
			has_perk = forbidden_ritual_p7_perk
			has_perk = warlock_perk
		}
		is_imprisoned = no
		can_be_power_saturated_trigger = yes
""")
    E('events/ev1.txt',
"""		scope:potential_sacrifice ?= { # 2.38h (Supernatural): there may be no one to drain
			add_character_modifier = lifestolen_modifier
		}
""",
"""		scope:potential_sacrifice ?= { # 2.38h (Supernatural): there may be no one to drain
			add_character_modifier = lifestolen_modifier
		}
		gain_huge_ps_effect = yes # 2.42 (Supernatural): a stolen life is power (the Lifestealer is a Black Magic perk)
""")
    # ---- 6, step 4: the Warlock's track matches the Mage's (Thomas, 20 Nov 2026) -------------------------
    E(TR,
"""				health = 0.4
				e_power_terrain_advantage = 2
				e_fire_terrain_advantage = 2
				e_kinetic_terrain_advantage = 2
			}
			50 = {
				e_power_terrain_advantage = 2
				e_fire_terrain_advantage = 2
				character_travel_safety = 10
""",
"""				health = 0.2 # 2.42 (Supernatural): the Warlock's pool pays what the Mage's does (was double at every step)
				e_power_terrain_advantage = 1
				e_fire_terrain_advantage = 1
				e_kinetic_terrain_advantage = 1
			}
			50 = {
				e_power_terrain_advantage = 1 # 2.42
				e_fire_terrain_advantage = 1
				character_travel_safety = 5
""")
    E(TR,
"""				e_power_terrain_advantage = 2
				prowess = 10
				advantage = 10
""",
"""				e_power_terrain_advantage = 1 # 2.42 (Supernatural): as the Mage's
				prowess = 5
				advantage = 5
""")
    # ---- Triangulation (W3) ----------------------------------------------------------------------------
    E(T,
"""has_access_to_magic_triangulation_trigger = {
	OR = {
		has_perk = mage_p4_perk
""",
"""has_access_to_magic_triangulation_trigger = {
	OR = {
		has_perk = magic_triangulation_p5_perk # 2.42 (Supernatural): the perk that says it enables this now does (jonlevir, 21 Sep 2026)
		has_perk = mage_p4_perk
""")
    E(D,
"""		custom_description = {
			text = not_archmage_txt
			is_true_mage = yes
		}
		custom_description = {
			text = is_incapable_custom
""",
"""		custom_description = {
			text = not_archmage_txt
			OR = { is_true_mage = yes has_trait = warlock } # 2.42 (Supernatural): the access trigger already admitted a Warlock; this line did not
		}
		custom_description = {
			text = is_incapable_custom
""")
    # ---- W1: the Black Grimoire rewards a Warlock's focus too (Angel DeStaar, 18 Sep 2026) ---------------
    E(V,
"""				has_focus = witch_focus
				has_focus = arcane_focus
			}
		}
		send_interface_toast = {
			title = study_blackgrimoire_decision
			custom_tooltip = ev2.47.a_ct
""",
"""				has_focus = witch_focus
				has_focus = arcane_focus
				has_focus = blackmagic_focus # 2.42 (Supernatural): Supernatural's third magic focus; Witchcraft has no such focus, so the gap was ours
			}
		}
		send_interface_toast = {
			title = study_blackgrimoire_decision
			custom_tooltip = ev2.47.a_ct
""")
    # ---- W2: potions and the four aging traits (Tanky1000, 18 Sep 2026) --------------------------------
    E(I,
"""					if = { limit = { has_trait = disfigured NOT = { has_character_flag = abdul_dude } }
""",
"""					# 2.42 (Supernatural): Regeneration mends the body's old age, not the mind's (Withering Mind is the Elixir of Youth's)
					if = { limit = { has_trait = fragile_bones } remove_trait = fragile_bones }
					if = { limit = { has_trait = faltering_heart } remove_trait = faltering_heart }
					if = { limit = { has_trait = clouded_eyes } remove_trait = clouded_eyes }
					if = { limit = { has_trait = disfigured NOT = { has_character_flag = abdul_dude } }
""")
    E(I,
"""					hidden_effect = {
						set_age = new_young_age_value
					}
					custom_tooltip = drink_pot5_decision_ct
""",
"""					hidden_effect = {
						set_age = new_young_age_value
					}
					healing_old_age_effect = yes # 2.42 (Supernatural): made young again, the marks of old age go with the years
					custom_tooltip = drink_pot5_decision_ct
""")

    # ---- 2, D5: the demon tree for merchant companies and adventurers (it had no government block at all) ----
    DP = 'common/lifestyle_perks/00_magic_3_demon_tree_perks.txt'
    _demon_blocks = ("\t# 2.42 (Supernatural): Merchants of the Night. A demon who keeps a company's books, or lives on the road.\n"
                     "\tgovernment_character_modifier = {\n\t\tflag = government_has_merchant_company\n"
                     "\t\ttrait_track_creditor_xp_gain_mult = 0.25\n\t\ttrade_competitiveness_add = 15\n\t}\n"
                     "\tgovernment_character_modifier = {\n\t\tflag = government_is_landless_adventurer\n"
                     "\t\towned_contract_scheme_success_chance_add = 15\n\t}\n")
    E(DP,
"""			text = deals_with_mortals_perk_effect2	#dark champion
		}
	}
}
""",
"""			text = deals_with_mortals_perk_effect2	#dark champion
		}
	}
""" + _demon_blocks + "}\n")
    E(DP,
"""	trait = cyrographer
	parent = depravity_perk
""",
"""	trait = cyrographer
	parent = depravity_perk
""" + _demon_blocks)

    # ---- 2, D3: the year a contract falls due, stamped where the soul is taken (the only writer of my_soul_owner) ----
    E(V,
"""		scope:recipient = {
			remove_mortal_soul_effect = yes
			set_variable = {
				name = my_soul_owner
				value = scope:actor
			}
		}
""",
"""		scope:recipient = {
			remove_mortal_soul_effect = yes
			set_variable = {
				name = my_soul_owner
				value = scope:actor
			}
			spn_soul_stamp_due_effect = yes # 2.42 (Supernatural): Cash In a Soul prices a contract by the years it has left
		}
""")
    # A contract that was cashed in or freed is not collected: the collection checks that the soul is still held.
    E('events/ev8.txt',
"""	trigger = {
		is_alive = yes
		exists = scope:actor
		scope:actor = {
			is_alive = yes
			is_imprisoned = no
		}
	}
	on_trigger_fail = {
""",
"""	trigger = {
		is_alive = yes
		has_variable = my_soul_owner # 2.42 (Supernatural): a freed soul (exorcism, Cash In a Soul) is not collected years later
		exists = scope:actor
		scope:actor = {
			is_alive = yes
			is_imprisoned = no
		}
		# ...and only by the demon who holds it now, on the contract that is due: a soul freed and signed again is not
		# collected early by the first contract's visit (which stays queued).
		var:my_soul_owner = scope:actor
		OR = {
			NOT = { has_variable = spn_soul_due_year }
			var:spn_soul_due_year <= current_year
		}
	}
	on_trigger_fail = {
""")
    # ---- 2, D2: a demon who heads a merchant company can pay for a soul in coin ---------------------------
    E('events/ev8.txt',
"""	option = {
		name = ev8.15.0.a	#refuse
""",
"""	option = { # 2.42 (Supernatural): a demon merchant pays in coin; the soul is owed all the same
		name = spn_ev8.15.coin
		trigger = {
			has_gdp_dlc_trigger = yes
			scope:actor = {
				government_has_flag = government_is_merchant
				gold >= root.gdp_loan_money_max_gold_value # the demon pays it out of his own purse (magic_ev8.17)
			}
		}
		show_as_tooltip = {
			add_gold = gdp_loan_money_max_gold_value
			remove_mortal_soul_effect = yes
		}
		hidden_effect = { add_character_flag = { flag = spn_cyro_coin_flag days = 5 } }
		scope:actor = {
			trigger_event = magic_ev8.17
		}
		ai_chance = {
			base = 5
			modifier = { add = 40 has_trait = greedy }
			modifier = { add = 40 gold < 0 }
		}
	}

	option = {
		name = ev8.15.0.a	#refuse
""")
    E('events/ev8.txt',
"""		spend_standard_ps_effect = yes
		if = {
			limit = {
				scope:recipient = {
					has_character_flag = select_better_offer_cyro_flag
""",
"""		spend_standard_ps_effect = yes
		if = { # 2.42 (Supernatural): the mortal took the bargain in coin (magic_ev8.15, spn_ev8.15.coin): gold, and no magic
			limit = { scope:recipient = { has_character_flag = spn_cyro_coin_flag } }
			scope:recipient = { remove_character_flag = spn_cyro_coin_flag }
			pay_short_term_gold = { # the demon's own coin, not gold from nowhere
				target = scope:recipient
				gold = scope:recipient.gdp_loan_money_max_gold_value
			}
		}
		else_if = {
			limit = {
				scope:recipient = {
					has_character_flag = select_better_offer_cyro_flag
""")
    # ---- 3, M2: a brewed potion lifts the brewer's home market ------------------------------------------
    E(D,
"""		gain_al_xp_small_effect = yes
		custom_tooltip = create_potion_decision_ct
""",
"""		gain_al_xp_small_effect = yes
		spn_potion_brewed_market_effect = yes # 2.42 (Supernatural): a mage merchant's medicines are trusted (Medicaments, vanilla's good)
		custom_tooltip = create_potion_decision_ct
""")
    # ---- log, 20 Nov: the AI artifact seeker claimed a relic it already held (12 error lines in 37 years) --------
    E(V,
"""				NOT = {
					has_personal_artifact_claim = scope:art1
				}
			}
			add_personal_artifact_claim = scope:art1
""",
"""				NOT = {
					has_personal_artifact_claim = scope:art1
				}
				NOT = { any_character_artifact = { this = scope:art1 } } # 2.42 (Supernatural): not one he already holds
			}
			add_personal_artifact_claim = scope:art1
""")
    # ---- review, 20 Nov: Hell's envoy (magic_ev2.11) no longer calls on a soul that was freed, or voids another demon's
    # contract. The branch ran whenever the first demon was dead, whatever had happened to the soul since.
    E('events/ev8.txt',
"""			limit = {
				OR = {
					NOT = {
						exists = scope:actor
					}
					scope:actor = {
						is_alive = no
					}
				}
			}
			remove_variable = my_soul_owner
""",
"""			limit = {
				has_variable = my_soul_owner # 2.42 (Supernatural): a freed soul is left alone; another demon's contract is not voided
				OR = {
					NOT = {
						exists = scope:actor
					}
					AND = {
						scope:actor = {
							is_alive = no
						}
						var:my_soul_owner = scope:actor
					}
				}
			}
			remove_variable = my_soul_owner
""")
