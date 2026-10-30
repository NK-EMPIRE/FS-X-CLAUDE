# FS VOX — style system

Origin: Vox / Johnny-Harris data-journalism charts (REF2 recording), adapted to the FirstSelfie brand. Only colours,
brand and content change from the reference; the grammar stays.

## Canvas
- 1920×1080 design units, 25 fps. Masters at 3840×2160 (kit `res: 4`).
- Background (kit `paperBG`): cream paper `PAPER [0.965,0.937,0.894]` + Grid (80 px cells, 2 px, ink, Multiply 7%,
  Roughen Edges) + paper dots (Fractal Noise → CC Ball Action 6 → Tint brown→paper, Multiply 18%).
- Finish (kit `finish`): adjustment layer, Noise 6 + **Posterize Time 12 fps** (the choppy, tactile doc feel). `{posterize:0}`
  only if the user asks for smooth motion.

## Colour (flat only)
| Token | RGB 0–1 | Use |
|---|---|---|
| `OR` | 1, 0.42, 0 (#FF6B00) | the point: hero number, the bar that matters, highlighter (55%) |
| `COCOA` | 0.227, 0.149, 0.094 | the comparison / second series, unit words |
| `WGREY` | 0.75, 0.71, 0.65 | context bars, tracks |
| `INK` | 0.11, 0.09, 0.08 | headlines, labels, axes, leader lines |
| `GREY` | 0.45, 0.42, 0.39 | sub lines, footers, minor labels |
| `PEACH`, `OL` | light orange tints | extra pie slices only |

## Type
| Role | Font (PostScript) | Size (1080 units) |
|---|---|---|
| Headline | TimesNewRomanPS-BoldMT | 62, left at x 160, baseline y 170 |
| Keyword in headline | TimesNewRomanPS-BoldItalicMT + orange highlighter | 62 |
| Sub line | Inter-Light, GREY | 24 at y+46 |
| Labels | Inter-Regular | 18–30 |
| Numbers | BodoniModa-Bold (₹ falls back to Times — accepted) | 26–60 labels, 120–250 heroes |
| Emphasis lines | Times Bold Italic | 40–56 |
| Footer | Inter-Light 18 GREY at [160,1010] + logo 130 px wide at [1780,1000], 85% |

## Layout
- Safe margins: x 160 → 1760, y 120 → 1010. Headline block top-left; chart in the middle band (y 330 → 940).
- One idea per shot. One hero (number or the orange element). Lots of empty paper.
- Right column (x 1360 → 1780) is the call-out zone when a chart steps back to the left.

## Motion
- Text: word-by-word (opacity 0 + 22 px rise, ~0.4–0.6 s), headline at 0.2 / keyword 0.55 / highlight swipe 0.9–1.35.
- Bars/lines/arcs: grow with AE ease (influence 70–75), stagger 0.08–0.6 s, Roughen Edges ~1.5 (hand-made edge).
- Counters: cubic-out, land on the spoken number.
- SaaS set-pieces: exact expo curves via `VOX.ex` (o = expo out, no overshoot; n = expo in for exits/pushes; i = in-out),
  comp motion blur on (`{mblur:true}`), dots that morph into glyphs, push-ins between beats.
- Every layer fades out over the last 0.4 s (`opOut`) unless the shot hands off to the next one.
