from pathlib import Path
from csc_mde.model import CPEMModel, ModelElement, ModelConnector
from csc_mde.generator import solidity_ident, generate_solidity


def test_solidity_ident_strips_activity_ordinals():
    assert solidity_ident("1. Select Diamond") == "selectDiamond"
    assert solidity_ident("8. Complete Order") == "completeOrder"


def test_primary_contract_scopes_and_dedupes_functions(tmp_path: Path):
    m = CPEMModel("x")
    sc1 = ModelElement("sc1", "P0 Purchasing Diamond", "SmartContract")
    sc2 = ModelElement("sc2", "Order Contract", "SmartContract")
    f1 = ModelElement("f1", "1. Select Diamond", "ContractFunction")
    f2 = ModelElement("f2", "6. Confirm Delivery", "ContractFunction")
    dup = ModelElement("f3", "confirmDelivery", "ContractFunction")
    for e in [sc1,sc2,f1,f2,dup]: m.elements[e.id] = e
    m.connectors += [
        ModelConnector("c1","containsFunction","sc1","f1"),
        ModelConnector("c2","containsFunction","sc1","f2"),
        ModelConnector("c3","functions","sc2","f3"),
    ]
    p, _, _ = generate_solidity(m, tmp_path, "sc1")
    text = p.read_text()
    assert "function selectDiamond()" in text
    assert "function confirmDelivery()" in text
    assert text.count("function confirmDelivery(") == 1
