# fs-color-grade  ·  v1.0.0

Natural, pro colour grading that recreates a reference's look on your footage (Premiere Lumetri via MCP, Resolve or ffmpeg), keeps brand colours, proves it with numbers and review sheets, renders 4K at the right bitrate, and bakes the whole grade into a one-click .cube LUT for editors.

Give it your footage and a reference (plus the seconds to copy). It:
1. measures both;
2. builds a global, colourist-style look (split tone, skin rescue, density, clean blacks);
3. finishes it in Lumetri and checks the face, the blacks and the logo on review sheets;
4. renders after you approve;
5. delivers `<Name>_FINAL.cube` plus a how-to so an editor can apply the exact grade to the final timeline.

Includes the shipped FirstSelfie *Moody Teal* grade (`examples/firstselfie_festival_intro/`) as a ready LUT.

## Install
```bash
claude plugin marketplace add NK-EMPIRE/FS-X-VFX
claude plugin install fs-color-grade@fs-x-vfx
```
Restart Claude Code, then use: /color-grade

**Needs:**
- Python 3 with numpy and Pillow;
- ffmpeg on PATH;
- for the Premiere route: Premiere Pro with the Premiere MCP bridge connected.

Part of the [FS-X-VFX marketplace](https://github.com/NK-EMPIRE/FS-X-VFX). Update with `claude plugin update fs-color-grade@fs-x-vfx`.
