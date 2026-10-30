// FS VOX CHARTS kit — FirstSelfie x Vox / Johnny-Harris editorial chart system for After Effects (ExtendScript, ES3).
// Self-contained: no other #include needed. A job script does:
//   #include "C:/Users/<you>/.claude/skills/fs-vox-charts/kit/fs_vox_kit.jsx"
//   VOX.init({ root: "D:/.../AE/", logo: "D:/.../logo.png", aep: "D:/.../MY_JOB.aep", res: 4 });
//   var c = VOX.comp("V01_NAME_0012-0020", 8);      // paper BG already in
//   VOX.headline(c, "Festivals vs", "medical", "emergencies", "sub line");
//   ... primitives / charts ...
//   VOX.finish(c);                                  // grain + 12fps posterize + 4K scaler — ALWAYS last per comp
//   VOX.save();                                     // saves, logs, quits
// Everything is authored in 1920x1080 units. res:4 builds 3840x2160 comps with a SCALE_4K null (x2) so vectors stay sharp.
// Times are comp seconds. VOX.TOFF shifts kit animations (negative = already built at frame 0, for "continue from shot X").

var VOX = (function () {
  var V = {};
  V.PAPER = [0.965, 0.937, 0.894]; V.INK = [0.11, 0.09, 0.08]; V.GREY = [0.45, 0.42, 0.39]; V.WHITE = [1, 1, 1];
  V.OR = [1, 0.42, 0]; V.OL = [1, 0.686, 0.545]; V.COCOA = [0.227, 0.149, 0.094]; V.WGREY = [0.75, 0.71, 0.65]; V.PEACH = [1, 0.79, 0.64];
  V.SERIF = "TimesNewRomanPS-BoldMT"; V.SERIF_I = "TimesNewRomanPS-BoldItalicMT";
  V.SANS = "Inter-Regular"; V.SANS_L = "Inter-Light"; V.NUM = "BodoniModa-Bold";
  V.FPS = 25; V.TOFF = 0; V.DUR = 8; V.CUR = "";
  var K = 1, CW = 1920, CH = 1080, proj = null, cfg = {}, logoItem = null;
  var NOSCALE = {PAPER: 1, GRID: 1, PAPER_DOTS: 1, FINISH_GRAIN_POSTERIZE: 1, SCALE_4K: 1};

  // ---------------- low level ----------------
  function T(t) { return t + V.TOFF; }
  function tr(l) { return l.property("ADBE Transform Group"); }
  function sp(e, i, v) { try { e.property(i).setValue(v); } catch (x) {} }
  function fx(l, m) { try { return l.property("ADBE Effect Parade").addProperty(m); } catch (x) { return null; } }
  V.tr = tr; V.fx = fx; V.sp = sp; V.T = T;
  V.log = function (msg) {
    var f = new File((cfg.root || Folder.temp.fsName + "/") + "vox_build_log.txt"); f.encoding = "UTF-8"; f.open("a"); f.writeln(msg); f.close();
  };
  // AE keyframe ease (influence-based) — used by the classic kit reveals
  V.keys = function (prop, times, vals, infl) {
    for (var i = 0; i < times.length; i++) prop.setValueAtTime(times[i], vals[i]);
    var t = prop.propertyValueType, dims = 1;
    if (t == PropertyValueType.TwoD) dims = 2; else if (t == PropertyValueType.ThreeD) dims = 3;
    for (var k = 1; k <= prop.numKeys; k++) {
      var e = [], e2 = [];
      for (var d = 0; d < dims; d++) { e.push(new KeyframeEase(0, 33)); e2.push(new KeyframeEase(0, infl || 85)); }
      try { prop.setTemporalEaseAtKey(k, e, e2); } catch (err) {}
    }
  };
  // exact per-segment easing via expression: o = expo out (no overshoot), i = expo in-out, n = expo in, l = linear.
  // modes = one letter per segment ("oln"); extra = expression tail that uses v (e.g. 'v+Math.sin(time)*4'). Arrays: use add()/mul().
  V.ex = function (prop, times, vals, modes, extra) {
    for (var i = 0; i < times.length; i++) prop.setValueAtTime(times[i], vals[i]);
    for (var k = 1; k <= prop.numKeys; k++) prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.LINEAR);
    prop.expression = 'var M="' + (modes || "o") + '",n=numKeys,v=value;if(n>1){var i=1;while(i<n&&key(i+1).time<=time)i++;' +
      'if(time<=key(1).time)v=key(1).value;else if(i>=n)v=key(n).value;else{var a=key(i),b=key(i+1),t=(time-a.time)/(b.time-a.time),' +
      'c=M.charAt(Math.min(i-1,M.length-1)),e;if(c=="l")e=t;else if(c=="i")e=t<.5?Math.pow(2,20*t-10)/2:(2-Math.pow(2,-20*t+10))/2;' +
      'else if(c=="n")e=(Math.pow(2,10*t-10)-Math.pow(2,-10))/(1-Math.pow(2,-10));else e=(1-Math.pow(2,-10*t))/(1-Math.pow(2,-10));' +
      'v=add(a.value,mul(sub(b.value,a.value),e));}}' + (extra || 'v');
  };
  var seed = 20251020;
  V.seed = function (s) { seed = s; };
  V.rnd = function () { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  // effect params on layers under SCALE_4K are scaled by the parent automatically — never multiply them by K
  V.rough = function (l, amt) { var r = fx(l, "ADBE Roughen Edges"); if (r) { sp(r, 2, amt || 1.6); sp(r, 4, 40); } return r; };
  V.opOut = function (l) { var o = tr(l).property("ADBE Opacity"); o.setValueAtTime(V.DUR - 0.4, o.valueAtTime(V.DUR - 0.4, false)); o.setValueAtTime(V.DUR - 0.2, 0); };

  // ---------------- shapes ----------------
  V.shape = function (c, name) { var l = c.layers.addShape(); l.name = name; return l; };
  V.group = function (l) { return l.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group").property("ADBE Vectors Group"); };
  V.fill = function (v, col, op) { var f = v.addProperty("ADBE Vector Graphic - Fill"); f.property("ADBE Vector Fill Color").setValue(col); f.property("ADBE Vector Fill Opacity").setValue(op === undefined ? 100 : op); return f; };
  V.stroke = function (v, col, w, op, roundCap) {
    var s = v.addProperty("ADBE Vector Graphic - Stroke");
    s.property("ADBE Vector Stroke Color").setValue(col); s.property("ADBE Vector Stroke Width").setValue(w);
    s.property("ADBE Vector Stroke Opacity").setValue(op === undefined ? 100 : op);
    if (roundCap) s.property("ADBE Vector Stroke Line Cap").setValue(2);
    return s;
  };
  V.rect = function (c, name, w, h, rad, col, op, pos) {
    var l = V.shape(c, name), v = V.group(l), r = v.addProperty("ADBE Vector Shape - Rect");
    r.property("ADBE Vector Rect Size").setValue([w, h]); r.property("ADBE Vector Rect Roundness").setValue(rad);
    if (col) V.fill(v, col, op);
    tr(l).property("ADBE Position").setValue(pos || [960, 540]);
    return {layer: l, v: v};
  };
  // set the rect's own group offset so it grows from its left edge (x) or bottom (y)
  V.groupOffset = function (l, off) { l.property("ADBE Root Vectors Group").property(1).property("ADBE Vector Transform Group").property("ADBE Vector Position").setValue(off); };
  V.dot = function (c, name, d, col, pos) {
    var l = V.shape(c, name), v = V.group(l);
    v.addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([d, d]);
    V.fill(v, col); tr(l).property("ADBE Position").setValue(pos); return l;
  };
  V.ring = function (c, name, d, w, col, op, pos) {
    var l = V.shape(c, name), v = V.group(l);
    v.addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([d, d]);
    V.stroke(v, col, w, op, false); tr(l).property("ADBE Position").setValue(pos); return l;
  };
  // arc / ring segment: start/end % clockwise from 12 o'clock
  V.arcShape = function (c, name, d, w, col, startPct, endPct, pos) {
    var l = V.shape(c, name), v = V.group(l);
    v.addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([d, d]);
    v.addProperty("ADBE Vector Filter - Trim"); V.stroke(v, col, w, 100, false);
    var trm = l.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Filter - Trim");
    trm.property("ADBE Vector Trim Start").setValue(startPct); trm.property("ADBE Vector Trim End").setValue(endPct);
    tr(l).property("ADBE Position").setValue(pos || [960, 540]);
    return {layer: l, trim: trm};
  };
  V.path = function (c, name, pts, closed, col, w, trimmed) {
    var l = V.shape(c, name), v = V.group(l), pth = v.addProperty("ADBE Vector Shape - Group"), sh = new Shape();
    sh.vertices = pts; sh.closed = !!closed; pth.property("ADBE Vector Shape").setValue(sh);
    if (trimmed) v.addProperty("ADBE Vector Filter - Trim");
    var s = V.stroke(v, col, w, 100, true);
    try { s.property("ADBE Vector Stroke Line Join").setValue(2); } catch (x) {}
    tr(l).property("ADBE Position").setValue([0, 0]); tr(l).property("ADBE Anchor Point").setValue([0, 0]);
    var trm = trimmed ? l.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Filter - Trim") : null;
    return {layer: l, trim: trm, stroke: s};
  };
  V.dashes = function (stroke, dash, gap) {
    var ds = stroke.property("ADBE Vector Stroke Dashes");
    try { ds.addProperty("ADBE Vector Stroke Dash 1").setValue(dash || 12); ds.addProperty("ADBE Vector Stroke Gap 1").setValue(gap || 10); } catch (x) {}
  };
  V.nul = function (c, name, pos) {
    var n = c.layers.addNull(V.DUR); n.name = name;
    tr(n).property("ADBE Anchor Point").setValue(pos); tr(n).property("ADBE Position").setValue(pos); return n;
  };
  // parent layers to a group null without changing their values; optionally make them follow its opacity
  V.kids = function (layers, parent, linkOpacity) {
    for (var i = 0; i < layers.length; i++) {
      layers[i].setParentWithJump(parent);
      if (linkOpacity) tr(layers[i]).property("ADBE Opacity").expression = 'value*thisComp.layer("' + parent.name + '").transform.opacity/100';
    }
  };
  V.mark = function (c) { return c.numLayers; };                                  // call before building a group
  V.since = function (c, m) { var a = []; for (var i = 1; i <= c.numLayers - m; i++) a.push(c.layer(i)); return a; };

  // ---------------- type ----------------
  V.text = function (c, name, str, font, size, col, pos, just, tracking) {
    var l = c.layers.addText(str); l.name = name;
    var tp = l.property("ADBE Text Properties").property("ADBE Text Document"), td = tp.value;
    td.resetCharStyle(); td.font = font; td.fontSize = size; td.applyFill = true; td.fillColor = col; td.applyStroke = false;
    td.justification = just || ParagraphJustification.LEFT_JUSTIFY; td.tracking = tracking || 0;
    tp.setValue(td); tr(l).property("ADBE Position").setValue(pos);
    return l;
  };
  V.centerAnchor = function (l) { tr(l).property("ADBE Anchor Point").expression = 'var r=sourceRectAtTime(0,false);[r.left+r.width/2,r.top+r.height/2]'; };
  // Vox word-by-word reveal: opacity 0 + 22px rise, Based On = Words
  V.words = function (l, t0, dur) {
    var a = l.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
    var pr = a.property("ADBE Text Animator Properties");
    pr.addProperty("ADBE Text Opacity").setValue(0);
    pr.addProperty("ADBE Text Position 3D").setValue([0, 22, 0]);
    var sel = a.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    try { sel.property("ADBE Text Range Advanced").property("ADBE Text Range Type2").setValue(3); } catch (x) {}
    V.keys(sel.property("ADBE Text Percent Start"), [T(t0), T(t0 + (dur || 0.6))], [0, 100], 60);
  };
  V.txt = function (c, name, s, font, size, col, pos, t0, dur, just) {
    var l = V.text(c, name, s, font, size, col, pos, just || ParagraphJustification.LEFT_JUSTIFY, 0);
    if (t0 !== undefined && t0 !== null) V.words(l, t0, dur);
    V.opOut(l); return l;
  };
  V.ctxt = function (c, name, s, font, size, col, pos, t0, dur) { return V.txt(c, name, s, font, size, col, pos, t0, dur, ParagraphJustification.CENTER_JUSTIFY); };
  V.rtxt = function (c, name, s, font, size, col, pos, t0, dur) { return V.txt(c, name, s, font, size, col, pos, t0, dur, ParagraphJustification.RIGHT_JUSTIFY); };
  // number counter (cubic out). Note: Bodoni Moda has no ₹ glyph, AE falls back to Times for that layer — accepted look.
  V.counter = function (c, n, from, to, dec, pre, suf, font, size, col, pos, t0, t1) {
    var l = V.text(c, n, pre + to + suf, font, size, col, pos, ParagraphJustification.CENTER_JUSTIFY, 0);
    l.property("ADBE Text Properties").property("ADBE Text Document").expression =
      'var t=Math.min(1,Math.max(0,(time-' + T(t0) + ')/(' + (t1 - t0) + ')));t=1-Math.pow(1-t,3);' +
      'var v=' + from + '+(' + (to - from) + ')*t;"' + (pre || '') + '"+v.toFixed(' + (dec || 0) + ')+"' + (suf || '') + '"';
    var o = tr(l).property("ADBE Opacity"); o.setValueAtTime(T(t0 - 0.05), 0); o.setValueAtTime(T(t0), 100); V.opOut(l); return l;
  };
  // orange highlighter swipe under a text layer. hf = bar height / text height, pf = bar centre (0 top .. 1 baseline-ish).
  // Big numbers: hf 0.16, pf 1.02 (thin underline). Never put Roughen Edges on highlighters (eats them at 4K).
  V.hilite = function (c, tl, t0, t1, hf, pf, col) {
    hf = hf || 0.40; pf = pf || 0.80;
    var n = tl.name, hl = V.rect(c, n + "_HL", 100, 40, 3, col || V.OR, 55, [0, 0]).layer;
    hl.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").expression =
      'var r=thisComp.layer("' + n + '").sourceRectAtTime(time,false);[r.width+18, r.height*' + hf + ']';
    tr(hl).property("ADBE Anchor Point").expression = 'var r=thisComp.layer("' + n + '").sourceRectAtTime(time,false);[-(r.width+18)/2,0]';
    tr(hl).property("ADBE Position").expression =
      'var k=thisComp.layer("' + n + '"),r=k.sourceRectAtTime(time,false);[k.transform.position[0]+r.left-9, k.transform.position[1]+r.top+r.height*' + pf + ']';
    hl.moveAfter(tl);
    V.keys(tr(hl).property("ADBE Scale"), [T(t0), T(t1)], [[0, 100], [100, 100]], 70); V.opOut(hl);
    return hl;
  };
  // put layer b right after layer a on the same baseline (gap px)
  V.follow = function (b, aName, gap) {
    tr(b).property("ADBE Position").expression =
      'var k=thisComp.layer("' + aName + '"),r=k.sourceRectAtTime(time,false);[k.transform.position[0]+r.left+r.width+' + (gap || 16) + ', k.transform.position[1]]';
  };
  // headline: "p1 *kw* p2" — serif, keyword italic + highlighter; grey sans sub line. Layers H1/H_KEY/H2/SUB (one per comp).
  V.headline = function (c, p1, kw, p2, sub, y) {
    y = y || 170;
    V.txt(c, "H1", p1, V.SERIF, 62, V.INK, [160, y], 0.2, 0.5);
    var k = V.txt(c, "H_KEY", kw, V.SERIF_I, 62, V.INK, [0, y], 0.55, 0.3);
    tr(k).property("ADBE Position").expression = 'var p=thisComp.layer("H1");[p.transform.position[0]+p.sourceRectAtTime(time,false).width+16, p.transform.position[1]]';
    V.hilite(c, k, 0.9, 1.35, 0.42, 0.80);
    if (p2) { var b = V.txt(c, "H2", p2, V.SERIF, 62, V.INK, [0, y], 0.75, 0.4); V.follow(b, "H_KEY", 16); }
    if (sub) V.txt(c, "SUB", sub, V.SANS_L, 24, V.GREY, [162, y + 46], 0.9, 0.5);
  };
  V.footer = function (c, src, verify) {
    V.txt(c, "SRC", "Source: " + src + (verify === false ? "" : "  ·  to verify"), V.SANS_L, 18, V.GREY, [160, 1010], 0.4, 0.3);
    if (!logoItem) return;
    var lg = c.layers.add(logoItem); lg.name = "FS_LOGO";
    var s = 130 / lg.source.width * 100; tr(lg).property("ADBE Scale").setValue([s, s]);
    tr(lg).property("ADBE Position").setValue([1780, 1000]); tr(lg).property("ADBE Opacity").setValue(85);
  };

  // ---------------- background / finish ----------------
  V.paperBG = function (c) {
    var p = c.layers.addSolid(V.PAPER, "PAPER", CW, CH, 1, V.DUR);
    var g = c.layers.addSolid([1, 1, 1], "GRID", CW, CH, 1, V.DUR);
    var ge = fx(g, "ADBE Grid"); if (ge) { sp(ge, 4, 80 * K); sp(ge, 6, 2 * K); sp(ge, 12, V.INK); }
    g.blendingMode = BlendingMode.MULTIPLY; tr(g).property("ADBE Opacity").setValue(7);
    var rg = fx(g, "ADBE Roughen Edges"); if (rg) { sp(rg, 2, 1.2 * K); sp(rg, 4, 40 * K); }   // BG is unparented: scale by K here
    var d = c.layers.addSolid([0.5, 0.5, 0.5], "PAPER_DOTS", CW, CH, 1, V.DUR);
    fx(d, "ADBE Fractal Noise"); var ba = fx(d, "CC Ball Action"); if (ba) sp(ba, 2, 6 * K);
    var tn = fx(d, "ADBE Tint"); if (tn) { sp(tn, 1, [0.7, 0.62, 0.52]); sp(tn, 2, V.PAPER); }
    d.blendingMode = BlendingMode.MULTIPLY; tr(d).property("ADBE Opacity").setValue(18);
    g.moveToEnd(); d.moveToEnd(); p.moveToEnd();
  };
  // opts: {posterize:12|0, grain:6}
  V.finish = function (c, opts) {
    opts = opts || {};
    var a = c.layers.addSolid([0.5, 0.5, 0.5], "FINISH_GRAIN_POSTERIZE", CW, CH, 1, V.DUR); a.adjustmentLayer = true;
    var n = fx(a, "ADBE Noise"); if (n) sp(n, 1, opts.grain === undefined ? 6 : opts.grain);
    var pz = opts.posterize === undefined ? 12 : opts.posterize;
    if (pz) { var pt = fx(a, "ADBE Posterize Time"); if (pt) sp(pt, 1, pz); }
    if (K == 1) return;
    var s = c.layers.addNull(V.DUR); s.name = "SCALE_4K";
    tr(s).property("ADBE Anchor Point").setValue([0, 0]); tr(s).property("ADBE Position").setValue([0, 0]); tr(s).property("ADBE Scale").setValue([100 * K, 100 * K]);
    for (var i = 1; i <= c.numLayers; i++) { var l = c.layer(i); if (NOSCALE[l.name] || l.parent) continue; l.setParentWithJump(s); }
    s.enabled = false;
  };

  // ---------------- project ----------------
  // cfg: root (folder for log, trailing /), logo (png path, copy it into the job/package folder first), aep (save path), res (1|4)
  V.init = function (o) {
    cfg = o || {}; K = cfg.res == 4 ? 2 : 1; CW = 1920 * K; CH = 1080 * K;
    app.beginSuppressDialogs();
    try { if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); } catch (e) {}
    app.newProject(); proj = app.project;
    if (cfg.logo && new File(cfg.logo).exists) logoItem = proj.importFile(new ImportOptions(new File(cfg.logo)));
    V.log("---- VOX build " + (cfg.aep || "") + " res=" + (K == 2 ? "4K" : "1080"));
    return proj;
  };
  // opts: {mblur:true} for fast SaaS-style motion (shutter 200, 16 samples)
  V.comp = function (id, dur, opts) {
    opts = opts || {}; V.CUR = id; V.DUR = dur; V.TOFF = 0;
    var c = proj.items.addComp(id, CW, CH, 1, dur, V.FPS);
    c.motionBlur = !!opts.mblur; if (opts.mblur) { c.shutterAngle = 200; c.motionBlurSamplesPerFrame = 16; }
    V.paperBG(c); return c;
  };
  V.run = function (fn) {
    try { fn(); V.log("built ok"); }
    catch (e) { V.log("ERROR in " + V.CUR + " line " + e.line + ": " + e.toString()); }
    V.save();
  };
  V.save = function () {
    try { proj.save(new File(cfg.aep)); V.log("saved " + cfg.aep); } catch (e) { V.log("SAVE ERROR " + e.toString()); }
    app.endSuppressDialogs(false);
    try { app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); } catch (e2) {}
    if (cfg.quit !== false) app.quit();
  };

  // ======================= CHARTS (all take data + start time; return the main layers) =======================
  // horizontal bar growing left->right
  V.hbar = function (c, n, x, y, w, h, col, t0) {
    var r = V.rect(c, n, w, h, 2, col, 100, [x, y]); V.groupOffset(r.layer, [w / 2, 0]);
    V.keys(tr(r.layer).property("ADBE Scale"), [T(t0), T(t0 + 0.7)], [[0, 100], [100, 100]], 70);
    V.rough(r.layer, 1.5); V.opOut(r.layer); return r.layer;
  };
  // vertical bar growing from the baseline
  V.vbar = function (c, n, x, base, w, h, col, t0) {
    var r = V.rect(c, n, w, h, 2, col, 100, [x, base]); V.groupOffset(r.layer, [0, -h / 2]);
    V.keys(tr(r.layer).property("ADBE Scale"), [T(t0), T(t0 + 0.6)], [[100, 0], [100, 100]], 70);
    V.rough(r.layer, 1.5); V.opOut(r.layer); return r.layer;
  };
  // rows: [[label, value, colour], ...]; scale px per unit; unit suffix e.g. "%"
  V.hbars = function (c, rows, opt) {
    opt = opt || {}; var y0 = opt.y0 || 480, gap = opt.gap || 200, sc = opt.scale || 260, t0 = opt.t0 || 0.6, out = [];
    for (var i = 0; i < rows.length; i++) {
      var y = y0 + i * gap, w = rows[i][1] * sc;
      V.txt(c, "HB_L" + i, rows[i][0], V.SANS, 30, V.INK, [160, y], t0 + i * 0.6, 0.4);
      out.push(V.hbar(c, "HB_" + i, 160, y + 60, w, opt.h || 80, rows[i][2] || V.OR, t0 + 0.2 + i * 0.6));
      V.counter(c, "HB_V" + i, 0, rows[i][1], opt.dec || 0, opt.pre || "", opt.suf || "", V.NUM, 60, rows[i][2] || V.OR, [160 + w + 110, y + 82], t0 + 0.4 + i * 0.6, t0 + 1.2 + i * 0.6);
    }
    return out;
  };
  // cats: [[label, value], ...] sorted; hiIdx: {index: colour}; returns all chart layers (for VOX.kids grouping)
  V.vbars = function (c, cats, opt) {
    opt = opt || {}; var m = V.mark(c), x0 = opt.x0 || 230, step = opt.step || 112, base = opt.base || 880, sc = opt.scale || 26, t0 = opt.t0 || 0.8, hi = opt.hi || {};
    for (var j = 0; j < cats.length; j++) {
      var x = x0 + j * step, h = Math.max(cats[j][1] * sc, 6), col = hi[j] || V.WGREY;
      V.vbar(c, "VB_" + j, x, base, opt.w || 56, h, col, t0 + j * 0.08);
      V.txt(c, "VB_L" + j, cats[j][0], V.SANS, 18, V.INK, [x - 40, base + 35], t0 + 0.1 + j * 0.08, 0.2);
      V.txt(c, "VB_V" + j, cats[j][1] < 1 ? "<1" + (opt.suf || "%") : cats[j][1] + (opt.suf || "%"), V.NUM, 26, hi[j] == V.OR ? V.OR : V.INK, [x - 22, base - 10 - h], t0 + 0.6 + j * 0.08, 0.2);
    }
    return V.since(c, m);
  };
  // ring counter: grey track + orange value arc + big % in the middle
  V.ringCounter = function (c, pct, ctr, d, t0) {
    var a = V.arcShape(c, "RING_TRACK", d, 26, V.WGREY, 0, 0, ctr); V.keys(a.trim.property("ADBE Vector Trim End"), [T(t0), T(t0 + 0.8)], [0, 100], 75); V.rough(a.layer, 1.5); V.opOut(a.layer);
    var b = V.arcShape(c, "RING_VALUE", d, 26, V.OR, 0, 0, ctr); V.keys(b.trim.property("ADBE Vector Trim End"), [T(t0 + 0.8), T(t0 + 2)], [0, pct], 75); V.rough(b.layer, 1.5); V.opOut(b.layer);
    return V.counter(c, "PCT", 0, pct, pct % 1 ? 1 : 0, "", "%", V.NUM, 150, V.OR, [ctr[0], ctr[1] + 50], t0 + 0.8, t0 + 2);
  };
  // pie / donut with leader lines. slices: [[pct, colour, label], ...]; w = stroke width (= d for full pie); side 1 right, -1 left
  V.pie = function (c, slices, ctr, d, w, t0, side) {
    var cum = 0, R = d / 2 + w / 2;
    for (var i = 0; i < slices.length; i++) {
      var s = slices[i], a = V.arcShape(c, "SLICE_" + i, d, w, s[1], cum, cum, ctr);
      V.keys(a.trim.property("ADBE Vector Trim End"), [T(t0 + i * 0.15), T(t0 + i * 0.15 + 0.8)], [cum, Math.min(100, cum + s[0])], 75); V.rough(a.layer, 1.5); V.opOut(a.layer);
      var m = (cum + s[0] / 2) / 100 * 2 * Math.PI, ex = ctr[0] + Math.sin(m) * R, ey = ctr[1] - Math.cos(m) * R;
      var lx = side < 0 ? ctr[0] - R - 220 : ctr[0] + R + 140, ly = 330 + i * (560 / slices.length);
      var ld = V.path(c, "LEADER_" + i, [[ex, ey], [(ex + lx) / 2, ly], [lx, ly]], false, V.INK, 2, true);
      V.keys(ld.trim.property("ADBE Vector Trim End"), [T(t0 + 0.9 + i * 0.1), T(t0 + 1.4 + i * 0.1)], [0, 100], 70); V.opOut(ld.layer);
      var lb = V.txt(c, "LABEL_" + i, s[2], V.SANS, 26, V.INK, [lx + (side < 0 ? -40 : 34), ly + 9], t0 + 1.3 + i * 0.1, 0.4, side < 0 ? ParagraphJustification.RIGHT_JUSTIFY : null);
      var key = V.dot(c, "KEY_" + i, 16, s[1], [lx + (side < 0 ? -20 : 16), ly]); V.keys(tr(key).property("ADBE Opacity"), [T(t0 + 1.2 + i * 0.1), T(t0 + 1.4 + i * 0.1)], [0, 100]); V.opOut(key);
      cum += s[0];
    }
  };
  // hemicycle (half donut): parts [[pct of half, colour], ...] totalling 100
  V.hemicycle = function (c, parts, ctr, d, w, t0) {
    var cum = 0, out = [];
    for (var i = 0; i < parts.length; i++) {
      var a = V.arcShape(c, "HEMI_" + i, d, w, parts[i][1], cum / 2, cum / 2, ctr);
      tr(a.layer).property("ADBE Rotate Z").setValue(-90);
      V.keys(a.trim.property("ADBE Vector Trim End"), [T(t0 + i * 0.6), T(t0 + i * 0.6 + 1.2)], [cum / 2, (cum + parts[i][0]) / 2], 75); V.rough(a.layer, 1.5); V.opOut(a.layer);
      out.push(a.layer); cum += parts[i][0];
    }
    return out;
  };
  // line chart: pts in px; axes optional
  V.lineChart = function (c, pts, col, t0, t1, axes) {
    if (axes) {
      var ax = V.path(c, "AXIS_X", [[axes[0], axes[3]], [axes[2], axes[3]]], false, V.GREY, 2, true); V.keys(ax.trim.property("ADBE Vector Trim End"), [T(t0 - 0.7), T(t0 - 0.2)], [0, 100], 70); V.opOut(ax.layer);
      var ay = V.path(c, "AXIS_Y", [[axes[0], axes[1]], [axes[0], axes[3]]], false, V.GREY, 2, true); V.keys(ay.trim.property("ADBE Vector Trim End"), [T(t0 - 0.7), T(t0 - 0.2)], [0, 100], 70); V.opOut(ay.layer);
    }
    var l = V.path(c, "LINE", pts, false, col || V.OR, 7, true); V.keys(l.trim.property("ADBE Vector Trim End"), [T(t0), T(t1)], [0, 100], 70); V.opOut(l.layer); return l.layer;
  };
  // big hero number + unit line (e.g. ₹219.64 / lakh crore)
  V.bigNumber = function (c, to, dec, pre, suf, unit, t0, t1, pos) {
    pos = pos || [960, 590];
    var n = V.counter(c, "BIG_NUM", 0, to, dec, pre, suf, V.NUM, 230, V.OR, pos, t0, t1);
    if (unit) V.ctxt(c, "BIG_UNIT", unit, V.SERIF_I, 72, V.COCOA, [pos[0], pos[1] + 90], t1 - 0.35, 0.5);
    return n;
  };
  // search pill that types a query, then an answer line
  V.searchBar = function (c, query, answer, sub, tAns) {
    var bar = V.rect(c, "SEARCH_BAR", 1100, 96, 48, V.WHITE, 100, [960, 520]); V.stroke(bar.v, V.WGREY, 2, 100, false);
    V.keys(tr(bar.layer).property("ADBE Scale"), [T(0.3), T(0.8)], [[60, 60], [100, 100]], 70); V.opOut(bar.layer);
    var q = V.text(c, "QUERY", "", V.SANS, 34, V.INK, [480, 532]);
    q.property("ADBE Text Properties").property("ADBE Text Document").expression = 'var s="' + query + '";var n=Math.floor(Math.max(0,(time-' + T(0.9) + '))*22);s.substr(0,n)+((Math.floor(time*2)%2)?"|":"")';
    V.opOut(q);
    V.txt(c, "ANSWER", answer, V.NUM, 110, V.OR, [480, 760], tAns, 0.4);
    if (sub) V.txt(c, "ANSWER_SUB", sub, V.SERIF_I, 40, V.COCOA, [486, 820], tAns + 0.4, 0.4);
  };

  // ======================= CALL-OUTS on an existing chart =======================
  // "select" a built chart: the chart (layers) steps back (scale/pos), a hand-drawn orange box locks round it,
  // a colour cover sweeps to pct% of the box, a dashed divider + rest label, an arrow to a big % call-out at the right.
  // box = [x0,y0,x1,y1] in chart units. o = {pct, tBox, tCover, tArrow, title, sub, restLabel, scale, toPos, anchor, callout:[x,y]}
  V.selectAndCover = function (c, chartLayers, box, o) {
    var BX0 = box[0], BY0 = box[1], BX1 = box[2], BY1 = box[3], BW = BX1 - BX0, BH = BY1 - BY0, P = o.pct / 100, s = (o.scale || 72) / 100;
    var bx = V.path(c, "SELECT_BOX", [[BX0, BY0], [BX1, BY0], [BX1, BY1], [BX0, BY1]], true, V.OR, 7, true);
    V.ex(bx.trim.property("ADBE Vector Trim End"), [o.tBox, o.tBox + 1], [0, 100], "o"); V.opOut(bx.layer);
    var cov = V.rect(c, "COVER", BW * P, BH, 2, V.OR, 100, [BX0, (BY0 + BY1) / 2]); V.groupOffset(cov.layer, [BW * P / 2, 0]);
    cov.layer.blendingMode = BlendingMode.MULTIPLY; tr(cov.layer).property("ADBE Opacity").setValue(42);
    V.ex(tr(cov.layer).property("ADBE Scale"), [o.tCover, o.tCover + 1], [[0, 100], [100, 100]], "o"); V.rough(cov.layer, 1.6); V.opOut(cov.layer);
    var DX = BX0 + BW * P, dv = V.path(c, "DIVIDER", [[DX, BY0], [DX, BY1]], false, V.INK, 3, true); V.dashes(dv.stroke);
    V.ex(dv.trim.property("ADBE Vector Trim End"), [o.tCover + 0.9, o.tCover + 1.4], [0, 100], "o"); V.opOut(dv.layer);
    var r1 = V.ctxt(c, "REST_PCT", (100 - o.pct) + "%", V.NUM, 40, V.GREY, [(DX + BX1) / 2, BY0 + 64], o.tCover + 1.3, 0.3);
    var r2 = V.ctxt(c, "REST_L", o.restLabel || "everything\relse", V.SANS, 20, V.GREY, [(DX + BX1) / 2, BY0 + 96], o.tCover + 1.4, 0.3);
    var an = o.anchor || [190, 940], to = o.toPos || [170, 905], g = V.nul(c, "CHART_GROUP", an);
    V.kids(chartLayers.concat([bx.layer, cov.layer, dv.layer, r1, r2]), g, false);
    V.ex(tr(g).property("ADBE Scale"), [0.3, 1.2], [[100, 100], [s * 100, s * 100]], "i");
    V.ex(tr(g).property("ADBE Position"), [0.3, 1.2], [an, to], "i");
    // world position of the cover's right edge middle -> arrow start
    var cx = to[0] + (DX - 60 - an[0]) * s, cy = to[1] + ((BY0 + BY1) / 2 - 60 - an[1]) * s, co = o.callout || [1585, 580];
    var a1 = [co[0] - 335, co[1] + 70], a2 = [co[0] - 240, co[1] + 12];
    var ar = V.path(c, "ARROW", [[cx, cy], a1, a2], false, V.INK, 4, true);
    V.ex(ar.trim.property("ADBE Vector Trim End"), [o.tArrow, o.tArrow + 0.6], [0, 100], "o"); V.opOut(ar.layer);
    var hd = V.path(c, "ARROW_HEAD", [[-18, -12], [0, 0], [-18, 12]], false, V.INK, 4, false);
    tr(hd.layer).property("ADBE Position").setValue(a2); tr(hd.layer).property("ADBE Rotate Z").setValue(Math.atan2(a2[1] - a1[1], a2[0] - a1[0]) * 180 / Math.PI);
    V.ex(tr(hd.layer).property("ADBE Scale"), [o.tArrow + 0.53, o.tArrow + 0.75], [[0, 0], [100, 100]], "o"); V.opOut(hd.layer);
    V.counter(c, "BIG_PCT", 0, o.pct, 0, "", "%", V.NUM, 210, V.OR, co, o.tArrow - 0.05, o.tArrow + 0.75);
    if (o.title) { var tl = V.ctxt(c, "CALL_T", o.title, V.SERIF_I, 42, V.INK, [co[0], co[1] + 80], o.tArrow + 1.5, 0.5); V.hilite(c, tl, o.tArrow + 1.9, o.tArrow + 2.4); }
    if (o.sub) V.ctxt(c, "CALL_S", o.sub, V.SANS, 26, V.GREY, [co[0], co[1] + 128], o.tArrow + 2.3, 0.9);
    return g;
  };

  // ======================= SaaS-motion set-pieces (use VOX.comp(...,{mblur:true})) =======================
  // seed dot -> big "?" + shock ring -> field of small "?" (each a dot that flies out and morphs) -> collapse to a dot.
  // t = {seed:0.15, burst:0.76, wobble:2.5, collapse:3.95}; ends with END_DOT (34px orange, centre) — hand-off to next shot.
  V.questionBurst = function (c, t) {
    t = t || {}; var B = t.burst || 0.76, W = t.wobble || 2.5, CL = t.collapse || 3.95, C = [960, 540], marks = 0;
    var md = V.dot(c, "SEED_DOT", 34, V.OR, C);
    V.ex(tr(md).property("ADBE Scale"), [B - 0.61, B - 0.31, B - 0.14, B, B + 0.19], [[0, 0], [100, 100], [70, 70], [70, 70], [260, 260]], "oilo");
    V.ex(tr(md).property("ADBE Opacity"), [B + 0.02, B + 0.19], [100, 0], "o");
    var sh = V.ring(c, "SHOCK_RING", 100, 8, V.OR, 100, C);
    V.ex(tr(sh).property("ADBE Scale"), [B, B + 0.69], [[30, 30], [1500, 1500]], "o");
    V.ex(sh.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Graphic - Stroke").property("ADBE Vector Stroke Width"), [B, B + 0.69], [8, 0.3], "o");
    V.ex(tr(sh).property("ADBE Opacity"), [B - 0.02, B + 0.02, B + 0.69], [0, 80, 0], "lo");
    for (var gy = 0; gy < 6; gy++) for (var gx = 0; gx < 10; gx++) {
      var px = 192 * (gx + 0.5) + (V.rnd() - 0.5) * 100, py = 180 * (gy + 0.5) + (V.rnd() - 0.5) * 90;
      if (Math.pow((px - 960) / 340, 2) + Math.pow((py - 540) / 270, 2) < 1) continue;
      var dd = Math.sqrt(Math.pow(px - 960, 2) + Math.pow(py - 540, 2)) / 1100, sz = 40 + V.rnd() * 70, rr = -25 + V.rnd() * 50, ph = V.rnd() * 6.28, pick = V.rnd();
      var mc = pick < 0.22 ? V.OR : (pick < 0.55 ? V.INK : (pick < 0.8 ? V.COCOA : V.WGREY));
      var L = B + 0.04 + dd * 0.25 + V.rnd() * 0.05, A = L + 0.5, tc = CL + dd * 0.12 + V.rnd() * 0.05;
      var q = V.text(c, "Q_" + marks, t.glyph || "?", V.SERIF, sz, mc, [px, py], ParagraphJustification.CENTER_JUSTIFY, 0);
      V.centerAnchor(q);
      tr(q).property("ADBE Position").expression = 'add(value,[Math.sin(time*0.9+' + ph + ')*6,Math.cos(time*0.7+' + ph + ')*6])';
      V.ex(tr(q).property("ADBE Scale"), [A - 0.04, A + 0.3, tc, tc + 0.12], [[0, 0], [100, 100], [100, 100], [0, 0]], "oln");
      V.ex(tr(q).property("ADBE Rotate Z"), [A - 0.04, A + 0.35], [rr - 70, rr], "o", 'v+Math.sin(time*' + (1 + V.rnd()).toFixed(2) + '+' + ph + ')*5');
      tr(q).property("ADBE Opacity").setValue(mc == V.WGREY ? 100 : 88); q.motionBlur = true;
      var qd = V.dot(c, "QD_" + marks, Math.max(8, sz * 0.22), mc, C);
      V.ex(tr(qd).property("ADBE Position"), [L, A, tc, tc + 0.45], [C, [px, py], [px, py], C], "oln");
      V.ex(tr(qd).property("ADBE Scale"), [L, L + 0.08, A - 0.02, A + 0.1, tc, tc + 0.08, tc + 0.38, tc + 0.45], [[0, 0], [100, 100], [100, 100], [0, 0], [0, 0], [100, 100], [100, 100], [0, 0]], "olololn");
      qd.motionBlur = true; marks++;
    }
    var bq = V.text(c, "BIG_Q", t.glyph || "?", V.SERIF, 520, V.OR, C, ParagraphJustification.CENTER_JUSTIFY, 0);
    V.centerAnchor(bq);
    V.ex(tr(bq).property("ADBE Scale"), [B, B + 0.44, CL + 0.3, CL + 0.65], [[20, 20], [100, 100], [100, 100], [0, 0]], "oln", 'add(v,mul([1,1],Math.sin(Math.max(0,time-' + (B + 0.44) + ')*2.2)*1.5))');
    V.ex(tr(bq).property("ADBE Rotate Z"), [B, B + 0.44, W, W + 0.22, W + 0.45, W + 0.7], [-35, 0, 0, -12, 7, 0], "oliii");
    V.ex(tr(bq).property("ADBE Opacity"), [B, B + 0.08], [0, 100], "o");
    var gb = fx(bq, "ADBE Gaussian Blur 2"); if (gb) V.ex(gb.property("ADBE Gaussian Blur 2-0001"), [B, B + 0.24], [30, 0], "o");
    bq.motionBlur = true;
    var ed = V.dot(c, "END_DOT", 34, V.OR, C); V.ex(tr(ed).property("ADBE Scale"), [CL + 0.5, CL + 0.8], [[0, 0], [100, 100]], "o");
    return marks;
  };
  // timeline: dot at centre slides to the left end, line draws, day ticks count in, end dot + labels, big centre label.
  // o = {from:"Navratri", to:"Diwali", ticks:29, big:"30 days", small:"one festive month", tEnd:1.3, tBig:2.45, pushAt:3.2}
  // returns the group null (pushes in + fades at o.pushAt when given)
  V.timeline = function (c, o) {
    var C = [960, 540], m = V.mark(c);
    var d0 = V.dot(c, "TL_START_DOT", 34, V.OR, C); V.ex(tr(d0).property("ADBE Position"), [0, 0.55], [C, [360, 540]], "i");
    var tl = V.path(c, "TL_LINE", [[360, 540], [1560, 540]], false, V.INK, 4, true);
    V.ex(tl.trim.property("ADBE Vector Trim End"), [0.4, (o.tEnd || 1.3) + 0.05], [0, 100], "o");
    var n = o.ticks || 29, tk = V.shape(c, "TL_TICKS"), tv = V.group(tk), tp = tv.addProperty("ADBE Vector Shape - Group"), ts = new Shape();
    ts.vertices = [[0, -16], [0, 16]]; ts.closed = false; tp.property("ADBE Vector Shape").setValue(ts); V.stroke(tv, V.WGREY, 3, 100, true);
    var rep = tv.addProperty("ADBE Vector Filter - Repeater");
    rep.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([1200 / (n + 1), 0]);
    tr(tk).property("ADBE Position").setValue([360 + 1200 / (n + 1), 540]);
    V.ex(rep.property("ADBE Vector Repeater Copies"), [0.45, (o.tEnd || 1.3) + 0.05], [0, n], "o", 'Math.round(v)');
    var d1 = V.dot(c, "TL_END_DOT", 34, V.OR, [1560, 540]); V.ex(tr(d1).property("ADBE Scale"), [o.tEnd || 1.3, (o.tEnd || 1.3) + 0.25], [[0, 0], [100, 100]], "o");
    V.ctxt(c, "TL_FROM", o.from, V.SERIF_I, 44, V.INK, [360, 615], 0.1, 0.4);
    V.ctxt(c, "TL_TO", o.to, V.SERIF_I, 44, V.INK, [1560, 615], o.tEnd || 1.3, 0.4);
    if (o.big) V.ctxt(c, "TL_BIG", o.big, V.NUM, 120, V.INK, [960, 470], o.tBig || 2.45, 0.4);
    if (o.small) V.ctxt(c, "TL_SMALL", o.small, V.SANS_L, 28, V.GREY, [960, 615], (o.tBig || 2.45) + 0.3, 0.5);
    var g = V.nul(c, "G_TIMELINE", C); V.kids(V.since(c, m).slice(1), g, true);
    if (o.pushAt) { V.ex(tr(g).property("ADBE Scale"), [o.pushAt, o.pushAt + 0.55], [[100, 100], [520, 520]], "n"); V.ex(tr(g).property("ADBE Opacity"), [o.pushAt + 0.2, o.pushAt + 0.55], [100, 0], "l"); }
    return g;
  };
  // per-minute clock: ring sweep + 60 ticks + orbit knob, a counter in the middle, a line under.
  // o = {tIn, tSweep0, tSweep1, top:"every single minute", to:14, pre:"₹", unit:"crore", tCount0, tCount1, under:"changes hands", tUnder, tOut}
  V.minuteRing = function (c, o) {
    var C = [960, 540], m = V.mark(c);
    var trk = V.arcShape(c, "MIN_TRACK", 520, 14, V.WGREY, 0, 100, C);
    var sw = V.arcShape(c, "MIN_SWEEP", 520, 14, V.OR, 0, 0, C); V.rough(sw.layer, 1.2);
    V.ex(sw.trim.property("ADBE Vector Trim End"), [o.tSweep0, o.tSweep1], [0, 100], "l");
    var mt = V.shape(c, "MIN_TICKS"), mv = V.group(mt), mp = mv.addProperty("ADBE Vector Shape - Group"), ms = new Shape();
    ms.vertices = [[0, -300], [0, -288]]; ms.closed = false; mp.property("ADBE Vector Shape").setValue(ms); V.stroke(mv, V.INK, 3, 100, true);
    var mr = mv.addProperty("ADBE Vector Filter - Repeater"); mr.property("ADBE Vector Repeater Copies").setValue(60);
    mr.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([0, 0]);
    mr.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Rotation").setValue(6);
    tr(mt).property("ADBE Position").setValue(C);
    var kn = V.dot(c, "MIN_KNOB", 30, V.OR, C); V.groupOffset(kn, [0, -260]);
    V.ex(tr(kn).property("ADBE Rotate Z"), [o.tSweep0, o.tSweep1], [0, 360], "l");
    if (o.top) V.ctxt(c, "MIN_TOP", o.top, V.SANS, 28, V.GREY, [960, 450], o.tCount0 - 0.5, 0.5);
    V.counter(c, "MIN_NUM", 0, o.to, 0, o.pre || "", o.suf || "", V.NUM, 190, V.OR, [960, 600], o.tCount0, o.tCount1);
    if (o.unit) V.ctxt(c, "MIN_UNIT", o.unit, V.SERIF_I, 56, V.COCOA, [960, 672], o.tCount1 - 0.05, 0.3);
    if (o.under) { var u = V.ctxt(c, "MIN_UNDER", o.under, V.SERIF_I, 54, V.INK, [960, 905], o.tUnder, 0.5); V.hilite(c, u, o.tUnder + 0.1, o.tUnder + 0.5); }
    var g = V.nul(c, "G_MINUTE", C); V.kids(V.since(c, m).slice(1), g, true);
    V.ex(tr(g).property("ADBE Scale"), [o.tIn, o.tIn + 0.5, o.tOut, o.tOut + 0.4], [[40, 40], [100, 100], [100, 100], [0, 0]], "oln");
    V.ex(tr(g).property("ADBE Opacity"), [o.tIn, o.tIn + 0.25, o.tOut + 0.1, o.tOut + 0.4], [0, 100, 100, 0], "lll");
    return g;
  };
  // "while you watch this video" player card: progress fills, timecode runs to o.length (mm:ss), big counter tied to progress.
  // o = {tIn, tFill0, tFill1, lengthSec:728, to:170, pre:"₹", tPlus, unit:"crore", tUnit, line:"spent on festivals across India", tLine, label:"while you watch this video"}
  V.playerCounter = function (c, o) {
    var len = o.lengthSec || 728, mm = Math.floor(len / 60), ss = len % 60, LEN = (mm < 10 ? "0" : "") + mm + ":" + (ss < 10 ? "0" : "") + ss;
    var card = V.rect(c, "PLAYER_CARD", 1480, 140, 28, V.WHITE, 100, [960, 870]); V.stroke(card.v, V.WGREY, 2, 100, false);
    var sh = fx(card.layer, "ADBE Drop Shadow"); if (sh) { sp(sh, 2, 22); sp(sh, 3, 180); sp(sh, 4, 10); sp(sh, 5, 40); }
    V.ex(tr(card.layer).property("ADBE Position"), [o.tIn, o.tIn + 0.5], [[960, 950], [960, 870]], "o");
    V.ex(tr(card.layer).property("ADBE Opacity"), [o.tIn, o.tIn + 0.25], [0, 100], "l"); V.opOut(card.layer);
    var kidsC = [], TX0 = -400, TW = 1080;
    var play = V.shape(c, "PLAY_ICON"), pv = V.group(play), pg = pv.addProperty("ADBE Vector Shape - Group"), ps = new Shape();
    ps.vertices = [[-12, -16], [16, 0], [-12, 16]]; ps.closed = true; pg.property("ADBE Vector Shape").setValue(ps); V.fill(pv, V.INK);
    tr(play).property("ADBE Position").setValue([-670, 0]); kidsC.push(play);
    var tt = V.text(c, "TIMECODE", "00:00 / " + LEN, V.SANS, 26, V.INK, [-630, 9]);
    tt.property("ADBE Text Properties").property("ADBE Text Document").expression =
      'var p=thisComp.layer("PROGRESS_FILL").transform.scale[0]/100,s=Math.round(p*' + len + '),m=Math.floor(s/60),q=s%60;(m<10?"0":"")+m+":"+(q<10?"0":"")+q+" / ' + LEN + '"';
    kidsC.push(tt);
    kidsC.push(V.rect(c, "PROGRESS_TRACK", TW, 10, 5, V.WGREY, 100, [TX0 + TW / 2, 0]).layer);
    var fl = V.rect(c, "PROGRESS_FILL", TW, 10, 5, V.OR, 100, [TX0, 0]); V.groupOffset(fl.layer, [TW / 2, 0]);
    V.ex(tr(fl.layer).property("ADBE Scale"), [o.tFill0, o.tFill1], [[0, 100], [100, 100]], "i"); kidsC.push(fl.layer);
    var kn = V.dot(c, "PROGRESS_KNOB", 28, V.WHITE, [TX0, 0]); V.stroke(kn.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group"), V.OR, 5, 100, false);
    tr(kn).property("ADBE Position").expression = '[' + TX0 + '+' + TW + '*thisComp.layer("PROGRESS_FILL").transform.scale[0]/100, 0]'; kidsC.push(kn);
    V.kids(kidsC, card.layer, true);   // children were authored in card-local units
    if (o.label) V.txt(c, "PLAYER_LABEL", o.label, V.SANS, 26, V.GREY, [224, 770], o.tIn + 0.05, 0.6);
    var big = V.text(c, "PLAYER_NUM", (o.pre || "") + o.to, V.NUM, 250, V.OR, [960, 470], ParagraphJustification.CENTER_JUSTIFY, 0);
    big.property("ADBE Text Properties").property("ADBE Text Document").expression = '"' + (o.pre || "") + '"+Math.round(' + o.to + '*thisComp.layer("PROGRESS_FILL").transform.scale[0]/100)';
    V.ex(tr(big).property("ADBE Opacity"), [o.tFill0 - 0.15, o.tFill0 + 0.05], [0, 100], "o"); V.opOut(big);
    if (o.tPlus) { var pl = V.txt(c, "PLAYER_PLUS", "+", V.NUM, 250, V.OR, [0, 470], o.tPlus, 0.2); V.follow(pl, "PLAYER_NUM", 6); V.hilite(c, big, o.tPlus + 0.05, o.tPlus + 0.45, 0.16, 1.02); }
    if (o.unit) V.ctxt(c, "PLAYER_UNIT", o.unit, V.SERIF_I, 70, V.COCOA, [960, 568], o.tUnit || o.tFill1, 0.3);
    if (o.line) V.ctxt(c, "PLAYER_LINE", o.line, V.SERIF_I, 54, V.INK, [960, 668], o.tLine, 0.7);
    return card.layer;
  };
  return V;
})();
