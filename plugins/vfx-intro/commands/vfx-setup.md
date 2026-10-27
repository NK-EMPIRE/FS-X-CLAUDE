---
description: Check this computer for the VFX intro pipeline (Blender, After Effects, ffmpeg, Python libs, NVIDIA GPU, fonts, disk) and tell the user exactly what to install
---

Check this machine for the vfx-intro pipeline. Report a table: tool, found (path/version), status, fix. Don't install anything without asking.

1. **Blender 5.x**: look for `blender.exe` under `C:/Program Files/Blender Foundation/*/` (or `blender` on PATH / `/Applications/Blender.app` on macOS). Run `blender -b --version`.
2. **After Effects 2024+**: look for `AfterFX.exe` under `C:/Program Files/Adobe/Adobe After Effects */Support Files/` (macOS: `/Applications/Adobe After Effects */`). Note that scripts need Preferences > Scripting & Expressions > "Allow Scripts to Write Files and Access Network".
3. **ffmpeg / ffprobe** on PATH (`ffmpeg -version`).
4. **Python 3** with **Pillow** and **numpy** (`python -c "import PIL, numpy"`). Offer `pip install pillow numpy`.
5. **GPU**: `nvidia-smi` (name, VRAM). OptiX needs an NVIDIA RTX. Without one, warn that Cycles will be ~10-20x slower and suggest lower samples.
6. **Fonts**: list the fonts the user's style needs. Remind them to use "Install for all users", otherwise AE renders a fallback.
7. **Disk**: free space on the project drive. Budget about 8 MB per frame (1920x804 16-bit PNG).
8. If Blender or AE are in non-default places, tell the user to set `BLENDER` and `AFX` environment variables (used by `scripts/tools/vfx.sh`).

End with: "Ready. Try: /vfx-intro <your idea or a reference video path>".
