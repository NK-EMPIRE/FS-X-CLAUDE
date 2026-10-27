// Editable title: "THE MOST / EXPENSIVE / FESTIVAL IN INDIA". Live text, gold styling on the text itself,
// all colours/glow/sweep driven from the "TITLE CONTROLS" layer.
(function () {
var OUTD = "D:/FS DOCUMENTARY INTRO/downloads/3d_motion_intros/renders/AE_PROJECT/";
var LOG = new File("D:/aetmp/fsintro/out/title_log.txt"); LOG.open("w");
function log(s) { LOG.writeln(s); }
try {
app.beginSuppressDialogs();
if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
var proj = app.newProject();
var W = 1920, H = 1080, FPS = 24, DUR = 6.0, CY = 540;
function dims(p) { var t = p.propertyValueType; if (t == PropertyValueType.TwoD_SPATIAL || t == PropertyValueType.ThreeD_SPATIAL || t == PropertyValueType.OneD) return 1; var v = p.value; return (v instanceof Array) ? v.length : 1; }
function keys(p, list, ease) {
    for (var i = 0; i < list.length; i++) p.setValueAtTime(list[i][0], list[i][1]);
    if (!ease) return; var n = dims(p);
    for (var k = 1; k <= p.numKeys; k++) { var e = []; for (var d = 0; d < n; d++) e.push(new KeyframeEase(0, ease)); p.setTemporalEaseAtKey(k, e, e); }
}
function fx(l, m, name) { var e = l.property("ADBE Effect Parade").addProperty(m); if (name) e.name = name; return e; }
function tr(l, n) { return l.property("ADBE Transform Group").property(n); }
var fSol = proj.items.addFolder("SOLIDS");
var c = proj.items.addComp("TITLE  (edit text here, render this)", W, H, 1, DUR, FPS); c.bgColor = [0, 0, 0];

// ---- controls
var ctl = c.layers.addNull(DUR); ctl.name = "TITLE CONTROLS"; ctl.source.name = "TITLE CONTROLS"; ctl.source.parentFolder = fSol;
function cc(m, name, v) { var e = fx(ctl, m, name); e.property(1).setValue(v); return e; }
cc("ADBE Color Control", "Gold TOP (highlight)", [1.0, 0.92, 0.72]);
cc("ADBE Color Control", "Gold BOTTOM (bronze)", [0.55, 0.36, 0.17]);
cc("ADBE Color Control", "Small lines colour", [0.86, 0.74, 0.52]);
cc("ADBE Slider Control", "Glow amount", 0.45);
cc("ADBE Slider Control", "Bevel depth", 4);
cc("ADBE Slider Control", "Shine sweep width", 90);
cc("ADBE Checkbox Control", "Show smoke backdrop", 1);
var C = 'thisComp.layer("TITLE CONTROLS").effect';

// ---- text
function text(txt, font, size, track) {
    var l = c.layers.addText(txt); var p = l.property("ADBE Text Properties").property("ADBE Text Document"); var d = p.value;
    d.resetCharStyle(); d.resetParagraphStyle(); d.font = font; d.fontSize = size; d.tracking = track;
    d.applyFill = true; d.fillColor = [1, 1, 1]; d.applyStroke = false; d.justification = ParagraphJustification.CENTER_JUSTIFY; p.setValue(d);
    log("font " + font + " -> " + p.value.font); return l;
}
function centre(l, y) {
    var r = l.sourceRectAtTime(0, false); tr(l, "ADBE Anchor Point").setValue([r.left + r.width / 2, r.top + r.height / 2]);
    tr(l, "ADBE Position").setValue([W / 2, y]); return r;
}
// anchor-relative position expressions keep lines spaced correctly when you edit text or size
function style(l, top, bot, big) {
    var r = fx(l, "ADBE Ramp", "Gold gradient");
    r.property("ADBE Ramp-0001").expression = "var s=sourceRectAtTime(time,false);toComp([s.left+s.width/2,s.top])";
    r.property("ADBE Ramp-0003").expression = "var s=sourceRectAtTime(time,false);toComp([s.left+s.width/2,s.top+s.height])";
    r.property("ADBE Ramp-0002").expression = top; r.property("ADBE Ramp-0004").expression = bot;
    var m = fx(l, "ADBE Set Matte3", "Keep text shape"); m.property("ADBE Set Matte3-0001").setValue(l.index);
    if (big) {
        var bv = fx(l, "ADBE Bevel Alpha", "Metal bevel"); bv.property("ADBE Bevel Alpha-0001").expression = C + '("Bevel depth")("Slider")';
        bv.property("ADBE Bevel Alpha-0002").setValue(-50); bv.property("ADBE Bevel Alpha-0004").setValue(0.6);
        var sw = fx(l, "CC Light Sweep", "Shine sweep");
        sw.property("CC Light Sweep-0002").setValue(-22); sw.property("CC Light Sweep-0004").expression = C + '("Shine sweep width")("Slider")';
        sw.property("CC Light Sweep-0005").setValue(45);
        keys(sw.property("CC Light Sweep-0001"), [[1.6, [300, CY]], [2.8, [1650, CY]]], 50);
    }
    var ds = fx(l, "ADBE Drop Shadow", "Shadow"); ds.property("ADBE Drop Shadow-0002").setValue(170); ds.property("ADBE Drop Shadow-0004").setValue(8); ds.property("ADBE Drop Shadow-0005").setValue(22);
    var g = fx(l, "ADBE Glo2", "Glow"); g.property("ADBE Glo2-0002").setValue(big ? 200 : 180); g.property("ADBE Glo2-0003").setValue(big ? 22 : 10);
    g.property("ADBE Glo2-0004").expression = C + '("Glow amount")("Slider")' + (big ? "" : "*0.6");
}
var tE = text("EXPENSIVE", "Theblock-Regular", 330, 15); tE.name = "EXPENSIVE  (TheBlock)"; var rE = centre(tE, CY);
var tM = text("THE MOST", "OpenSauceSans-SemiBold", 34, 700); tM.name = "THE MOST  (Open Sauce)"; centre(tM, CY);
var tF = text("FESTIVAL IN INDIA", "OpenSauceSans-SemiBold", 34, 700); tF.name = "FESTIVAL IN INDIA  (Open Sauce)"; centre(tF, CY);
style(tE, C + '("Gold TOP (highlight)")("Color")', C + '("Gold BOTTOM (bronze)")("Color")', true);
style(tM, C + '("Small lines colour")("Color")', C + '("Gold BOTTOM (bronze)")("Color")', false);
style(tF, C + '("Small lines colour")("Color")', C + '("Gold BOTTOM (bronze)")("Color")', false);
// small lines sit above / below EXPENSIVE automatically (follow its size + position)
var big = 'var b=thisComp.layer("' + tE.name + '");var r=b.sourceRectAtTime(time,false);var sc=b.transform.scale[1]/100;';
var upBase = 'var gap=60;';
tr(tM, "ADBE Position").expression = big + upBase + '[b.transform.position[0], b.transform.position[1]-r.height*sc/2-gap]';
tr(tF, "ADBE Position").expression = big + upBase + '[b.transform.position[0], b.transform.position[1]+r.height*sc/2+gap]';

// ---- animation (all keyframes editable)
var bl = fx(tE, "ADBE Gaussian Blur 2", "Reveal blur"); bl.moveTo(1); bl = tE.property("ADBE Effect Parade").property(1);
keys(bl.property("ADBE Gaussian Blur 2-0001"), [[0, 60], [0.9, 0]], 75);
keys(tr(tE, "ADBE Opacity"), [[0, 0], [0.45, 100], [DUR - 0.6, 100], [DUR, 0]], 50);
keys(tr(tE, "ADBE Position"), [[0, [W / 2, CY + 70]], [1.1, [W / 2, CY]]], 85);
keys(tr(tE, "ADBE Scale"), [[0, [108, 108]], [1.3, [100, 100]], [DUR, [97, 97]]], 70);
keys(tr(tM, "ADBE Opacity"), [[0.7, 0], [1.2, 100], [DUR - 0.6, 100], [DUR, 0]], 50);
keys(tr(tF, "ADBE Opacity"), [[0.85, 0], [1.35, 100], [DUR - 0.6, 100], [DUR, 0]], 50);
function trackOpen(l, t0) {
    var an = l.property("ADBE Text Properties").property("ADBE Text Animators"); an.addProperty("ADBE Text Animator");
    an = l.property("ADBE Text Properties").property("ADBE Text Animators"); var a = an.property(an.numProperties); a.name = "Tracking open";
    a.property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount");
    an = l.property("ADBE Text Properties").property("ADBE Text Animators"); a = an.property(an.numProperties);
    keys(a.property("ADBE Text Animator Properties").property("ADBE Text Tracking Amount"), [[t0, -300], [t0 + 0.9, 0]], 80);
}
trackOpen(tM, 0.7); trackOpen(tF, 0.85);

// ---- backdrop (switch off for transparent / overlay use)
var bd = c.layers.addSolid([0.02, 0.022, 0.024], "BACKDROP  (turn off for transparent)", W, H, 1, DUR); bd.source.parentFolder = fSol; bd.moveToEnd();
var sm = c.layers.addSolid([0, 0, 0], "SMOKE  (faint)", W, H, 1, DUR); sm.source.parentFolder = fSol; sm.blendingMode = BlendingMode.SCREEN;
var fn = fx(sm, "ADBE Fractal Noise"); fn.property("ADBE Fractal Noise-0004").setValue(140); fn.property("ADBE Fractal Noise-0005").setValue(-55);
fn.property("ADBE Fractal Noise-0010").setValue(500); fn.property("ADBE Fractal Noise-0023").expression = "time*40";
tr(sm, "ADBE Opacity").expression = C + '("Show smoke backdrop")("Checkbox")*18'; sm.moveBefore(bd);
ctl.moveToBeginning();

proj.save(new File(OUTD + "TITLE_Editable.aep")); log("saved");
var rq = proj.renderQueue.items.add(c); var om = rq.outputModule(1);
try { om.applyTemplate("High Quality"); } catch (e1) { log("tmpl " + e1); }
om.file = new File("D:/aetmp/fsintro/out/title_test");
proj.renderQueue.render(); log("render done");
proj.save();
app.endSuppressDialogs(false);
} catch (e) { log("ERR " + e.toString() + " line " + e.line); }
LOG.close(); var f = new File("D:/aetmp/fsintro/TITLE_DONE.txt"); f.open("w"); f.write("ok"); f.close();
})();
