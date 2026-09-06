# CPEM → Solidity M2T Tool v1.1

v1.1 fixes the issues found during live testing with Enterprise Architect:

- resolves `traceFrom` links whose CPDM source is outside the selected CPEM package;
- when explicit trace connectors are absent, conservatively derives trace links from the repository using M2M-compatible stereotype/name matching and labels them **inferred** in the UI/reports;
- adds a **Primary SmartContract** selector instead of silently using the first of several contracts;
- limits generated Solidity functions to functions associated with the selected primary contract and removes duplicate Solidity signatures;
- removes activity number prefixes from generated Solidity identifiers (`1. Select Diamond` → `selectDiamond()`);
- fixes Windows execution of `npm.cmd` / `npx.cmd` (the cause of WinError 2); and
- displays Node.js/npm/npx availability in the UI.

## Run

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open Enterprise Architect, select the CPEM package, then click **Connect to Enterprise Architect**.
Review the automatically preselected Primary SmartContract and change it if necessary.
Then run **Validate → Generate Solidity + Hardhat → npm install → Compile → Test**.

## Traceability interpretation

`explicit` means an actual `traceFrom` connector exists in the EA repository.
`inferred-by-M2M-rule/name` means v1.1 derived the correspondence conservatively from the source repository using the transformation-compatible source stereotype and matching identifier/name. The generated report preserves this distinction; inferred links are not presented as explicit EA connectors.
