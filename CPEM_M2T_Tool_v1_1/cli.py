import argparse
from pathlib import Path
from csc_mde.xmi_parser import parse_xmi
from csc_mde.validator import validate
from csc_mde.pipeline import generate_project

p = argparse.ArgumentParser(description="CPEM M2T Tool v1")
p.add_argument("input", help="CPEM XMI file")
p.add_argument("-o", "--output", default="generated_project")
args = p.parse_args()
model = parse_xmi(args.input)
vr = validate(model)
for x in vr.info: print("[INFO]", x)
for x in vr.warnings: print("[WARN]", x)
for x in vr.errors: print("[ERROR]", x)
if not vr.ok: raise SystemExit(2)
res = generate_project(model, args.output)
print("Generated:", res["solidity"])
print("Project:", Path(args.output).resolve())
