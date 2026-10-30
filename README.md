# FS-X-VFX

FirstSelfie's private **Claude Code plugin marketplace**: one repo for every skill and plugin we build.
Each plugin installs **on its own**, so you can share just one plugin with someone.

## Catalogue
| Plugin | What it does | Commands | Install |
|---|---|---|---|
| [vfx-intro](plugins/vfx-intro) | Cinema-grade 3D/VFX intros from a reference video, an idea or keywords | /vfx-intro, /vfx-setup | `claude plugin install vfx-intro@fs-x-vfx` |
| [cinematic-sound](plugins/cinematic-sound) | Hollywood / Think School sound for a finished picture | /score-this | `claude plugin install cinematic-sound@fs-x-vfx` |
| [fs-vox-charts](plugins/fs-vox-charts) | FirstSelfie Vox-style editorial data-chart animations in After Effects, scripted and rendered headless at 4K | /vox-chart | `claude plugin install fs-vox-charts@fs-x-vfx` |

## Install
**Once per computer**, add the marketplace. You need repo access and Git signed in to GitHub:
```bash
claude plugin marketplace add NK-EMPIRE/FS-X-VFX
```
**Then install only what you need**, one plugin or several:
```bash
claude plugin install vfx-intro@fs-x-vfx
claude plugin install cinematic-sound@fs-x-vfx
claude plugin install fs-vox-charts@fs-x-vfx
```
Or install everything: `setup\install.ps1` (Windows) / `bash setup/install.sh` (macOS/Linux). Pass names to install only some: `setup\install.ps1 cinematic-sound`.
Restart Claude Code after installing.

**Update:** `claude plugin marketplace update fs-x-vfx`, then `claude plugin update <plugin>@fs-x-vfx`.
**Remove:** `claude plugin uninstall <plugin>@fs-x-vfx`.

## Share one plugin
Send the plugin's own page, e.g. `https://github.com/NK-EMPIRE/FS-X-VFX/tree/main/plugins/cinematic-sound`. Its README has the two install lines.
The person needs read access to this private repo (Settings → Collaborators, or a team in the NK-EMPIRE org).

## Layout
```
.claude-plugin/marketplace.json   the catalogue (one entry per plugin)
plugins/<plugin>/
  .claude-plugin/plugin.json      name + version (must equal the catalogue entry)
  README.md                       the share page for this plugin
  skills/<skill>/SKILL.md         one or more skills (+ references/, scripts/, examples/)
  commands/<command>.md           slash commands
templates/plugin-template/        copy this to start a new plugin
setup/install.ps1, install.sh     installers (all plugins, or the names you pass)
tools/validate.py                 checks every manifest, versions and READMEs before a push
CONTRIBUTING.md                   how to add or update a plugin
CHANGELOG.md                      release notes
```
