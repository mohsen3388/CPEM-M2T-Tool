from pathlib import Path
from csc_mde.xmi_parser import parse_xmi
from csc_mde.validator import validate
from csc_mde.pipeline import generate_project

ROOT = Path(__file__).resolve().parents[1]

def test_sample_parses_and_generates(tmp_path):
    model = parse_xmi(ROOT / "samples" / "CPEM_Diamond_Traceable_EA.xmi")
    assert model.by_stereotype("SmartContract")
    assert len(model.by_stereotype("ContractFunction")) >= 8
    vr = validate(model)
    assert vr.ok, vr.errors
    res = generate_project(model, tmp_path / "out")
    assert res["solidity"].exists()
    assert (tmp_path / "out" / "reports" / "traceability-report.csv").exists()
    assert (tmp_path / "out" / "package.json").exists()
