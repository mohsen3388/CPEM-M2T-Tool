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
