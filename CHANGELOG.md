# Changelog

Version history for **Supernatural**. These are the notes written for each Steam Workshop update, kept here so the
repository carries its own history.

Newest first. Notes for 2.29 and earlier are on the Workshop's
[change notes page](https://steamcommunity.com/sharedfiles/filedetails/changelog/2856525601).

---

## 2.37 — The Six Hides

Six ancient wolf hides are loose in the world: Silverback, Timber, Tundra, Graybeard, Midnight and Alpha. Each has a will of its own and chooses a werewolf or hybrid who fits it, and its Champion is stronger, lives longer, never grows frail and can hear magic. Most start as relics in shrines at holy sites. Take one by holding the county, by siege or on pilgrimage, or pay someone to bring it back with Send for a Hide. Wolves can now found and join packs, rise in Pack Standing, challenge the alpha for the pack, and meet at the new Werewolf Gathering. AI wolves challenge an alpha only for a reason: he is too weak to lead, cruel to his pack, or their enemy. A hide an AI leaves idle for ten years slips away to find a wolf. Two new game rules control the hides and the packs. The mod's death reasons now read as proper sentences, a few broken links and icons are fixed, and a demon can now have a child with a werewolf or hybrid (reported by Jean de Valois). It works on a running save: the hides turn up within the year.

Questions about the mod? Read the wiki: [dlonem.com/mods/supernatural/wiki](https://dlonem.com/mods/supernatural/wiki/)

**Playing with AGOT?** AGOT hasn't been updated for 1.20 yet. Until it and the compatibility patch are, play on CK3 1.19 with Supernatural 2.35a from [GitHub](https://github.com/Dlonem/CK3SupernaturalMod/releases/tag/v2.35a) ([how to install it](https://dlonem.com/mods/supernatural/download/)).

---

## 2.36 — Crusader Kings III 1.20

Supernatural now runs on CK3 1.20. On 1.20, 2.35a crashed as a new game started; 2.36 fixes that and moves the mod onto 1.20's rites. The vampire, werewolf, hybrid and hunter doctrines now sit on every rite, and your rite weighs your feeding, killing and turning others through Spiritual Fulfillment. It only condemns them once you are known for what you are. Feeding only leaves a trail when there is a body or somebody talks. French, German, Spanish, Korean, Polish and Chinese players now see English instead of raw keys wherever a translation is missing. Start a new game with this version.

Questions about the mod? Read the wiki: [dlonem.com/mods/supernatural/wiki](https://dlonem.com/mods/supernatural/wiki/)

**Playing with AGOT?** AGOT hasn't been updated for 1.20 yet. Until it and the compatibility patch are, play on CK3 1.19 with Supernatural 2.35a from [GitHub](https://github.com/Dlonem/CK3SupernaturalMod/releases/tag/v2.35a) ([how to install it](https://dlonem.com/mods/supernatural/download/)).

---

## Hotfix 2.35a — The witch you let live

A hotfix for four faults that shipped with The Hunt. No new content, and nothing here breaks a save.

### Bug Fixes

- **Turning down a witch hunt no longer kills the witch.** "Someone spotted a witch" used to conjure a woman out of nothing, so the two options that decline the hunt quietly killed her afterwards — otherwise she was left standing in the world as set dressing. In 2.35 that event was rebuilt to find a *real* person instead: someone in your court, in the local lord's court, the lord himself, or a witch whose secret you already keep. The old tidy-up was still attached, and it was now pointed at real characters. Declining killed them outright, with no notification to whoever owned them. This is why witch dynasties were going missing after you married them off: she moves into her husband's court, his liege gets the event, he decides it sounds too dangerous, and she is gone. The tidy-up now only ever touches a witch the mod invented.
- **The world stops filling with hunters and monsters.** 2.35 raised how often the witch and monster sighting events fire by about seventeen times, to fix how rarely a hunter ever heard anything. That was the right complaint and the wrong lever: the pulse behind those events does not run for hunters, it runs for every ordinary ruler on the map. Both events create people — one condemns a witch, the other conjures a werewolf or a vampire and hands out the hunter trait on a coin flip — and every new hunter then subscribed to the same pulse. Hunters keep the faster rate, because they are who the news is for. Everyone else is back to the rate the mod ran at before 2.35, which is roughly once in a lifetime.
- **Monster Sighting had no conditions on it at all.** Not a loose check — none. It could fire on the imprisoned, the incapable, or a character mid-transformation. It is now gated the same way its twin, the witch sighting, always has been.
- **An ordinary murder no longer reads as a creature's kill.** The county trail system recorded who the killer was and never looked at how the victim died, so any assassination by anyone carrying a supernatural trait — or just a witch's secret, which is most practitioners — was written up as a creature kill and offered you the body to dispose of. It now requires the killer to have actually been present. Murdering someone in your own hall can still trip it; closing that properly means reworking every kill site in the mod and is a job for the next full release, not a hotfix.

### Notes

- Safe to drop onto a running save. Nothing needs a new game.
- Characters already in House Hellion stay where they are — nothing in the mod moves anyone out of a house. No *new* witches are added to it; that was fixed in 2.35.
- Reported by Plato in the Cave and Angel DeStaar, both of whom read the code and named the event. That is why this took a day.

---

## 2.35 — The Hunt

Something has been killing people in your counties. Until now nobody did anything about it. Now the county remembers, the lord hears about it, and somebody rides out.

### New: trails

- **A kill leaves a mark on the county it happened in.** One body is usually just a body. A second inside the year is not, and the county starts talking. Prowling counts for less than a kill, and covering your tracks badly counts for more than you would like.
- **Three incidents and the lord finds out.** He can look into it himself, put his spymaster on it, post a bounty for an adventurer, send for a hunter by name and pay him when it is done — or write it off as superstition and watch his county bleed.
- **Trails outlive the creature that made them.** Kill the thing everyone was watching and the county still has a mark, a memory and, often, another monster. Suspicion lands on whoever is still there.
- A county that turns three hunters away stops attracting them. Nobody will come — unless you are good enough that nobody else would.

### New: the Trailsman

- **A court position that reads the countryside for you.** Three tasks: find a trail, run it down to the thing standing at the end of it, or walk your borders in a year when nothing is out there.
- A landless adventurer's camp officer does the same work. He reads the world's trails, not just the ground under the tent.

### New: the hunt

- **A full activity.** Hunt a creature or hunt a witch — the second runs on suspicion alone, which is the darker one.
- **Bring what you think you will need.** Silver, stakes, dogs, men. Each of them changes what happens at the door, and bringing the wrong kit is its own answer.
- **Take an apprentice and he finishes his training in the field** — the only place that lesson has ever meant anything.
- Landless hunters reach far further than landed ones, because a man with a horse and no land goes where the work is. A duke can hunt anywhere in his king's realm.

### New: the other side of the door

- **The creature gets the other half of the scene, and real answers.** Stand and fight. Go to ground. Look him in the eye. Send your progeny out to die in your place. Let the wolf out. Or tell him there is worse than you in this land, and be right.
- **Send somebody else and the hunter is told.** He gets to kill the one who was sent, or refuse the trade and go back to the door — where there is nobody left to send out through it.
- **Get away and the news travels.** Warn your get, warn the one who made you, warn all of them — or point the hunt at your own blood and let them have it instead.
- Demons do not run. They argue, and they may offer you a bargain you will still be paying for in thirty years.
- Cover your own kills. Pay it off, hide the body, or put it on a neighbour who had it coming.

### Fixes

- **Witch hunts could never actually happen.** One gate, closed since the feature shipped. They work now.
- **Two files never loaded at all**, so no trail was ever written and no hunter ever moved. Both are loading.
- **Hunters are told about witches and monsters roughly twenty times more often.** Three separate dampeners were multiplied together; the expected wait for that letter was over two hundred years.
- Secret witches leave trails, not just the ones who were never careful.
- Compelling someone for their secrets no longer throws an error instead of revealing them.
- Hunter regiments now need the Hunter Academies perk, and the perk says so.
- Hosting a hunt costs half what it did. Thousands of script errors a session are gone.

### Note

- Safe to drop onto a running save.
- If you run A Game of Thrones, pair this with the AGOT: Supernatural & The Long Night Compatibility Patch 1.1.3b.

---

## Hotfix 2.34a — The people who made you know what you are

A hotfix for one bug. No new content.

### Bug Fixes

- **Your spymaster and the scrying orb stop "finding" secrets you already know.** Find Secrets and scrying both pick a secret in your court that the game says you have not learned, and the base game leans toward family. Supernatural was creating its secrets with nobody recorded as knowing them — a child born to two werewolves came of age with a secret his parents were never told; a vampire you embraced in an event carried a secret the game did not credit you with; a hunter you trained, the same. So the werewolf father kept being told his werewolf son is a werewolf. Now, the moment one of the four supernatural secrets is created, the people who made that character are told: the maker, the sire whose blood it was, the trainer, and a living supernatural parent for the born. Every road into a creature trait goes through the same line, so no path is missed.
- **Running games are repaired once.** The first time a save is loaded under 2.34a, every existing supernatural secret is shown to the same people. Nothing else about your save changes.

### Notes

- Safe to drop onto a running save.
- Reported by Mertehan. This is separate from the 2.31c fix that let spymasters uncover every secret type again.

---

## 2.34 — The Blood Remembers Who

Your character now remembers how they became what they are, and who did it to them. The maker remembers too. A hundred years on, a dead teacher, a child born into the wolf — those memories start to talk back.

### New: memories

- **Every turning is remembered.** Made a vampire, clawed into the wolf, made a hybrid, trained as a hunter — dated, in your own words, naming the one who did it when there is one and staying vague when there is not. Forced turnings read as forced. Dying in battle and rising has its own.
- **The other side remembers you.** The maker opens a vein for "my friend", "my lover", "my son" — whatever you are to them. The clawer remembers the gift. Asking to be turned is remembered once.
- **The first hunter who came for you** — killed, escaped, or sent home — is remembered once. Only the first.
- **Six one-off events grow out of those memories.** The trainer who started you, a year in the ground. A hundred years since you died and did not stay dead. Watching a child who was born into what you were clawed into. A hybrid whose two bloods have drifted apart. A demon-blooded fourteen-year-old. Thirty years a Mage.
- **Memories are private**, like a murder. You see your own; nobody browsing a character page learns who is a vampire from it.

### New: the compel

- **A vampire or hybrid with a maxed track can look a hunter in the eye and send them home** — 20 Vampirism, hunter lives, hunter remembers nothing. A trained hunter knows about compulsion and cannot be turned. Player-only, like the whole confrontation chain.
- The hunters who come for you finally have skill of their own, so the fights they start mean something.

### Invoke the Bond

- **Every order shows its price.** "Be Obedient" is now "You Owe Me" — it was always a favour hook. Four new orders: Give me your Prisoners, Release your Prisoners, Break your Betrothal, Take my Culture.
- Marry Me and You Owe Me had their labels swapped and one of them did nothing. Refusing the Bond never cost anything; it does now. Give me the Titles charged 60 and said 40. Being your progeny's regent added a hidden 10 to every order. All fixed.

### Hunters and witches

- **True Witch Hunter and True Monster Hunter** cap the two hunter trees, like True Vampire and True Werewolf.
- **Witch hunts open on the witch-hunting track or the tree's first perk**, not the capstone. The witch-hunter quest, the duel roll and the heir now make a real hunter instead of handing out the capstone.
- Protection Runes and Combat Spells did nothing. They do now, and Combat Spells reaches the Witcher's elixirs.

### Fixes

- **Mage, Warlock and True Witch are granted again.** Two of them excluded each other, and a hunter could buy a perk whose trait it could never hold. Reported three times — thank you.
- Supernaturals who started their own perk tree could never open another lifestyle's tree again. The trigger now mirrors vanilla's exactly, for all nine trees.
- AI vampires, werewolves and hunters pick their own focus 25% more often than an ordinary lord picks his — landed or landless. The three magic trees have AI weighting at last.
- Vampires can feed on tribal holdings. Demons no longer catch diseases. Witches are no longer randomly turned into werewolves. Fallen hunters lose the whole hunter identity, not half of it. A newly turned character no longer keeps the wound that was about to kill them.

### Note

- Safe to drop onto a running save. Existing dead makers and trainers are picked up by the new events on the first pulse.
- If you run A Game of Thrones, pair this with the AGOT: Supernatural & The Long Night Compatibility Patch 1.1.3. Nothing in 2.34 needs a patch change.

---

## 2.33 — The Blood Remembers

Fall in battle with a vampire's blood in you and you do not die. You wake three days later on the wrong side of it, and you have about a month to decide what you are.

### New: dying in battle with vampire blood in your system

- **The blood catches the blow that would have killed you.** If a mortal carrying vampire blood takes a fatal hit as a knight, he goes down, comes off the field, and wakes up three days later — no pain, no heartbeat, and a wound that has closed over clean.
- **Three events, and you are not told what is happening.** You wake first and understand nothing. A fortnight later the hunger arrives, and with it the memory of a cup somebody handed you months ago and made very little of at the time.
- **Feed, ask, or refuse.** Drain a dying captain, a knight still standing, or a stranger on the field. If the one who gave you the blood is there, ask them instead and nobody has to die. Or refuse, and get one more fortnight to change your mind before it is decided for you.
- **Refuse twice and you die of it** — a new death reason, "Refused the Blood."
- **Whoever gave you the blood becomes your Maker.** Full Maker and Progeny relation, not just a note in a tooltip.
- **The AI weighs this like a person would.** A twenty-year-old with his whole life ahead of him takes the blood far more often than a man of seventy. Stubborn and zealous characters refuse; the craven and the gluttonous do not. Having small children pushes hard toward living.
- **Works landed or landless, and needs no compatibility patch.**

### Fixes

- **Maker and Progeny are now set on every way you turn.** The relation only ever existed if a vampire turned you through the interaction. Dying with blood in your system, asking to be turned, working out what was in you, or experimenting with it all made a vampire with no Maker at all. Five paths, one fix.
- **Supernatural's men-at-arms no longer throw errors when a war ends.** All four types asked whether the recruiter was a werewolf or a vampire in a context where there is no character to ask about.

### Compatibility

- **Dragonriders are left to A Game of Thrones.** A rider in the air is resolved by their rules; the blood catches him on foot like everyone else.
- **The blood goes before the fire.** If you are blessed by R'hllor and carrying vampire blood, the blood takes the fall first and is spent. Your blessing is untouched and catches the next one. Both systems, in order, instead of one silently eating the other.

### Note

- Safe to drop onto a running save.
- If you run A Game of Thrones, pair this with the AGOT: Supernatural & The Long Night Compatibility Patch 1.1.3.

---

## Hotfix 2.31c

A small pass. Two bug fixes, and a tidy-up that only shows itself if you run a compatibility patch.

### Bug Fixes

- **Fixed the Mikaelson men keeping their beards.** The rule that shaves them was correct and had been dead script for a while — the group held two entries with the same name and the later one won, and four of the five comparisons pointed at Mikael instead of their own character. Both fixed.
- **Fixed the version popup announcing the previous version.** Third place the version number lives, and it had fallen behind again.

### Compatibility

- **Ten more places now ask "is this a valid target?" before changing what someone is.** The mod already asked at every interaction you click. It did not ask on the paths you don't click — the yearly trait sweep, the witchcraft dynasty legacy, a mythical legend's reward, a court mage picking his own curse victim, a cult priest appointment, the place-of-power sweep, the werewolf bite chain, and a war whose victory converted every character of an entire faith at once. All of them go through the same check now.
- **On its own this changes nothing.** The check answers yes for everyone unless a compatibility patch says otherwise. If you run A Game of Thrones with the compatibility patch, it means dragons and the walking dead are no longer quietly eligible for any of the above.

### Note

- Safe to drop onto a running save.
- If you run A Game of Thrones, this pairs with the AGOT: Supernatural & The Long Night Compatibility Patch 1.1.3 — the beard fix and the compatibility work each need both mods updated to reach you.

---

## Hotfix 2.31b

A compatibility and bug-hunting pass. Save-safe — no new game needed.

### Playing alongside A Game of Thrones

Supernatural was written for a world where every character is a person. Loaded next to a total conversion that is no longer true, so the mod now asks first.

- **Dragons cannot be turned, compelled, dominated, cursed or healed.** They are not people. Every magic and creature interaction now checks, and says so in the tooltip instead of failing silently.
- **The dead are excluded too.** Wights, Others and the Night King, when The Long Night is installed. A corpse with somebody else's will in it has nothing for a spell to take hold of.
- This costs nothing in a normal game. Without a total conversion loaded, every character is still a valid target, exactly as before.

### Fixes

- **Spymasters can uncover every secret type again.** The mod was replacing the base game's list of fourteen with its own four, and disabling the fallback — so a spymaster on Find Secrets could only ever turn up supernatural ones. All eighteen are back, and the fallback works.
- **Perk point alerts work for the four creature focuses.** Vampires, werewolves, hybrids and hunters were never told they had a point to spend.
- **130 spell tooltips showed a raw key instead of a sentence.** Things like "spn_cannot_be_turned_custom has no localization" in place of the reason. Every one of them reads properly now, in all supported languages.
- **The Magic Council's summoned host arrives at full strength.** Three of its five regiment types did not exist, so most of the army never showed up.
- **Dark temples and magic academies no longer error for landless casters.**
- **The eight Originals use the current portrait gene set.** Their DNA predated several gene additions, so their portraits were being assembled from an incomplete description.
- **Supernaturals keep modern hair.** The mod carried an old copy of the base game's hair rules, which quietly reverted every character to a much older set. Rebuilt against the current game — and supernaturals still never go bald.

### Changes

- **Yearly NPC trait sweeps no longer walk every character at once.** Six separate passes over the entire world every 1 January, replaced with one check per character spread across the year. Same result, a fraction of the cost.
- A duplicate on_action warning at load is gone.

**Running Supernatural with A Game of Thrones?** Use the Compatibility Patch, and load it last.

---

## Hotfix 2.31a

A disease-immunity fix on top of 2.31.

- **Vampires, werewolves and hybrids are properly immune to disease.** The immunity was only ever applied on some of the ways you can be turned, so a lot of supernaturals never had it — and hybrids had it removed outright by the transformation, leaving them worse off than the werewolf they used to be. A hybrid could catch consumption.
- **Consumption is cured when you turn,** like every other illness. It was the only disease missing from that list.
- **Existing characters are repaired automatically.** No new game needed — anyone already turned gets their immunity back on the next yearly tick.

Nothing else in 2.31 has changed.

---

## 2.31

A bug-hunting pass. Several of these have been reported for a long time — thank you for the patience.

### Fixes

- **Master of Shadows and Vampire Nest can be clicked again** — both sat outside the perk tree's clickable area, so the vampire tree couldn't be finished. Two monster-hunter perks had the same fault. *CleverPolarBear, Lord Zymeth, Noa3, ТоЬЬыэЯ™*
- **Scholarly education gives back its two lost domain slots** — every ruler in the game, supernatural or not. *Angel DeStaar*
- **Pregnancy no longer collapses after your first supernatural child** — vampires, werewolves, hybrids and demons alike. *Dr. Baphomet, valdijan72, Explode_Toad*
- **Demon-blooded children now grow into demons in their twenties.** *Omni*
- **All ten base-game secret descriptions load again.** The 2.30 fix was correct and had never once taken effect.
- Set Visual Age no longer reverts on your next birthday; a quarter of all NPC werewolves were being created as vampires; glabro form is detected correctly again.

### Playing better with other mods

- **Supernatural now replaces 4 base-game scripted triggers instead of 42.** One file was a whole renamed copy of a base-game file. The other 38 are gone, so the base game wins again — and so does any other mod that edits them.
- **Four base-game traits restored** — Scholar, Heresiarch, Leper and Scholarly education, each frozen years out of date. Two files that were identical copies of base-game files are gone too.
- **The witch-sighting chain works in total conversions now** — it required a base-game world region, which conversions don't define, so it silently never fired there.

### Changes

- **A werewolf bite now festers for one to three years before it decides**, instead of turning you on the spot — with stages, a cost while you carry it, and an ending shaped by how those years went. Every werewolf encounter routes through it now.
- **Survive a Lycan and a Hunter may spare you** — burn the wound clean and train you, or come back once the fever breaks if you're still yourself.
- **The peddler's elixir no longer tells you what you're about to become**, and may do nothing at all.
- **Feeding invitations only reach people who could plausibly know what you are** — not every vampire on the map.
- **Performance:** several map-wide character sweeps narrowed, and a source of constant error-log spam removed.

### Load order with AGOT

1. A Game of Thrones
2. AGOT submods
3. AGOT: The Long Night & Azor Ahai *(optional)*
4. Supernatural
5. AGOT: Supernatural & The Long Night Compatibility Patch — **always last**

Reported by CleverPolarBear, Lord Zymeth, Noa3, ТоЬЬыэЯ™, Omni, Angel DeStaar, Explode_Toad, manic_Mage, AZTRAGOS, valdijan72 and Dr. Baphomet. Keep them coming.

---

## 2.30

- **Fix:** secret descriptions. The mod's custom localization was *replacing* the base game's secret-description list instead of adding to it — which deleted all ten vanilla secret descriptions, fallback included, for every player. All ten are back; the four supernatural secrets are untouched.
- **Fix:** the magic-artifact pulse no longer floods the error log (and slows the game) when it runs with no player found — observer mode included.
- **New companion mod:** **AGOT: Supernatural & The Long Night Compatibility Patch**. If you play Supernatural with A Game of Thrones, both mods define twenty-two of the same things — marriages, secrets, disinheritance, the witch ritual, birth events — and whichever loads later silently erases the other's. The patch merges every one of them. Subscribe, put it **last** in your playset, done.

### Load order with AGOT

1. A Game of Thrones
2. AGOT submods
3. AGOT: The Long Night & Azor Ahai *(optional)*
4. Supernatural
5. AGOT: Supernatural & The Long Night Compatibility Patch — **always last**
