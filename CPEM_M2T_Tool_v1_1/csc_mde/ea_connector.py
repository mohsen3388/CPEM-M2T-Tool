from __future__ import annotations
import re
from typing import Dict, List, Tuple
from .model import CPEMModel, ModelElement, ModelConnector, ModelAttribute

class EAConnectionError(RuntimeError):
    pass


def _iter_ea_collection(collection):
    try:
        count = collection.Count
    except Exception:
        count = 0
    for i in range(count):
        yield collection.GetAt(i)


def _stereotype(e) -> str:
    st = str(getattr(e, "StereotypeEx", "") or getattr(e, "Stereotype", ""))
    return st.split(",")[0].split("::")[-1].strip()


def _to_element(e) -> ModelElement:
    eid = str(getattr(e, "ElementID", ""))
    guid = str(getattr(e, "ElementGUID", ""))
    key = guid or eid
    el = ModelElement(id=key, guid=guid, name=str(getattr(e, "Name", "")), stereotype=_stereotype(e))
    for a in _iter_ea_collection(getattr(e, "Attributes", None)):
        val = str(getattr(a, "Default", "") or "").strip('"')
        el.attributes[str(a.Name)] = ModelAttribute(str(a.Name), str(getattr(a, "Type", "String") or "String"), val)
    for tv in _iter_ea_collection(getattr(e, "TaggedValues", None)):
        el.tagged_values[str(tv.Name)] = str(getattr(tv, "Value", "") or "")
    return el


def _norm(s: str) -> str:
    s = re.sub(r"^\s*\d+\s*[.):-]?\s*", "", s or "")
    s = s.lower().replace("tokenized_", "").replace("tokenized ", "")
    for prefix in ["processcontract_", "ordercontract_", "execution_", "metric_", "indicator_", "okr_", "riskpolicy_", "approved_", "rejected_", "transition_"]:
        s = s.replace(prefix, "")
    return re.sub(r"[^a-z0-9]+", "", s)


def _collect_repository_elements(repo) -> List[object]:
    out = []
    seen = set()
    def walk_package(p):
        for e in _iter_ea_collection(p.Elements):
            key = str(getattr(e, "ElementGUID", "") or getattr(e, "ElementID", ""))
            if key and key not in seen:
                seen.add(key); out.append(e)
        for ch in _iter_ea_collection(p.Packages):
            walk_package(ch)
    for m in _iter_ea_collection(repo.Models):
        walk_package(m)
    return out


def _is_cpdm_candidate(st: str) -> bool:
    s = st.lower()
    return s in {
        "activity", "product", "order", "supplychainprocess", "decision", "supplychainactor",
        "metric", "indicator", "okr", "traceabilityrule", "riskassessment", "contract", "payment",
        "event", "insurance", "transportconditions", "criticalactivity", "integratedrepository"
    } or s.startswith("cpdm")


def _target_source_types(target_st: str) -> set[str]:
    return {
        "contractfunction": {"activity", "payment"},
        "tokenizedasset": {"product"},
        "smartcontract": {"supplychainprocess", "contract", "order"},
        "statetransition": {"activity", "decision"},
        "contractstate": {"decision"},
        "blockchainevent": {"event", "metric", "indicator", "okr"},
        "supplychainactor": {"supplychainactor"},
        "ethereumidentity": {"supplychainactor"},
        "actorrolebinding": {"supplychainactor"},
        "accesscontrolpolicy": {"riskassessment", "traceabilityrule"},
        "executionrisk": {"riskassessment"},
        "executiontraceabilityrule": {"traceabilityrule"},
        "executionmetric": {"metric"},
        "executionindicator": {"indicator"},
        "executionokr": {"okr"},
        "costmodel": {"product", "payment"},
    }.get(target_st.lower(), set())


def _best_cpdm_match(target: ModelElement, cpdm: List[ModelElement]) -> ModelElement | None:
    allowed = _target_source_types(target.stereotype)
    if not allowed:
        return None
    tn = _norm(target.name)
    candidates = [x for x in cpdm if x.stereotype.lower() in allowed]
    if not candidates:
        return None
    # exact normalized name is strongest
    exact = [x for x in candidates if _norm(x.name) == tn]
    if len(exact) == 1:
        return exact[0]
    # containment handles ProcessContract_P0... / Tokenized_RoughDiamond / Approved_D1...
    scored: List[Tuple[int, ModelElement]] = []
    for x in candidates:
        xn = _norm(x.name)
        score = 0
        if xn and tn:
            if xn in tn or tn in xn:
                score += 50 + min(len(xn), len(tn))
            # IDs/aliases often survive transformation names
            xid = _norm(x.value("id"))
            if xid and xid in tn:
                score += 80
        if score:
            scored.append((score, x))
    if not scored:
        return None
    scored.sort(key=lambda z: z[0], reverse=True)
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    return scored[0][1]


