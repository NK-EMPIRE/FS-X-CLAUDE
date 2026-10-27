// Graded test: drop the 6 blast test frames into the v5 edit and render them through 02_GRADED / 03_FINAL.
(function () {
var LOG = new File("D:/aetmp/fsintro/out/gradetest.txt"); LOG.open("w");
try {
    app.beginSuppressDialogs();
    if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    var p = app.open(new File("D:/FS DOCUMENTARY INTRO/downloads/3d_motion_intros/renders/AE_PROJECT/DhanterasCoin_v5.aep"));
    var io = new ImportOptions(new File("D:/FS DOCUMENTARY INTRO/downloads/3d_motion_intros/work/coin3/tail/S8_tail2/test_00.png")); io.sequence = true;
    var seq = p.importFile(io); seq.mainSource.conformFrameRate = 24;
    var edit = null, fin = null;
    for (var i = 1; i <= p.numItems; i++) { var it = p.item(i); if (it instanceof CompItem) { if (it.name == "01_EDIT") edit = it; if (it.name.indexOf("03_FINAL") == 0) fin = it; } }
    var T = 29.5;
    var l = edit.layers.add(seq); l.startTime = T; l.inPoint = T; l.outPoint = T + 6 / 24;
    for (var k = 1; k <= edit.numLayers; k++) { var n = edit.layer(k).name; if (n.indexOf("TITLE") == 0 || n.indexOf("FLASH") == 0 || n.indexOf("FADE") == 0) edit.layer(k).enabled = false; }
    l.moveToBeginning(); l.property("ADBE Transform Group").property("ADBE Scale").setValue([200, 200]);
    for (var k2 = 2; k2 <= edit.numLayers; k2++) { if (edit.layer(k2).name.indexOf("SHOT") == 0) edit.layer(k2).enabled = false; }

    for (var k3 = 1; k3 <= fin.numLayers; k3++) { var nm = fin.layer(k3).name; if (nm == "CA  red channel") fin.layer(k3).property("ADBE Transform Group").property("ADBE Scale").setValue([100.05, 100.05]); if (nm == "CA  blue channel") fin.layer(k3).property("ADBE Transform Group").property("ADBE Scale").setValue([99.95, 99.95]); }
    var rq = p.renderQueue.items.add(fin); rq.timeSpanStart = T; rq.timeSpanDuration = 6 / 24;
    var om = rq.outputModule(1);

    om.file = new File("D:/aetmp/fsintro/out/gradetest/gt");
    new Folder("D:/aetmp/fsintro/out/gradetest").create();
    p.renderQueue.render(); LOG.writeln("done");
    p.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.endSuppressDialogs(false);
} catch (e) { LOG.writeln("ERR " + e.toString() + " line " + e.line); }
LOG.close();
})();
