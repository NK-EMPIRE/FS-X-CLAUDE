# Premiere Pro via the Premiere MCP: tested ExtendScript recipes

Run each recipe with `mcp__premiere-pro__execute_extendscript`. The last expression is the return value, so end with a string.

## Connection
- **Bridge:** the MCP bridge listens on ws port 8097. Check it with `get_connection_status`.
  - Only ONE Claude session's bridge can own the port. If another session holds it, ask the user before killing that PID.
  - Find the PID with `Get-NetTCPConnection -LocalPort 8097`.
- **If Premiere was closed:** `Start-Process <project>.prproj`. Wait until `app.project.path` is set.
  - The project may have been saved under another name by the user. Look for the newest `.prproj` with real size; an empty project is ~5 KB.
  - Open it with `app.openDocument(path, 1, 0, 1, 1)`, then pick it from `app.projects` by name.
- **Broken MCP tools:**
  - `export_frame` and `export_sequence` failed with "EvalScript error". Use the recipes below instead.
  - `app.project.save()` can time out when a dialog is open; ask the user to press Ctrl+S. `save_project` usually works.

## Find the Lumetri on the graded clip
```js
var clip = app.project.activeSequence.videoTracks[0].clips[0]; var L = null;
for (var i = 0; i < clip.components.numItems; i++) if (clip.components[i].displayName == "Lumetri Color") L = clip.components[i];
```
Add one with `app.enableQE(); var e = qe.project.getVideoEffectByName("Lumetri Color"); qe.project.getActiveSequence().getVideoTrackAt(0).getItemAt(0).addVideoEffect(e);`

## Property indices (Premiere 2026, Lumetri Color)
| Index | Property | Notes |
|---|---|---|
| 14 | Temperature | |
| 15 | Tint | |
| 16 | Saturation | 100 = neutral |
| 19 | Exposure | |
| 20 | Contrast | |
| 21 | Highlights | |
| 22 | Shadows | |
| 23 | Whites | |
| 24 | Blacks | |
| 6 | Input LUT | |
| 34 / 35 | Look | dropdown; can't load a .cube by script |
| 38 | Look Intensity | |
| 41 | Sharpen | |
| 42 | Vibrance | |
| 43 | Saturation (Creative) | |
| 110 | Vignette Amount | |

- Set a value with `L.properties[16].setValue(105, true)`.
- **Curves, wheels and HSL are blobs and not scriptable.** Bake those moves into the look .cube instead (build_look.py).
- **Look .cube:** the user loads it once via Lumetri > Creative > Look > Browse. It is then embedded in the project (prop 32 blob / 122 Embedded LUTs).
- Dump every property to check a project:
  ```js
  for (k = 0; k < L.properties.numItems; k++) o.push(k + ":" + L.properties[k].displayName + "=" + L.properties[k].getValue());
  ```

## Export frames (the Program Monitor result, 4K PNG)
```js
app.enableQE(); var q = qe.project.getActiveSequence(); var times = [30, 90, 150, 220, 300, 400];
for (var t = 0; t < times.length; t++) {
  app.project.activeSequence.setPlayerPosition(String(Math.round(times[t] * 254016000000)));   // ticks
  q.exportFramePNG(q.CTI.timecode, "D:\\work\\pp_" + times[t]);   // backslashes, NO extension: Premiere adds .png
}
"done";
```
A forward-slash path with ".png" returns "EvalScript error".

## Render with a proper preset (Media Encoder)
```js
app.encoder.launchEncoder();
var id = app.encoder.encodeSequence(app.project.activeSequence, "D:\\out\\FINAL_4K.mp4", "D:\\out\\FS_H264_4K25_50Mbps.epr", 0, 1);  // 0 = entire sequence, 1 = remove from queue when done
app.encoder.startBatch(); "job " + id;
```
- **Waiting:** wait in a background Bash loop until the file size is stable for about 60 s.
- **Checking:** run `ffprobe`. A 7-minute 4K render at 50 Mbps took about 6 minutes on our machine.

## Bake the full grade into a LUT (bake_lut.py identity / extract)
```js
var pi = app.project.activeSequence.videoTracks[0].clips[0].projectItem; var orig = pi.getMediaPath();
pi.changeMediaPath("D:\\work\\identity_65.png", true);
// ... export one frame with the frame recipe above ...
pi.changeMediaPath(orig, true);   // RESTORE immediately, then check app.project.activeSequence.end
```
- **Back up the .prproj first.**
- **Check the export:** export two frames at different times; they must be identical.

## Pitfalls
- The sequence time unit is ticks: 254016000000 per second.
- Several projects can be open. `app.project` is the active one; pick by `app.projects[i].name`.
- A pixel-perfect identity image needs the sequence frame size to equal the image size (3840×2160), with no scaling.
