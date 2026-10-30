// Builds job_template.jsx at 1080 into %TEMP%/fs_vox_selftest/ to prove the kit compiles in this After Effects.
var T0 = Folder.temp.fsName.split("\\").join("/") + "/fs_vox_selftest/"; new Folder(T0).create();
var VOX_JOB_OVERRIDE = { root: T0, logo: "", aep: T0 + "FS_VOX_SELFTEST.aep", res: 1 };
#include "../kit/job_template.jsx"
