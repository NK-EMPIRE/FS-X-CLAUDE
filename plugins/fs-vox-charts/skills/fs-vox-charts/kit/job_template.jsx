// FS VOX CHARTS — job template. Copy to <project>/AE/scripts/build_<job>.jsx, edit JOB + the comps, run:
//   "C:/Program Files/Adobe/Adobe After Effects 2026/Support Files/AfterFX.com" -r "<abs path to this file>"
// Each comp: VOX.comp(name, dur, opts) -> headline/charts -> VOX.finish(c). Name comps <ID>_<WHAT>_<mmss>-<mmss> (VO window).
// Comp time 0 = the VO time in the name; every t below is "VO word time - comp start".
#include "C:/Users/Naveen Karthick/.claude/skills/fs-vox-charts/kit/fs_vox_kit.jsx"

var JOB = {
  root: "D:/CLIENT WORKS/EXAMPLE/AE/",                        // build log lands here (vox_build_log.txt)
  logo: "D:/CLIENT WORKS/EXAMPLE/AE/PACKAGE/JOB/Footage/logo/Primary Logo - Transparent (1).png",
  aep:  "D:/CLIENT WORKS/EXAMPLE/AE/PACKAGE/JOB/FS_VOX_JOB.aep",  // save INTO the package folder = self-contained
  res: 4                                                      // 4 = 3840x2160 (YouTube master), 1 = 1080 test
};
if (typeof VOX_JOB_OVERRIDE !== "undefined") JOB = VOX_JOB_OVERRIDE;   // tools/selftest.jsx sets this

VOX.init(JOB);
VOX.run(function () {
  var c;

  // 1) big number + 100% bar (a "total" that a later chart slices)
  c = VOX.comp("V01_TOTAL_0008-0016", 8.1);
  VOX.headline(c, "What Indians spent in", "2025", "just to live", "MoSPI · household consumption expenditure, 2025");
  VOX.bigNumber(c, 219.64, 2, "₹", "", "lakh crore", 2.0, 4.9);
  VOX.txt(c, "BAR_L", "Total household spending", VOX.SANS, 28, VOX.INK, [160, 778], 5.5, 0.4);
  VOX.hbar(c, "TOTAL_BAR", 160, 832, 1600, 64, VOX.INK, 5.6);
  VOX.rtxt(c, "BAR_100", "100%", VOX.NUM, 44, VOX.INK, [1760, 792], 6.1, 0.3);
  VOX.footer(c, "MoSPI");
  VOX.finish(c);

  // 2) two comparable horizontal bars
  c = VOX.comp("V02_FEST_VS_MED_0016-0028", 8);
  VOX.headline(c, "Festivals vs", "medical", "emergencies", "Share of household spend, 2025");
  VOX.hbars(c, [["Five festival seasons", 4.5, VOX.OR], ["Medical emergencies", 5.2, VOX.COCOA]], {dec: 1, suf: "%"});
  VOX.txt(c, "NOTE", "Almost the same level.", VOX.SERIF_I, 50, VOX.INK, [160, 900], 3.0, 0.4);
  VOX.footer(c, "MoSPI");
  VOX.finish(c);

  // 3) sorted vertical bars, then (continuation shot) select + cover 85%
  c = VOX.comp("V03_CATEGORIES_85_0551-0601", 10.1);
  VOX.TOFF = -3;                                   // chart already built at frame 0 (continues the previous shot)
  VOX.headline(c, "What India", "actually", "buys for Diwali", "Share of ₹6.05 lakh crore festive trade");
  VOX.footer(c, "CAIT");
  var bars = VOX.vbars(c, [["Other", 19], ["Grocery", 12], ["Gold", 10], ["Electronics", 8], ["Durables", 7], ["Garments", 7], ["Décor", 5], ["Sweets", 5], ["Crackers", 0.9]],
    {hi: {1: VOX.COCOA, 8: VOX.OR}, step: 170});
  VOX.TOFF = 0;
  VOX.selectAndCover(c, bars, [168, 350, 1736, 948], {pct: 85, tBox: 1.3, tCover: 3.9, tArrow: 4.15,
    title: "traditional shopping", sub: "physical, local roadside shops"});
  VOX.finish(c);

  // 4) donut with leaders
  c = VOX.comp("V04_SPLIT_DONUT_0100-0108", 8);
  VOX.headline(c, "Where", "Onam's", "₹25,000 crore goes", "Kerala festive season");
  VOX.pie(c, [[40, VOX.OR, "Gold & jewellery — 40%"], [60, VOX.WGREY, "Everything else — 60%"]], [760, 610], 300, 120, 0.6, 1);
  VOX.footer(c, "script claim");
  VOX.finish(c);

  // 5) SaaS set-piece: question burst (only ?), ends on a dot
  c = VOX.comp("V05_GUESS_0031-0035", 4.9, {mblur: true});
  VOX.questionBurst(c, {burst: 0.76, wobble: 2.5, collapse: 3.95});
  VOX.finish(c);

  // 6) SaaS set-piece chain: timeline -> per-minute ring -> player progress counter (starts from that dot)
  c = VOX.comp("V06_PER_MINUTE_0035-0048", 12.5, {mblur: true});
  VOX.timeline(c, {from: "Navratri", to: "Diwali", ticks: 29, big: "30 days", small: "one festive month", tEnd: 1.3, tBig: 2.45, pushAt: 3.2});
  VOX.minuteRing(c, {tIn: 3.45, tSweep0: 3.6, tSweep1: 6.45, top: "every single minute", to: 14, pre: "₹", unit: "crore",
    tCount0: 4.6, tCount1: 5.7, under: "changes hands", tUnder: 5.95, tOut: 6.5});
  VOX.playerCounter(c, {tIn: 6.7, tFill0: 7.25, tFill1: 9.15, lengthSec: 728, to: 170, pre: "₹", tPlus: 9.9, unit: "crore", tUnit: 9.25,
    line: "spent on festivals across India", tLine: 10.3, label: "while you watch this video"});
  VOX.footer(c, "CAIT · ₹6.05 L Cr over 30 days ≈ ₹14 Cr a minute");
  VOX.finish(c);
});
