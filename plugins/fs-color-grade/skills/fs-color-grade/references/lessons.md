# Lessons from the FirstSelfie Festival Intro grade: read these before starting

1. **A selective HSV "paint" LUT got the grade rejected.** We keyed teal, skin and red in one LUT and pushed each hard. The result had:
   - banding on 8-bit gradients and crushed blacks;
   - an orange "painted" face and a blown lamp;
   - the whole room turned teal, and the logo drifted to cyan;
   - a plastic, AI look.

   The user: "it's not a colour grading, just painted the face and the background." The fix was a global look built with curves (build_look.py) plus Lumetri sliders, as the tutorials teach.
2. **Faces went darker than the rough cut.** This happened three times, from the moody curve, from density, and from Look Intensity. The rule now: measure face luma against the rough cut at 6 points, and the graded face must be ≥ the rough cut.
3. **The skin lift in the look (v2) went too coloured.** The user asked for "between v1 and v2". The answer was v1 plus Lumetri: Exposure +0.04, Shadows +24 → 30, Blacks +9 and Saturation 108 → 105.
4. **Too saturated / orange face** (hue 18–21° against the reference's 11–14°). The fix was Temperature −4 → −2 with Tint +3, plus a small saturation cut. Vibrance −14 also dulled the logo red, so it went back to 0.
5. **A navy under-cap forehead.** Split-tone shadows plus a cool white balance land on skin in shadow. The fix was Shadows +6, Look Intensity 150 → 125 and a warmer Temperature. Always make a 2× face zoom; the 6-frame grid hides it.
6. **ffmpeg decodes untagged 4K H.264 with the 601 matrix.** That shifts hues by about 5° and made a perfect render look wrong. Grab frames with `scale=in_color_matrix=bt709` (fsgrade.grab does this).
7. **Premiere's "Match Source – High bitrate" preset is 1080p at 10 Mbps.** The 4K render came out at 10.7 Mbps and soft. Editing that preset's bitrate did nothing (the file came out byte-identical). Build the preset from "High Quality 2160 4K" with the right fps (make_preset.py) and always run ffprobe on the result.
8. **The MCP export_frame / export_sequence tools threw "EvalScript error".** Use the ExtendScript recipes in premiere_mcp.md: backslash paths with no extension, and app.encoder.
9. **Lumetri's Look can't be set by script, and curves are blobs.** Bake the curve moves into the look .cube; the user clicks Browse once.
10. **The project was "saved as" under another name.** Reopening the original showed an empty project. Check for the newest .prproj with real size before panicking.
11. **The editor won't have your timeline.** Deliver a baked full-grade LUT (bake_lut.py) with a verify number, an ffmpeg parse test, before/after stills and a 1-page guide.
12. **Credits:** Premiere via MCP is nearly free. Resolve via computer use costs much more. Ask before choosing it.
13. **Ask, then act.** Confirm the reference range, what to copy, the brand colours and the deliverable. Show sheets and numbers, and get "yes" before rendering.
