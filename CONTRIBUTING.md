# Adding and updating plugins / skills

## Add a new skill to an existing plugin
1. Create `plugins/<plugin>/skills/<new-skill>/SKILL.md` (frontmatter `name` + a `description` that says WHEN to use it), plus `references/` / `scripts/` if needed.
2. Bump `version` in `plugins/<plugin>/.claude-plugin/plugin.json` **and** the matching entry in `.claude-plugin/marketplace.json` (keep them equal).
3. Add a line to `CHANGELOG.md`, validate, commit, push (below).

## Add a new plugin
1. `cp -r templates/plugin-template plugins/<new-plugin>` and rename inside `plugin.json`, `skills/`, `commands/`.
2. Add an entry to `.claude-plugin/marketplace.json` → `plugins` (`name`, `source: "./plugins/<new-plugin>"`, `description`, `version`, `category`).
3. Add it to the table in `README.md` and the `PLUGINS` list in `setup/install.ps1` and `setup/install.sh`.

## Validate before every push
```bash
claude plugin validate .
claude plugin validate plugins/<plugin>
```
Test locally without pushing: `claude plugin marketplace add "<path to this repo>"` then install, restart Claude Code, try the commands.

## Release
```bash
git add -A && git commit -m "<plugin>: <change> (vX.Y.Z)"
git push
claude plugin tag plugins/<plugin>      # optional: creates <plugin>--vX.Y.Z tag after checking versions agree
```
Team members get it with `claude plugin marketplace update fs-x-vfx` + `claude plugin update <plugin>@fs-x-vfx`.

## Rules
- Versioning: patch = fixes/wording, minor = new skill/command/feature, major = breaking change to scripts or config formats.
- Never commit renders, frames, caches, .blend files over 50 MB, client footage, fonts you are not licensed to share, or API keys. See `.gitignore`.
- Paths inside skills are relative to the skill folder; never hard-code a personal drive path in instructions (examples may keep them, clearly labelled).
- Every hard-won fix goes into the plugin's `references/lessons_learned.md`.