def connect_to_running_ea() -> CPEMModel:
    """Read the currently selected Enterprise Architect package through EA Automation/COM.

    v1.1 also resolves explicit traceFrom connectors outside the selected package and, when
    those connectors are absent, derives trace links conservatively from the repository using
    stereotype-compatible transformation/name matching. Derived links are marked as inferred.
    """
    try:
        import win32com.client  # type: ignore
    except Exception as exc:
        raise EAConnectionError("pywin32 is not installed. Run: python -m pip install pywin32") from exc

    try:
        try:
            app = win32com.client.GetActiveObject("EA.App")
        except Exception:
            app = win32com.client.Dispatch("EA.App")
        repo = app.Repository
        pkg = repo.GetTreeSelectedPackage()
    except Exception as exc:
        raise EAConnectionError(
            "Could not connect to Enterprise Architect. Open EA, open the project, and select the CPEM package."
        ) from exc

    if pkg is None:
        raise EAConnectionError("No package is selected in Enterprise Architect.")

    model = CPEMModel(name=str(pkg.Name), source="Enterprise Architect COM")
    seen_connectors = set()
    external_explicit_sources: Dict[str, ModelElement] = {}

    def add_package(p):
        for e in _iter_ea_collection(p.Elements):
            el = _to_element(e)
            if not el.id:
                continue
            model.elements[el.id] = el

            for c in _iter_ea_collection(e.Connectors):
                cid = str(getattr(c, "ConnectorGUID", "") or getattr(c, "ConnectorID", ""))
                if cid in seen_connectors:
                    continue
                seen_connectors.add(cid)
                client_id = int(getattr(c, "ClientID", 0) or 0)
                supplier_id = int(getattr(c, "SupplierID", 0) or 0)
                try:
                    client = repo.GetElementByID(client_id)
                    supplier = repo.GetElementByID(supplier_id)
                    src = str(client.ElementGUID or client.ElementID)
                    dst = str(supplier.ElementGUID or supplier.ElementID)
                except Exception:
                    continue
                cname = str(getattr(c, "Name", "") or getattr(c, "Stereotype", "") or "connector")
                model.connectors.append(ModelConnector(
                    id=cid or f"ea_{len(model.connectors)+1}",
                    name=cname,
                    source_id=src,
                    target_id=dst,
                    kind=str(getattr(c, "Type", "Connector")),
                    provenance="explicit",
                ))
                # If traceFrom points outside selected CPEM package, materialize the source as a shadow element.
                if cname.lower() == "tracefrom" and dst not in model.elements:
                    try:
                        ext = _to_element(supplier)
                        if ext.id:
                            external_explicit_sources[ext.id] = ext
                    except Exception:
                        pass
        for child in _iter_ea_collection(p.Packages):
            add_package(child)

    add_package(pkg)
    model.elements.update(external_explicit_sources)

    # Repository-wide CPDM lookup for CPEM elements that do not yet have an explicit trace.
    try:
        repo_cpdm = []
        selected_ids = set(model.elements)
        for e in _collect_repository_elements(repo):
            el = _to_element(e)
            if el.id and el.id not in selected_ids and _is_cpdm_candidate(el.stereotype):
                repo_cpdm.append(el)
        for target in list(model.elements.values()):
            if _is_cpdm_candidate(target.stereotype):
                continue
            if model.traced_source(target.id):
                continue
            src = _best_cpdm_match(target, repo_cpdm)
            if src:
                model.elements[src.id] = src
                model.connectors.append(ModelConnector(
                    id=f"derived_trace_{target.id}_{src.id}",
                    name="traceFrom",
                    source_id=target.id,
                    target_id=src.id,
                    kind="DerivedTrace",
                    provenance="inferred-by-M2M-rule/name",
                ))
    except Exception:
        # Direct parsing still works even when global repository traversal is restricted.
        pass

    return model
