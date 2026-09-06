# CPEM-to-Solidity M2T Tool

This repository contains the supporting Model-to-Text (M2T) tool developed for
transforming Ethereum-oriented CPEM execution models into Solidity smart-contract
artifacts.

The tool directly integrates with Enterprise Architect, reads CPEM model elements,
validates the execution model, performs the CPEM-to-Solidity transformation, and
generates a Hardhat-compatible project for compilation and testing.

## Transformation Pipeline

CPDM
→ M2M Transformation
→ CPEM
→ CPEM-to-Solidity M2T Tool
→ Solidity / OpenZeppelin
→ Hardhat Compilation and Testing
→ Ethereum Execution

## Main Features

- Direct integration with Enterprise Architect
- Import of CPEM models
- CPEM model validation
- Model-to-Text transformation
- Solidity smart-contract generation
- OpenZeppelin-compatible artifact generation
- Hardhat project generation
- CPDM → CPEM → Solidity traceability reporting
- Generation metrics for experimental validation


## Related Research Artifacts

This repository focuses on the CPEM-to-Solidity transformation and the
implementation-level validation of the proposed approach.

The broader modeling and model-driven engineering artifacts are available in the
companion **CollabChain Platform** repository:

https://github.com/mohsen3388/collabchain-platform

The companion repository contains the broader modeling infrastructure and research
artifacts developed as part of the underlying research, including modeling,
transformation, code-generation, and diamond supply-chain case-study resources.

Together, the two repositories support inspection of the complete model-driven chain:

CPDM → M2M → CPEM → M2T → Solidity → Hardhat / Ethereum