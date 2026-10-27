# From words to shots

Works from anything: "gold coin bursts into the title", "Vinayagar emerges from a cracker blast, 360 turn", or a video topic ("The Richest Temple in India").

## Brief questions (ask once, max 4; default if the user says "you decide")
1. Topic/title text and channel/brand (does a brand intro open the film?).
2. Length (10 / 20 / 30-40 s) and delivery (YouTube 16:9, Shorts 9:16, both).
3. Hero object or "you choose" + any must-have imagery (cultural symbols, product).
4. Mood: luxury gold / gritty doc / tech / devotional / playful; reference links if any.

## 1. Concept engine
From the topic, list 10 hero-object candidates that *are* the story in one image (money -> coin/note/vault; temple -> bell/lamp/idol; tech -> chip; food -> spice). Pick the one with: a strong silhouette, a material that looks expensive under a raking light, and a natural transformation.

## 2. Transformation verbs (pick a chain of 2-4)
emboss / engrave / morph relief -> flip / spin / orbit -> energise (arcs, traces, glow) -> crack -> shatter / explode / disintegrate into particles -> melt / pour -> assemble from fragments -> reveal (light sweep, push-through, dust clears) -> title.

## 3. Beat sheet template (seconds, 30 s example)
| t | beat | camera |
|---|---|---|
| 0-4.8 | brand intro, push into logo detail, flash match-cut | 2D in AE |
| 4.8-10 | hero object out of darkness, first transformation | top-down -> low hero push |
| 10-18 | detail and energy (macro, arcs) | macro slide, 70 mm, shallow |
| 18-24 | turn / reveal second face | orbit / flip |
| 24-29 | build-up (fuse, cracks, light from inside) | slow push, shake on hits |
| 29-31 | payoff: burst / transformation (48 fps) | same camera, slow-mo on impact only |
| 31-38 | aftermath flows into the title (smoke/light), hold 5-6 s | drift, push through |

## 4. Pitch three directions
For each: name, logline, hero, key frame description, why it fits, render cost. Recommend one. When the user writes an idea in their own words, keep their beats and add yours as clearly marked upgrades.

## 5. Turn into a scene
Map each beat to: STORY keys (`KEY(nt, "control", [(t, v)])`), SHOTS entries (camera path, lens, f-stop), JOBS (fps 24/48), AE config (remaps, flashes, title start). Write it all in PLAN.md first.

## Imagination without references
If the user gives only words, still produce: a mood palette (3-5 rgb), a lighting diagram (key/rim/fill positions), a camera diagram per shot, and a 6-frame storyboard rendered from a quick Blender layout (`test` mode at 50 %). Pictures before full builds.
