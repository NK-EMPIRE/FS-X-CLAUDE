#!/usr/bin/env bash
# vfx.sh: safe launchers for the pipeline (Git Bash on Windows).
#   vfx.sh blender <blend|-> <script.py> <args...>   -> background render, 6 threads, below-normal priority, log next to script
#   vfx.sh wait_blender                              -> block until no blender.exe is running
#   vfx.sh ae <dir_without_spaces>/script.jsx [done_file] -> run an AE script (kills any open AE first), wait for done file
#   vfx.sh encode <master.mov> <out_basename>        -> <out>_1080p.mp4 (crf 15 grain), <out>_4K.mp4 (lanczos+unsharp+grain), <out>_preview.mp4
#   vfx.sh gpu                                       -> GPU temp / load / power (safe < 87C on laptops)
# auto-detect the newest install (override with BLENDER=... AFX=...)
[ -z "$BLENDER" ] && BLENDER="$(ls -d /c/Program\ Files/Blender\ Foundation/*/blender.exe 2>/dev/null | sort -V | tail -1)"
[ -z "$BLENDER" ] && BLENDER="$(command -v blender || echo /Applications/Blender.app/Contents/MacOS/Blender)"
[ -z "$AFX" ] && AFX="$(ls -d /c/Program\ Files/Adobe/Adobe\ After\ Effects\ */Support\ Files/AfterFX.exe 2>/dev/null | sort -V | tail -1)"
cmd="$1"; shift
case "$cmd" in
  blender)
    blend="$1"; script="$2"; shift 2; log="${script%.py}_$(date +%H%M%S).log"
    if [ "$blend" = "-" ]; then ("$BLENDER" -b -t 6 -P "$script" -- "$@" > "$log" 2>&1 &); else ("$BLENDER" -b "$blend" -t 6 -P "$script" -- "$@" > "$log" 2>&1 &); fi
    sleep 4; wmic process where name="blender.exe" CALL setpriority "below normal" >/dev/null 2>&1; echo "log: $log" ;;
  wait_blender)
    sleep 5; while tasklist | grep -qi blender.exe; do sleep 15; done; echo "blender finished" ;;
  ae)
    jsx="$1"; done="${2:-}"; case "$jsx" in *" "*) echo "AE script path must not contain spaces"; exit 1;; esac
    [ -n "$done" ] && rm -f "$done"; taskkill //IM AfterFX.exe //F >/dev/null 2>&1; sleep 3
    ("$AFX" -r "$jsx" >/dev/null 2>&1 &)
    if [ -n "$done" ]; then for i in $(seq 1 720); do [ -f "$done" ] && break; sleep 5; done; echo "AE done: $done"; fi ;;
  encode)
    m="$1"; o="$2"
    ffmpeg -y -v error -i "$m" -c:v libx264 -crf 15 -preset slow -tune grain -pix_fmt yuv420p "${o}_1080p.mp4"
    ffmpeg -y -v error -i "$m" -vf "scale=3840:2160:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,noise=c0s=4:allf=t" -c:v libx264 -crf 16 -preset medium -tune grain -pix_fmt yuv420p "${o}_4K.mp4"
    ffmpeg -y -v error -i "$m" -vf scale=1280:-2 -c:v libx264 -crf 24 -preset fast -pix_fmt yuv420p "${o}_preview.mp4"
    ls -la "${o}"_*.mp4 ;;
  gpu)
    nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,power.draw,memory.used --format=csv ;;
  *) sed -n 2,8p "$0" ;;
esac
