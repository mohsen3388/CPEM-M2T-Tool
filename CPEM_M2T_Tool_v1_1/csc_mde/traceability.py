from __future__ import annotations
import csv, json
from pathlib import Path
from typing import List, Dict
from .model import CPEMModel

TRACE_TYPES = {
    "smartcontract", "contractfunction", "tokenizedasset", "decision", "contractstate", "statetransition", "blockchainevent",
    "executionrisk", "executiontraceabilityrule", "executionmetric", "executionindicator", "executionokr",
    "supplychainactor", "ethereumidentity", "actorrolebinding", "accesscontrolpolicy"
}


def build_trace_rows(model: CPEMModel, solidity_file: str, artifact_map: Dict[str, str]) -> List[dict]:
    rows = []
    for e in model.elements.values():
        if e.stereotype.lower() not in TRACE_TYPES:
            continue
        src, method = model.traced_source_with_method(e.id)
        rows.append({
            "cpdm_source_id": src.id if src else "",
            "cpdm_source_name": src.name if src else "",
            "cpdm_source_stereotype": src.stereotype if src else "",
            "cpem_id": e.id,
            "cpem_name": e.name,
            "cpem_stereotype": e.stereotype,
            "trace_method": method if src else "",
            "m2t_artifact": artifact_map.get(e.id, ""),
            "solidity_file": solidity_file,
            "trace_status": "traced" if src else "not-traced",
        })
    return rows


def write_traceability(model: CPEMModel, out_dir: str | Path, solidity_file: str, artifact_map: Dict[str, str]):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = build_trace_rows(model, solidity_file, artifact_map)
    csv_path = out / "traceability-report.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["cpem_id"])
        w.writeheader(); w.writerows(rows)
    json_path = out / "traceability-report.json"
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    traced = sum(1 for r in rows if r["trace_status"] == "traced")
    explicit = sum(1 for r in rows if r.get("trace_method") == "explicit")
    inferred = sum(1 for r in rows if r.get("trace_method", "").startswith("inferred"))
    metrics = {
        "evaluated_trace_elements": len(rows),
        "traced_elements": traced,
        "explicit_trace_links": explicit,
        "inferred_trace_links": inferred,
        "traceability_coverage_percent": round(traced / len(rows) * 100, 2) if rows else 0,
        "cpem_to_solidity_artifacts": sum(1 for r in rows if r["m2t_artifact"]),
    }
    metrics_path = out / "generation-metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return csv_path, json_path, metrics_path
