from __future__ import annotations
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict
from .model import CPEMModel, ModelElement, ModelConnector, ModelAttribute


def _local(tag: str) -> str:
    return tag.split('}', 1)[-1].split(':')[-1]


def _attr(node, *names, default=""):
    for n in names:
        if n in node.attrib:
            return node.attrib[n]
    for k, v in node.attrib.items():
        local = k.split('}', 1)[-1].split(':')[-1]
        if local in names:
            return v
    return default


def parse_xmi(path: str | Path) -> CPEMModel:
    path = Path(path)
    root = ET.parse(path).getroot()
    model = CPEMModel(name=path.stem, source=str(path))

    # XMI 1.x style stereotype declarations.
    stereotype_names: Dict[str, str] = {}
    for node in root.iter():
        if _local(node.tag) == "Stereotype":
            sid = _attr(node, "xmi.id", "id")
            name = _attr(node, "name")
            if sid and name:
                stereotype_names[sid] = name

    # First pass: UML classes/components as logical model elements.
    for node in root.iter():
        ln = _local(node.tag)
        if ln not in {"Class", "Component", "Object"}:
            continue
        eid = _attr(node, "xmi.id", "id")
        name = _attr(node, "name")
        if not eid or not name:
            continue
        stereotype = _attr(node, "stereotype")
        if not stereotype:
            for ch in node.iter():
                if _local(ch.tag) == "Stereotype":
                    ref = _attr(ch, "xmi.idref", "idref")
                    if ref and ref in stereotype_names:
                        stereotype = stereotype_names[ref]
                        break
        el = ModelElement(id=eid, guid=_attr(node, "ea_guid", "guid"), name=name, stereotype=stereotype)
        for ch in node.iter():
            if _local(ch.tag) == "Attribute":
                aid = _attr(ch, "xmi.id", "id")
                aname = _attr(ch, "name")
                if not aname:
                    continue
                atype = _attr(ch, "type", default="String")
                val = _attr(ch, "default", "value")
                if not val:
                    for ex in ch.iter():
                        if _local(ex.tag) in {"Expression", "LiteralString", "LiteralBoolean", "LiteralInteger"}:
                            val = _attr(ex, "body", "value")
                            if val:
                                break
                el.attributes[aname] = ModelAttribute(aname, atype or "String", val or "")
        model.elements[eid] = el

    # XMI 2.x stereotype applications (profile:Stereo base_Class="id").
    for node in root.iter():
        ln = _local(node.tag)
        base_id = _attr(node, "base_Class", "base_Element", "base_Component")
        if base_id and base_id in model.elements and ln not in {"Class", "Component", "Object"}:
            if ln not in {"Model", "Package", "Property", "Association", "Dependency", "ownedAttribute"}:
                model.elements[base_id].stereotype = ln
                for k, v in node.attrib.items():
                    key = k.split('}', 1)[-1]
                    if not key.startswith("base_"):
                        model.elements[base_id].tagged_values[key] = v

    # XMI 1.x dependencies.
    for node in root.iter():
        ln = _local(node.tag)
        if ln == "Dependency":
            cid = _attr(node, "xmi.id", "id") or f"dep_{len(model.connectors)+1}"
            src = _attr(node, "client", "source")
            dst = _attr(node, "supplier", "target")
            name = _attr(node, "name") or "dependency"
            if src and dst:
                model.connectors.append(ModelConnector(cid, name, src, dst, "Dependency"))

    # XMI 1.x associations.
    for node in root.iter():
        if _local(node.tag) != "Association":
            continue
        ends = []
        for ch in node.iter():
            if _local(ch.tag) == "AssociationEnd":
                typ = _attr(ch, "type")
                if typ:
                    ends.append(typ)
        if len(ends) >= 2:
            cid = _attr(node, "xmi.id", "id") or f"assoc_{len(model.connectors)+1}"
            model.connectors.append(ModelConnector(cid, _attr(node, "name") or "association", ends[0], ends[1], "Association"))

    # XMI 2.x associations often reference end property types.
    # This is deliberately conservative: we only create if two target class refs are resolvable.
    for node in root.iter():
        if _local(node.tag) != "packagedElement":
            continue
        xtype = _attr(node, "type")
        if not xtype.endswith("Association"):
            continue
        refs = []
        for ch in node.iter():
            if _local(ch.tag) in {"ownedEnd", "type"}:
                ref = _attr(ch, "idref")
                if ref in model.elements:
                    refs.append(ref)
        refs = list(dict.fromkeys(refs))
        if len(refs) >= 2:
            cid = _attr(node, "id") or f"assoc2_{len(model.connectors)+1}"
            tup = (cid, _attr(node, "name") or "association", refs[0], refs[1])
            if not any(c.id == cid for c in model.connectors):
                model.connectors.append(ModelConnector(*tup, kind="Association"))

    # Try to obtain model name.
    for node in root.iter():
        if _local(node.tag) == "Model" and _attr(node, "name"):
            model.name = _attr(node, "name")
            break
    return model
