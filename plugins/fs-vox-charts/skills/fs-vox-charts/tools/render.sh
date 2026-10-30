#!/usr/bin/env bash
# Render every comp of an FS VOX project with aerender, then make contact sheets (+ optional VO review copies).
# usage: render.sh <project.aep> <out_dir> "<COMP1> <COMP2> ..." [roughcut.mp4]
#   VO review offset is read from the comp name suffix _mmss-mmss  (e.g. V12_X_0551-0601 -> 351 s; add exact decimals with OFFSETS env "COMP=351.5,...")
# Template: "H.264 - Match Render Settings - 40 Mbps" (4K). There is NO "PNG Sequence" template on this machine.
set -u
AEP="$1"; OUT="$2"; COMPS="$3"; RC="${4:-}"
AER="/c/Program Files/Adobe/Adobe After Effects 2026/Support Files/aerender.exe"
mkdir -p "$OUT/sheets" "$OUT/review_withVO"
P="$(cygpath -w "$AEP")"
for comp in $COMPS; do
  "$AER" -project "$P" -comp "$comp" -OMtemplate "H.264 - Match Render Settings - 40 Mbps" -output "$(cygpath -w "$OUT/$comp.mp4")" > "$OUT/$comp.log" 2>&1
  echo "$comp render exit $?"
  ffmpeg -v error -y -i "$OUT/$comp.mp4" -vf "fps=2.5,scale=480:-1,tile=4x8" -frames:v 1 "$OUT/sheets/$comp.jpg"
  if [ -n "$RC" ]; then
    off=$(echo "${OFFSETS:-}" | tr ',' '\n' | grep "^$comp=" | cut -d= -f2)
    if [ -z "$off" ]; then mmss=$(echo "$comp" | sed -E 's/.*_([0-9]{4})-[0-9]{4}$/\1/'); off=$(( 10#${mmss:0:2} * 60 + 10#${mmss:2:2} )); fi
    ffmpeg -v error -y -i "$OUT/$comp.mp4" -ss "$off" -i "$RC" -map 0:v -map 1:a -shortest -vf scale=1920:-2 -c:v libx264 -crf 20 -preset fast -c:a aac -b:a 160k "$OUT/review_withVO/${comp}_VO_1080.mp4"
    echo "$comp review (VO from $off s) exit $?"
  fi
done
