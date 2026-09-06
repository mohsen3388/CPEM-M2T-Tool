from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Optional
from .model import CPEMModel, ModelElement
from .traceability import write_traceability


def _strip_ordinal(name: str) -> str:
    return re.sub(r"^\s*\d+\s*[.):-]?\s*", "", name or "")


def solidity_ident(name: str, pascal: bool = False) -> str:
    name = _strip_ordinal(name)
    parts = re.findall(r"[A-Za-z0-9]+", name)
    if not parts:
        return "GeneratedElement"
    if pascal:
        s = "".join(p[:1].upper()+p[1:] for p in parts)
    else:
        s = parts[0][:1].lower()+parts[0][1:] + "".join(p[:1].upper()+p[1:] for p in parts[1:])
    if s[0].isdigit():
        s = "x" + s
    return s


def _ordered_functions(model: CPEMModel, functions: List[ModelElement]) -> List[ModelElement]:
    ids = {f.id for f in functions}
    next_map = {}; prev = set()
    for c in model.connectors:
        if c.name.lower() in {"next", "nextfunction", "flowsto"} and c.source_id in ids and c.target_id in ids:
            next_map[c.source_id] = c.target_id; prev.add(c.target_id)
    starts = [f for f in functions if f.id not in prev]
    ordered, seen = [], set()
    cur = starts[0] if starts else None
    while cur and cur.id not in seen:
        ordered.append(cur); seen.add(cur.id)
        nxt = next_map.get(cur.id); cur = model.elements.get(nxt) if nxt else None
    # Natural ordinal fallback for remaining functions.
    def k(f):
        m = re.match(r"\s*(\d+)\s*[.]", f.name or "")
        return (0, int(m.group(1))) if m else (1, f.name.lower())
    ordered.extend(sorted([f for f in functions if f.id not in seen], key=k))
    return ordered


def _functions_for_contract(model: CPEMModel, sc: ModelElement) -> List[ModelElement]:
    all_functions = {f.id: f for f in model.by_stereotype("ContractFunction")}
    related = []
    relation_names = {"containsfunction", "functions", "contains", "comprises"}
    for c in model.connectors:
        if c.name.lower() not in relation_names:
            continue
        other = None
        if c.source_id == sc.id and c.target_id in all_functions: other = c.target_id
        elif c.target_id == sc.id and c.source_id in all_functions: other = c.source_id
        if other and other not in related: related.append(other)
    funcs = [all_functions[i] for i in related] if related else list(all_functions.values())
    funcs = _ordered_functions(model, funcs)
    # De-duplicate Solidity signatures; prefer numbered process functions over helper duplicates.
    chosen: Dict[str, ModelElement] = {}
    for f in funcs:
        sig = solidity_ident(f.name).lower()
        if sig not in chosen:
            chosen[sig] = f
        else:
            old = chosen[sig]
            if re.match(r"\s*\d+\s*[.]", f.name or "") and not re.match(r"\s*\d+\s*[.]", old.name or ""):
                chosen[sig] = f
    return [f for f in funcs if chosen.get(solidity_ident(f.name).lower()) is f]


