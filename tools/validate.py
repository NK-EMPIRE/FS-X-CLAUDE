"""Pre-push check: every catalogue entry has a plugin folder, versions match, each plugin has a README and at least one skill or command.
   python tools/validate.py   (then: claude plugin validate . && claude plugin validate plugins/<each>)"""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); bad = 0
mk = json.load(open(os.path.join(R, ".claude-plugin", "marketplace.json"), encoding="utf8"))
names = set()
for p in mk["plugins"]:
    d = os.path.join(R, p["source"]); names.add(p["name"])
    pj = os.path.join(d, ".claude-plugin", "plugin.json")
    if not os.path.exists(pj): print("MISSING", pj); bad += 1; continue
    j = json.load(open(pj, encoding="utf8"))
    if j["name"] != p["name"]: print("NAME MISMATCH", p["name"], j["name"]); bad += 1
    if j.get("version") != p.get("version"): print("VERSION MISMATCH", p["name"], j.get("version"), "vs catalogue", p.get("version")); bad += 1
    if not os.path.exists(os.path.join(d, "README.md")): print("NO README", p["name"]); bad += 1
    if not (os.path.isdir(os.path.join(d, "skills")) or os.path.isdir(os.path.join(d, "commands"))): print("EMPTY", p["name"]); bad += 1
for d in os.listdir(os.path.join(R, "plugins")):
    if d not in names: print("NOT IN CATALOGUE", d); bad += 1
print("OK" if not bad else f"{bad} problem(s)"); sys.exit(1 if bad else 0)
