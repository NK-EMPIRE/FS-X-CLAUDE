"""Word-level VO timings for FS VOX shots.
usage:  python -I -X utf8 word_times.py <audio_or_video> <start_s> <dur_s> [lang=ta] [model=medium]
prints  SEG a-b  then  word@time  (absolute seconds in the source). Needs: pip install faster-whisper, ffmpeg on PATH.
Note: -I ignores PYTHONIOENCODING, so always pass -X utf8 (Tamil text crashes cp1252 otherwise).
Whisper can silently skip long stretches: transcribe in windows of <= 30 s around each line you need."""
import os, subprocess, sys, tempfile
from faster_whisper import WhisperModel

src, start, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
lang = sys.argv[4] if len(sys.argv) > 4 else "ta"
model = sys.argv[5] if len(sys.argv) > 5 else "medium"
wav = os.path.join(tempfile.mkdtemp(), "clip.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", src, "-ac", "1", "-ar", "16000", wav], check=True)
m = WhisperModel(model, device="cpu", compute_type="int8")
segs, _ = m.transcribe(wav, language=lang, word_timestamps=True, vad_filter=False)
for s in segs:
    print("SEG %.2f-%.2f" % (s.start + start, s.end + start))
    print("  " + " ".join("%s@%.2f" % (w.word.strip(), w.start + start) for w in s.words))
