#!/usr/bin/env bash
# Finish an FS VOX package folder and zip it. The .aep must already be saved INTO <pkg>/ by the job (JOB.aep) and the
# logo must already be in <pkg>/Footage/logo/ (copy it there BEFORE building) — then nothing needs relinking.
# usage: package.sh <pkg_dir> <renders_dir> <fonts_dir> <job_script.jsx>
set -eu
PKG="$1"; R="$2"; F="$3"; JS="$4"; SK="$(dirname "$0")/.."
mkdir -p "$PKG/Renders_4K" "$PKG/Review_1080_withVO" "$PKG/Fonts" "$PKG/Scripts"
cp "$R"/*.mp4 "$PKG/Renders_4K/" 2>/dev/null || true
cp "$R"/review_withVO/*.mp4 "$PKG/Review_1080_withVO/" 2>/dev/null || true
for f in BodoniModa.ttf Inter.ttf; do [ -f "$F/$f" ] && cp "$F/$f" "$PKG/Fonts/"; done
cp "$JS" "$SK/kit/fs_vox_kit.jsx" "$PKG/Scripts/"
[ -f "$PKG/README.txt" ] || cp "$SK/reference/README_TEMPLATE.txt" "$PKG/README.txt"
cd "$(dirname "$PKG")"; n="$(basename "$PKG")"; rm -f "$n.zip"
powershell -NoProfile -Command "Compress-Archive -Path '$n' -DestinationPath '$n.zip' -CompressionLevel Optimal"
ls -la "$n.zip"