def generate_solidity(model: CPEMModel, out_dir: str | Path, primary_contract_id: Optional[str] = None):
    out_dir = Path(out_dir)
    contracts_dir = out_dir / "contracts"; reports_dir = out_dir / "reports"
    contracts_dir.mkdir(parents=True, exist_ok=True); reports_dir.mkdir(parents=True, exist_ok=True)

    contracts = model.by_stereotype("SmartContract")
    if not contracts: raise ValueError("No SmartContract in model")
    if primary_contract_id:
        sc = next((x for x in contracts if x.id == primary_contract_id), None)
        if sc is None: raise ValueError("Selected primary SmartContract was not found")
    elif len(contracts) == 1:
        sc = contracts[0]
    else:
        raise ValueError("Multiple SmartContracts exist. Select the Primary SmartContract in the UI before generation.")

    cname = solidity_ident(sc.name, pascal=True)
    if not cname.lower().endswith("contract"): cname += "Contract"

    functions = _functions_for_contract(model, sc)
    assets = model.by_stereotype("TokenizedAsset")
    actors = model.by_stereotype("SupplyChainActor")
    events = model.by_stereotype("BlockchainEvent")
    decisions = model.by_stereotype("Decision", "ContractState")

    role_names = []
    for a in actors:
        role = (a.value("role") or solidity_ident(a.name, pascal=False)).upper().replace(" ", "_").replace("-", "_")
        role = re.sub(r"[^A-Z0-9_]", "_", role)
        if role and role not in role_names: role_names.append(role)

    use_erc721 = bool(assets)
    imports = ['import "@openzeppelin/contracts/access/AccessControl.sol";']; bases = ["AccessControl"]; ctor_base = ""
    if use_erc721:
        imports.insert(0, 'import "@openzeppelin/contracts/token/ERC721/ERC721.sol";'); bases.insert(0, "ERC721")
        token_name = assets[0].name.replace('"',''); token_symbol = "DIAMOND" if "diamond" in token_name.lower() else "ASSET"
        ctor_base = f' ERC721("{token_name}", "{token_symbol}")'

    states = ["Created"] + [solidity_ident(f.name, pascal=True) for f in functions]
    if decisions: states.insert(-1 if len(states)>1 else len(states), "Rejected")
    states = list(dict.fromkeys(states))

    artifact_map: Dict[str, str] = {sc.id: f"contract {cname}"}
    lines = ["// SPDX-License-Identifier: MIT", "pragma solidity ^0.8.24;", "", *imports, "",
             f"contract {cname} is {', '.join(bases)} {{",
             "    // Generated by CPEM M2T Tool v1.1. Cross-level traceability is retained in comments and reports."]
    for role in role_names: lines.append(f'    bytes32 public constant {role}_ROLE = keccak256("{role}_ROLE");')
    lines += ["", f"    enum ProcessState {{ {', '.join(states)} }}", "    ProcessState public state = ProcessState.Created;", "    uint256 private _nextTokenId;", ""]

    # Use only business/process events in contract emission; monitoring events are still preserved in trace reports.
    unique_events = []
    seen_event_names = set()
    for ev in events:
        ename = solidity_ident(ev.name, pascal=True)
        if ename.lower() in seen_event_names: continue
        seen_event_names.add(ename.lower()); unique_events.append(ev)
        artifact_map[ev.id] = f"event {ename}"
        lines.append(f"    event {ename}(address indexed actor, uint256 timestamp);")
    lines.append("    event TraceEvent(string cpdmSource, string cpemElement, string action, address indexed actor, uint256 timestamp);")
    lines += ["", f"    constructor(){ctor_base} {{", "        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);"]
    for role in role_names: lines.append(f"        _grantRole({role}_ROLE, msg.sender); // bootstrap role assignment for test deployment")
    lines += ["    }", "", "    modifier inState(ProcessState expected) {", '        require(state == expected, "Invalid process state");', "        _;", "    }", ""]

    prev_state = "Created"
    for idx, fn in enumerate(functions):
        fname = solidity_ident(fn.name); next_state = solidity_ident(fn.name, pascal=True)
        src = model.traced_source(fn.id); srcid = (src.value("id") if src else "") or (src.id if src else "UNTRACED"); source_name = src.name if src else "UNTRACED"
        artifact_map[fn.id] = f"function {fname}()"
        payable = (fn.value("payable", "false").lower() == "true") or "payment" in fname.lower()
        extra_param = "bool approved" if "qualitycontrol" in fname.lower() and decisions else ""
        payable_kw = " payable" if payable else ""
        lines += [f"    /// @custom:cpdm-trace {srcid} | {source_name}", f"    /// @custom:cpem-id {fn.id}",
                  f"    function {fname}({extra_param}) external{payable_kw} inState(ProcessState.{prev_state}) {{"]
        if use_erc721 and idx == 0: lines += ["        uint256 tokenId = ++_nextTokenId;", "        _safeMint(msg.sender, tokenId);"]
        if extra_param:
            lines += ["        if (!approved) {", "            state = ProcessState.Rejected;",
                      f'            emit TraceEvent("{srcid}", "{fn.id}", "{fname}:rejected", msg.sender, block.timestamp);', "            return;", "        }"]
        lines.append(f"        state = ProcessState.{next_state};")
        for ev in unique_events:
            if "delivery" in fname.lower() and "delivery" in ev.name.lower():
                lines.append(f"        emit {solidity_ident(ev.name, pascal=True)}(msg.sender, block.timestamp);")
        lines.append(f'        emit TraceEvent("{srcid}", "{fn.id}", "{fname}", msg.sender, block.timestamp);')
        lines += ["    }", ""]; prev_state = next_state

    if use_erc721:
        lines += ["    function supportsInterface(bytes4 interfaceId) public view override(ERC721, AccessControl) returns (bool) {",
                  "        return super.supportsInterface(interfaceId);", "    }", ""]
    lines.append("}")

    sol_path = contracts_dir / f"{cname}.sol"; sol_path.write_text("\n".join(lines), encoding="utf-8")
    trace_files = write_traceability(model, reports_dir, str(sol_path.name), artifact_map)
    return sol_path, trace_files, artifact_map
