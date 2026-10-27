# FS-X-VFX

FirstSelfie's private **Claude Code plugin marketplace** for cinematic CGI / VFX, motion design and video production skills.

| Plugin | What it does | Commands |
|---|---|---|
| [vfx-intro](plugins/vfx-intro) | Cinema-grade 3D/VFX intros (Think School / Netflix-doc style) from a reference video, an idea or keywords. Blender + After Effects + ffmpeg, end to end. | `/vfx-intro`, `/vfx-setup` |

## Install (team members)
1. Get access to this private repo (ask NK-EMPIRE), install [Git](https://git-scm.com) and sign in once. A `git clone` of this repo should work without errors.
2. Install [Claude Code](https://claude.com/claude-code).
3. Run:
```bash
claude plugin marketplace add NK-EMPIRE/FS-X-VFX
claude plugin install vfx-intro@fs-x-vfx
```
   Or clone the repo and run `setup\install.ps1` (Windows) / `bash setup/install.sh` (macOS/Linux), which installs every plugin in the catalogue.
4. Restart Claude Code and run `/vfx-setup` once. It checks Blender, After Effects, ffmpeg, Python, the GPU and fonts.

Inside Claude Code you can also type `/plugin` → *Add marketplace* → `NK-EMPIRE/FS-X-VFX`.

**Update later:**
```bash
claude plugin marketplace update fs-x-vfx
claude plugin update vfx-intro@fs-x-vfx
```

## Use
```
/vfx-intro The Richest Temple in India: a gold temple bell cracks and explodes into the title
/vfx-intro recreate and beat this reference: D:/refs/intro.mp4
```

## Repository layout
```
.claude-plugin/marketplace.json   catalogue of all plugins (add new ones here)
plugins/<plugin>/                 one folder per plugin
  .claude-plugin/plugin.json      name, version, description
  skills/<skill>/SKILL.md         skills (+ references/, scripts/, examples/)
  commands/<cmd>.md               slash commands
templates/plugin-template/        copy this to start a new plugin
setup/install.ps1, install.sh     one-shot installers for team machines
CONTRIBUTING.md                   how to add or update a plugin / skill
CHANGELOG.md                      release notes
```
