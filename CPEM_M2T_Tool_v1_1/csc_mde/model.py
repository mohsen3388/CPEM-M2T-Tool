from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class ModelAttribute:
    name: str
    type: str = "String"
    value: str = ""

@dataclass
class ModelElement:
    id: str
    name: str
    stereotype: str = ""
    guid: str = ""
    attributes: Dict[str, ModelAttribute] = field(default_factory=dict)
    tagged_values: Dict[str, str] = field(default_factory=dict)

    def value(self, key: str, default: str = "") -> str:
        if key in self.tagged_values:
            return self.tagged_values[key]
        if key in self.attributes:
            return self.attributes[key].value
        return default

@dataclass
class ModelConnector:
    id: str
    name: str
    source_id: str
    target_id: str
    kind: str = "Dependency"
    provenance: str = "explicit"

@dataclass
class CPEMModel:
    name: str = "CPEM Model"
    elements: Dict[str, ModelElement] = field(default_factory=dict)
    connectors: List[ModelConnector] = field(default_factory=list)
    source: str = ""

    def by_stereotype(self, *stereotypes: str) -> List[ModelElement]:
        wanted = {s.lower() for s in stereotypes}
        return [e for e in self.elements.values() if e.stereotype.lower() in wanted]

    def outgoing(self, element_id: str, name: Optional[str] = None) -> List[ModelConnector]:
        conns = [c for c in self.connectors if c.source_id == element_id]
        if name is not None:
            conns = [c for c in conns if c.name.lower() == name.lower()]
        return conns

    def incoming(self, element_id: str, name: Optional[str] = None) -> List[ModelConnector]:
        conns = [c for c in self.connectors if c.target_id == element_id]
        if name is not None:
            conns = [c for c in conns if c.name.lower() == name.lower()]
        return conns

    def traced_source_with_method(self, element_id: str) -> Tuple[Optional[ModelElement], str]:
        for c in self.outgoing(element_id, "traceFrom"):
            src = self.elements.get(c.target_id)
            if src:
                return src, c.provenance or "explicit"
        return None, ""

    def traced_source(self, element_id: str) -> Optional[ModelElement]:
        return self.traced_source_with_method(element_id)[0]
