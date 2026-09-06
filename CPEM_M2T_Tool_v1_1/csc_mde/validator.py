from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .model import CPEMModel

@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    @property
    def ok(self):
        return not self.errors


def validate(model: CPEMModel, primary_contract_id: Optional[str] = None) -> ValidationResult:
    r = ValidationResult()
    contracts = model.by_stereotype("SmartContract")
    functions = model.by_stereotype("ContractFunction")
    assets = model.by_stereotype("TokenizedAsset")
    events = model.by_stereotype("BlockchainEvent")
    actors = model.by_stereotype("SupplyChainActor")

    if not contracts:
        r.errors.append("No CPEM SmartContract element was found.")
    if not functions:
        r.errors.append("No CPEM ContractFunction elements were found.")
    if len(contracts) > 1 and not primary_contract_id:
        r.warnings.append(f"{len(contracts)} SmartContract elements found; select a Primary SmartContract before generation.")
    if primary_contract_id and not any(c.id == primary_contract_id for c in contracts):
        r.errors.append("Selected Primary SmartContract is not present in the current model.")
    if not assets:
        r.warnings.append("No TokenizedAsset found; ERC-721 support will be omitted.")
    if not events:
        r.warnings.append("No BlockchainEvent found; only generic trace events will be generated.")
    if not actors:
        r.warnings.append("No SupplyChainActor found; role constants will be minimal.")

    traceable_types = {
        "contractfunction", "tokenizedasset", "decision", "contractstate", "statetransition", "blockchainevent",
        "executionrisk", "executiontraceabilityrule", "executionmetric", "executionindicator", "executionokr", "smartcontract",
        "supplychainactor", "ethereumidentity", "actorrolebinding", "accesscontrolpolicy"
    }
    candidates = [e for e in model.elements.values() if e.stereotype.lower() in traceable_types]
    traced = [e for e in candidates if model.traced_source(e.id)]
    explicit = 0; inferred = 0
    for e in traced:
        _, method = model.traced_source_with_method(e.id)
        if method == "explicit": explicit += 1
        else: inferred += 1
    coverage = (len(traced) / len(candidates) * 100) if candidates else 0.0
    r.info.append(f"Elements: {len(model.elements)}; connectors: {len(model.connectors)}")
    r.info.append(f"SmartContracts: {len(contracts)}; functions: {len(functions)}; assets: {len(assets)}; events: {len(events)}")
    r.info.append(f"Traceability coverage (evaluated CPEM elements): {len(traced)}/{len(candidates)} = {coverage:.1f}%")
    r.info.append(f"Trace links: explicit={explicit}; inferred-by-M2M-rule/name={inferred}")
    return r
