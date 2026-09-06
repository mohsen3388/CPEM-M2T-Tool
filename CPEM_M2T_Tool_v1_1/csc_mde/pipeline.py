from __future__ import annotations
from pathlib import Path
from .validator import validate
from .generator import generate_solidity
from .hardhat import prepare_hardhat_project


def generate_project(model, out_dir, primary_contract_id=None):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    vr = validate(model, primary_contract_id)
    if vr.errors: raise ValueError("; ".join(vr.errors))
    sol_path, trace_files, artifact_map = generate_solidity(model, out, primary_contract_id)
    contract_name = sol_path.stem
    prepare_hardhat_project(out, contract_name)
    return {"validation": vr, "solidity": sol_path, "trace_files": trace_files, "artifact_map": artifact_map, "project_dir": out}
