# Supernatural — Crusader Kings III

Vampires, werewolves, hybrids, hunters, witches and demons for Crusader Kings III.

This repository holds the mod's source. It exists so Supernatural can be installed without Steam, and so
every released version stays available. The files here are the same files the Workshop copy ships.

| | |
|---|---|
| Steam Workshop | https://steamcommunity.com/sharedfiles/filedetails/?id=2856525601 |
| Mod page | https://dlonem.com/mods/supernatural |
| Discord | https://discord.gg/Efvd2B97xx |
| Downloads | https://github.com/Dlonem/CK3SupernaturalMod/releases |

## Installing without Steam

Take the archive from the [latest release](https://github.com/Dlonem/CK3SupernaturalMod/releases/latest) —
not the green **Code** button, which gives you the repository rather than something the launcher can read.

Extract it and drop **both** items into your CK3 mod folder:

| | |
|---|---|
| Windows | `Documents\Paradox Interactive\Crusader Kings III\mod\` |
| macOS | `~/Documents/Paradox Interactive/Crusader Kings III/mod/` |
| Linux | `~/.local/share/Paradox Interactive/Crusader Kings III/mod/` |

so that you end up with this:

```
mod\supernatural_mod.mod
mod\supernatural_mod\
```

Both are required. `supernatural_mod.mod` is the file the launcher reads; `supernatural_mod\` is the mod.
Start the launcher and Supernatural appears under **Mods**, ready to add to a playset.

### If it does not show up in the launcher

Nearly always one of two things:

- **Only the folder got copied.** The launcher does not scan folders — it reads `.mod` files. With no
  `supernatural_mod.mod` beside the folder, there is nothing for it to find.
- **The `.mod` file is the launcher's copy rather than this one.** The launcher rewrites `path=` to an
  absolute path on the machine that uploaded the mod, which resolves to nothing on anyone else's. The
  `.mod` in this repository is the portable form — `path="mod/supernatural_mod"`, no `remote_file_id`.
  If yours differs, replace it with a fresh copy from the release.

`supernatural_mod/descriptor.mod` is a different file and is not what the launcher reads. Leave it as it is.

## Load order

Supernatural runs on its own. Alongside A Game of Thrones it needs the compatibility patch, and the order
matters:

1. A Game of Thrones
2. AGOT submods
3. AGOT: The Long Night & Azor Ahai *(optional)*
4. **Supernatural**
5. [AGOT: Supernatural & The Long Night Compatibility Patch](https://steamcommunity.com/sharedfiles/filedetails/?id=3780270228) — **always last**

In multiplayer every player needs the same mods at the same positions.

## Repository map

| | |
|---|---|
| `supernatural_mod/` | the mod — this is what the game loads |
| `supernatural_mod.mod` | the launcher descriptor; the portable one, keep it |
| `CHANGELOG.md` | version history |

Release archives are attached to [Releases](https://github.com/Dlonem/CK3SupernaturalMod/releases) rather
than committed.

## Reporting bugs

The [Discord](https://discord.gg/Efvd2B97xx) is the fastest route, and the Workshop comments are read.
Issues here work too. A report is much more useful with your load order and, if the game threw errors,
`Documents\Paradox Interactive\Crusader Kings III\logs\error.log`.
