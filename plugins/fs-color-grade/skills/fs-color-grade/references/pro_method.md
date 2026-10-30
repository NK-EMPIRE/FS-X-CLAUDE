# How a pro colourist grades: the method behind this skill

These notes come from the tutorials studied for the FirstSelfie grade:
- Danny Gan's qualifier-free split tone;
- Enam Alamin's 8 steps in Premiere;
- Gaku Lange's density / hue-vs-luma;
- plus four more on scopes and skin.

## Order of operations (one Lumetri, or one node, per job)
1. **Monitor and input.** Make sure the display is trustworthy. LOG footage gets its Rec.709 conversion LUT first.
2. **Balance.** Exposure and white balance on the scopes:
   - waveform (luma): highlights under 90 IRE, except practicals such as lamps or the sun;
   - white balance: something white should read neutral;
   - skin on the vectorscope skin line.
3. **Contrast with curves.** Shadows down a little but not crushed (keep ~5 IRE of texture), highs under 90–95, mids up for skin.
   The filmic trick: lift the black point slightly for "milky" film blacks.
4. **The look (global).** Teal/orange via the RGB curves:
   - red channel: down in the shadows (teal), up in the highlights (warm);
   - green: down in the shadows;
   - blue: down in the highlights and slightly in the mids (orange skin).
5. **Skin rescue without qualifiers (Danny Gan).** Hue vs Sat: orange ×1.16 and red at half of that (×1.08). This adds back the skin warmth the split tone removed, with no key and so no edges. ×1.24 orange / ×1.12 red is already "unnatural".
6. **Clean blacks.** Luma vs Sat: pull saturation out of the deepest blacks, so black stays black and not teal.
7. **Density (Gaku Lange).** Hue vs Luma: pull the luminance of the background hue (−8 %) and of orange (−4 %) down slightly. That gives a richer, more "film" colour without more saturation.
8. **Secondaries, only if needed.**
   - Use masks gently, with a big feather and tracking: a face mask with HSL refine, or a sky mask placed above the contrast layer.
   - Prefer global moves. On 8-bit H.264, keys band and halo.
9. **Finish.** A subtle highlight glow (blur + luma key, Lighten, 30 px) and fine grain (~2 %, no colour) make it organic.

## What "natural" means in numbers (South-Asian skin under warm practicals, Rec.709)
| Measure | Target |
|---|---|
| Face hue | 8–14° (under 8 is pink/red, over 16 is orange/"painted") |
| Face saturation | 0.26–0.38 |
| Face luma | never below the rough cut; 0.33–0.65 depending on the shot |
| Background (moody teal) | hue 180–186, sat 0.45–0.52, luma ~0.33 |
| Brand red (FirstSelfie logo) | hue unchanged (±1°); sat may rise a few % |

The face numbers are measured on the lit 60th-percentile skin of the face.

## Copying a reference
- Copy the **hue** relationships (background hue, skin hue) closely, but **saturation only partly**. References are usually graded harder than a client will accept.
- Copy the **mood through density and contrast**: a darker background, lifted soft blacks, warm skin against teal.
- Copy only the part the user asked for (e.g. the reference's left-side teal and the face, not its red set dressing).
- The match is right when the *relationships* match: skin vs background contrast, how warm against how cool, and where the shadows sit. Matching every pixel is not the goal.
