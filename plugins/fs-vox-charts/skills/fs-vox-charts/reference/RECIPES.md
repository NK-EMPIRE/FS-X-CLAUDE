# FS VOX — recipes and gotchas

## Pick the chart from the line
| The script says… | Use | Kit call |
|---|---|---|
| one big total ("₹219.64 lakh crore") | hero counter + unit + a 100% bar it will later be sliced from | `bigNumber` + `hbar` |
| "X% of Y" | ring counter | `ringCounter` |
| A vs B (nearly equal / one dwarfs the other) | horizontal bars with counters | `hbars` |
| a ranking of categories | sorted vertical bars, the point in orange/cocoa, rest grey | `vbars` |
| a split of a whole (2–6 parts) | pie / donut + leader lines | `pie` |
| goods vs services, a share of a "parliament" | hemicycle | `hemicycle` |
| a trend over time / a seasonal spike | line chart drawing L→R + peak label | `lineChart` |
| "according to <source>…" | search bar typing, answer appears | `searchBar` |
| "of all that, N% was…" on an existing chart | step chart back, hand-drawn box, cover N%, arrow → big N% | `selectAndCover` |
| a rhetorical question / "guess" | dot → big ? + field of small ? (nothing else on screen) | `questionBurst` |
| a span of time (festival to festival, 30 days) | dot → timeline with day ticks | `timeline` |
| a rate ("₹14 crore every minute") | clock ring sweep + counter | `minuteRing` |
| "by the time you finish this video…" | player card, progress fills, counter tied to progress, timecode = rate maths | `playerCounter` |

Rate maths to check before building: amount ÷ rate = minutes (₹170 Cr ÷ ₹14 Cr/min ≈ 12:08); rate × minutes in the
period ≈ the stated total (₹14 Cr × 43,200 min ≈ ₹6.05 L Cr). Say so in the footer.

## Timing patterns (comp seconds; t = word time − comp start)
- Standard chart shot 8 s: headline 0.2–1.35 → data 0.6–3 → note/punch line ~3 → hold → opOut at DUR−0.4.
- Continuation of an existing chart: same build with `VOX.TOFF = -3` (finished at frame 0), new action from 0.3 s.
- Chained SaaS shots hand off on a shared element: `questionBurst` ends on `END_DOT` (34 px orange, centre) and
  `timeline` starts from the same dot → cut is invisible.
- Push between beats: group null scale 100→520 with mode "n" over 0.55 s + opacity out; next beat scales 40→100 "o".

## Gotchas already paid for
- 2D rotation matchName is `"ADBE Rotate Z"` (not "ADBE Rotation").
- Expressions run in the JavaScript engine: arrays need `add()/sub()/mul()`; `[1,1]*x` is NaN.
- `layer.setParentWithJump(null)` keeps local values (authored 1080 numbers survive the 4K scaler); `layer.parent = x` would compensate.
- Null opacity does not affect children → `VOX.kids(layers, null, true)` links opacity by expression.
- Effects on layers under SCALE_4K are scaled by the parent. Doubling them (K) made Roughen Edges eat highlighters.
  Highlighters get no Roughen at all, and neither do thin strokes (< 8 px: boxes, arrows, timeline lines) — at 1080 it breaks them into dashes. Roughen only bars, arcs, covers.
- Big-number highlighter: `hilite(c, layer, t0, t1, 0.16, 1.02)` (thin underline), otherwise it sits over the digits.
- Text layer anchor for scaling/rotating glyphs: `VOX.centerAnchor(l)` (uses sourceRectAtTime(0)).
- aerender template that exists: `"H.264 - Match Render Settings - 40 Mbps"` (15/5 Mbps also). No PNG Sequence template.
  4K renders ≈ 1 min per 10 s; the question burst (≈100 layers + motion blur) ≈ 4 min.
- faster-whisper: run Python with `-I -X utf8` (PYTHONIOENCODING is ignored under -I). Long files skip regions — use ≤ 30 s windows.
- If `AfterFX.com -r` produces no log line at all, AE is stuck before running the script (startup dialog / licence).
  Don't loop retries: kill only the AE process you started, tell the user, ask them to check the AE window.
  Avoid it in the first place by saving the .aep straight into the package folder with the logo already there
  (no separate relink pass needed).
- Comp names carry the VO window (`_0551-0601`); `render.sh` uses it to cut the review audio (override decimals with OFFSETS).

## Delivery README must say
Where each shot goes (VO time + line), the fonts to install (Bodoni Moda, Inter; Times is in Windows), that everything is
drawn in 1080 units under the disabled `SCALE_4K` null (don't delete it), and that `FINISH_GRAIN_POSTERIZE` switches the 12 fps look.
