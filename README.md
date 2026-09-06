# CPEM-to-Solidity Model-to-Text Transformation Tool

This repository provides the implementation and replication artifacts of the
model-to-text (M2T) stage of our model-driven approach for the definition and
Ethereum-based execution of collaborative supply-chain processes.

The tool directly connects to Enterprise Architect, retrieves an
Ethereum-oriented CPEM execution model, validates its modeling constructs,
performs the CPEM-to-Solidity transformation, and generates a Hardhat-compatible
project for compilation, testing, and subsequent deployment.

## End-to-End Model-Driven Pipeline

CPDM
→ M2M Transformation
→ CPEM
→ CPEM-to-Solidity M2T Tool
→ Solidity / OpenZeppelin
→ Hardhat Compilation and Testing
→ Ethereum Execution

A central objective of the implementation is to preserve traceability across
the different abstraction levels:

CPDM business element
→ CPEM execution element
→ generated Solidity artifact


## Research and Replication Artifacts

The repository includes the artifacts required to inspect and reproduce the
execution-level transformation demonstrated in the diamond supply-chain case
study.

### M2T Tool

`CPEM_M2T_Tool_v1_1/`

Contains the source code of the developed supporting tool, including:

- direct Enterprise Architect integration;
- CPEM model extraction;
- execution-model validation;
- CPEM-to-Solidity M2T transformation;
- Solidity smart-contract generation;
- Hardhat project generation;
- cross-level traceability reporting; and
- generation metrics.

### Enterprise Architect Model

`enterprise-architect/`

Contains the Enterprise Architect project used for the CPDM/CPEM modeling and
diamond supply-chain case study.

The model can be inspected using Sparx Systems Enterprise Architect.

### Generated and Validation Artifacts

`output-artifacts/diamond-case/`

Contains the artifacts generated from the CPEM diamond supply-chain execution
model, including:

- generated Solidity smart contracts;
- Hardhat test specifications;
- Hardhat configuration;
- exact npm dependency definitions;
- CPDM–CPEM–Solidity traceability reports; and
- model/code generation metrics.

The `node_modules` directory is intentionally excluded from version control.
All JavaScript dependencies can be restored using:

npm install



## Companion Research Repository

The broader research infrastructure and artifacts underlying the proposed
approach are available in the companion CollabChain Platform repository:

https://github.com/mohsen3388/collabchain-platform

That repository contains the broader modeling, transformation, code-generation,
and collaborative supply-chain research infrastructure.

Together, the two repositories provide artifacts supporting the complete
model-driven chain:

CPDM → M2M → CPEM → M2T → Solidity → Hardhat / Ethereum


## Reproducing the Diamond Case

1. Open the provided Enterprise Architect project.
2. Select the CPEM diamond supply-chain package.
3. Run the CPEM-to-Solidity M2T Tool.
4. Connect the tool to Enterprise Architect.
5. Validate the execution model.
6. Generate the Solidity and Hardhat artifacts.
7. From the generated project directory run:

npm install
npx hardhat compile
npx hardhat test

The generated traceability and generation reports are available under
`output-artifacts/diamond-case/reports/`.
