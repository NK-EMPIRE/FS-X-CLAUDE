// relink_package.jsx: point every footage item of an .aep at a self-contained package folder and save it there.
// First copy the files (bash):  <PKG>/Footage/Renders/<seq folder>/..., <PKG>/Footage/Brand/<video>, <PKG>/Footage/Title/<png>
// Config next to this script: package_config.json  { "aep": "D:/.../Name_v1.aep", "package_dir": "D:/.../Name_PACKAGE", "name": "Name_v1" }
// Run: AfterFX.exe -r D:/aetmp/<proj>/relink_package.jsx   -> <PKG>/<name>.aep and <PKG>/relink_log.txt ("relinked N missing 0")
(function () {
var HERE = File($.fileName).parent.fsName.replace(/\\/g, "/") + "/";
var cf = new File(HERE + "package_config.json"); cf.open("r"); var C = eval("(" + cf.read() + ")"); cf.close();
var P = C.package_dir.replace(/\/?$/, "/");
var LOGF = new File(P + "relink_log.txt"); LOGF.open("w");
try {
    app.beginSuppressDialogs();
    if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    var p = app.open(new File(C.aep)); var n = 0, miss = 0;
    for (var i = 1; i <= p.numItems; i++) {
        var it = p.item(i);
        if (!(it instanceof FootageItem) || !it.file) continue;
        var nm = File.decode(it.file.name), np = null, low = nm.toLowerCase();
        if (it.mainSource.isStill === false && /_\d{4}\.(png|exr|tif)$/.test(low)) {       // image sequence
            var fps = it.mainSource.conformFrameRate;
            np = P + "Footage/Renders/" + File.decode(it.file.parent.name) + "/" + nm;
            it.replaceWithSequence(new File(np), false); it.mainSource.conformFrameRate = fps;
        } else if (/\.(mp4|mov|avi|mxf)$/.test(low)) { np = P + "Footage/Brand/" + nm; it.replace(new File(np)); }
        else if (/\.(png|jpg|jpeg|psd|tif)$/.test(low)) { np = P + "Footage/Title/" + nm; it.replace(new File(np)); }
        if (np) { n++; if (it.footageMissing) miss++; LOGF.writeln("-> " + it.name + " | " + np + " missing=" + it.footageMissing); }
    }
    p.save(new File(P + C.name + ".aep")); LOGF.writeln("relinked " + n + " missing " + miss);
    p.close(CloseOptions.DO_NOT_SAVE_CHANGES); app.endSuppressDialogs(false);
} catch (e) { LOGF.writeln("ERR " + e.toString() + " line " + e.line); }
LOGF.close();
})();
