FS VOX charts — <JOB NAME> (4K 3840x2160, 25 fps)
==================================================
Renders_4K/            final 4K H.264 (~40 Mbps) for the edit
Review_1080_withVO/    1080p copies with the rough-cut voiceover (sync check only)
<JOB>.aep              editable After Effects 2026 project
Footage/logo/          FirstSelfie logo
Fonts/                 Bodoni Moda, Inter (Times New Roman ships with Windows)
Scripts/               fs_vox_kit.jsx + the job script that builds the project

WHERE EACH SHOT GOES (rough-cut VO time = comp time 0)
  <COMP NAME>   <mm:ss>   "<script line>"   <notes: continues X / hands off to Y>

OPEN THE PROJECT
  1. Install the fonts in Fonts/, restart After Effects, open the .aep.
  2. Everything is drawn in 1920x1080 units under the disabled null "SCALE_4K" (x2) - edit layers normally, don't delete it.
  3. "FINISH_GRAIN_POSTERIZE" (top layer) = the 12 fps Vox feel; switch it off for smooth motion.
