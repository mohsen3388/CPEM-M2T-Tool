# CPEM-to-Solidity Model-to-Text Transformation Tool

**Research software and replication artifacts for:** *A Model-Driven Approach to the Definition and Blockchain-Based Execution of Collaborative Supply Chain Processes*  
**Authors:** Mohsen Khoram Dastjerdi, Julián Alberto García-García, and José González Enríquez  
**Manuscript:** submitted to *PeerJ Computer Science* (manuscript CS-2026:10:150472; peer-review/publication status should be checked before citation)  
**Repository:** https://github.com/mohsen3388/CPEM-M2T-Tool  
**Companion research repository:** https://github.com/mohsen3388/collabchain-platform

## 1. Overview and research purpose

This repository documents the **model-to-text (M2T) stage** of a model-driven engineering approach to collaborative supply-chain processes. The approach separates (i) business-oriented models conforming to the **Collaborative Process Definition Metamodel (CPDM)** from (ii) Ethereum-oriented execution models conforming to the **Collaborative Process Execution Metamodel (CPEM)**. The supporting Python tool reads a CPEM execution model, checks modeling constraints, and generates Solidity smart-contract and Hardhat project artifacts. Generation also produces machine-readable reports to support investigation of model-to-code traceability.

The research demonstration concerns a diamond supply-chain process involving organizations in Lesotho, South Africa, and Spain. The case-study artifacts are research examples; **they do not contain a production deployment or empirical records of a live commercial supply chain**.

### Scope and boundaries

```text
CPDM business model --(M2M in Enterprise Architect)--> CPEM execution model
                                                     |
                                CPEM-to-Solidity M2T tool (this repository)
                                                     |
                         generated Solidity + Hardhat files + traceability reports
                                                     |
                                     compilation and automated testing
```

This repository concentrates on **CPEM-to-Solidity generation and its associated replication artifacts**. The CPDM-to-CPEM (M2M) modeling stage is described in the manuscript and represented through Enterprise Architect and companion research materials; the Python M2T application should **not** be interpreted as independently performing the entire CPDM-to-CPEM transformation. Refer to the companion repository for broader research infrastructure. The tool can read models from an active Enterprise Architect session or an exported XMI file.

## 2. Repository contents and dataset information

| Location | Contents / research role |
| --- | --- |
| `README.md` | Project description, setup, execution, reproducibility information, and limitations. |
| `CPEM_M2T_Tool_v1_1/app.py` | Tkinter desktop application: EA connection / XMI import, validation, contract selection, generation, and Hardhat command buttons. |
| `CPEM_M2T_Tool_v1_1/cli.py` | Command-line entry point for parsing and validating CPEM XMI and generating a project. |
| `CPEM_M2T_Tool_v1_1/csc_mde/` | Python modules used by the parser, validator, code-generation pipeline, and integrations. |
| `CPEM_M2T_Tool_v1_1/requirements.txt` | Python package requirements declared by the source tree. |
| `CPEM_M2T_Tool_v1_1/run_windows.bat` | Windows launcher for the desktop application. |
| `CPEM_M2T_Tool_v1_1/samples/CPEM_Diamond_Traceable_EA.xmi` | Supplied CPEM XMI input example for repeatable import and generation experiments. |
| `CPEM_M2T_Tool_v1_1/tests/` | Python source-level tests of the transformation tool. |
| `enterprise-architect/Use Case Diagram of CPDM Final.EAP` | Native Enterprise Architect project; inspect with a compatible Sparx Enterprise Architect installation. |
| `enterprise-architect/enterprise-architect/README.md` | Notes on the EA research model. |
| `output-artifacts/contracts/` | Published example of a generated Solidity contract. |
| `output-artifacts/test/generated.test.js` | Published example Hardhat smoke test. |
| `output-artifacts/hardhat.config.js` | Hardhat configuration for the published example. |
| `output-artifacts/package.json` / `package-lock.json` | JavaScript dependency manifest and lockfile. |
| `output-artifacts/reports/traceability-report.csv` | Tabular traceability output; suitable for review in a spreadsheet or as CSV. |
| `output-artifacts/reports/traceability-report.json` | Machine-readable traceability output. |
| `output-artifacts/reports/generation-metrics.json` | Counts and derived traceability statistics of the published generation example. |

The **curated research inputs and derived outputs** available in this repository are the example XMI model, the native EA modeling project, generated smart-contract/Hardhat artifacts, and the traceability/metrics files. These are *model-based case-study and software-generation artifacts*, not personal data or observations sampled from a live supply-chain organization. Refer to the manuscript for the case-study design, research questions, evaluation procedure, and interpretation.

**PeerJ data submission note:** If the editorial system requires a separate “raw data” deposit, the authors should identify and upload/associate the exact input model(s), case-study inputs, and evaluation records used for the manuscript, with an appropriate description and stable repository reference. A README and GitHub URL alone do not guarantee that the curated dataset requirement is satisfied.

## 3. Software and platform requirements

- **Windows** is recommended for the GUI and direct integration with the Windows-based Enterprise Architect COM interface.
- **Python 3** with `pip`; a specific Python minor version is *not pinned* by the repository and should be recorded when reproducing results.
- **Sparx Systems Enterprise Architect**, with an edition/version that can open the provided `.EAP` project, for the direct-EA workflow. An exported XMI can be used instead for the XMI workflow; some model-specific features may depend on the supported XMI structure.
- **Node.js, npm, and npx** to compile and test a generated Hardhat project.
- Python requirements listed in `CPEM_M2T_Tool_v1_1/requirements.txt`:

  ```text
  pywin32>=306; platform_system == "Windows"
  pytest>=8.0
  ```

- The checked-in Hardhat example declares `hardhat ^2.22.10`, `@nomicfoundation/hardhat-toolbox ^5.0.0`, and `@openzeppelin/contracts ^5.0.2` (see `output-artifacts/package.json`). Actual resolved versions should be taken from the lockfile and recorded for reproducibility.

**Requirements caveat:** The declared Python dependencies do not pin all runtime/platform versions. Users should record their Python, Node.js, Enterprise Architect, and operating-system versions, and report any additional environment-specific configuration required.

## 4. Obtain and install the research software

Clone the repository:

```bash
git clone https://github.com/mohsen3388/CPEM-M2T-Tool.git
cd CPEM-M2T-Tool
```

In Windows PowerShell, create a Python virtual environment:

```powershell
cd CPEM_M2T_Tool_v1_1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell does not allow activating the environment, invoke its Python interpreter directly instead, for example:

```powershell
.\.venv\Scripts\python.exe app.py
```

The repository currently contains a `.venv` directory; for reproducibility, **create and use a fresh local environment rather than relying on committed environment contents**.

## 5. Usage: desktop application (Windows)

From the `CPEM_M2T_Tool_v1_1` directory, execute:

```powershell
python app.py
```

Or launch the provided `run_windows.bat` from Windows Explorer.

The GUI provides the following workflow:

1. **Load an execution model.** Choose **Import CPEM XMI** and select `samples/CPEM_Diamond_Traceable_EA.xmi`; alternatively, open the appropriate research model/package in Enterprise Architect and choose **Connect to Enterprise Architect**.
2. **Inspect the model.** Confirm that the imported elements, CPEM stereotypes, and available source references appear as expected.
3. **Select the Primary SmartContract.** Where more than one contract is present, choose the relevant process-level contract in the selection control.
4. **Validate.** Click **Validate** and inspect all errors and warnings. Correct blocking validation errors before generation.
5. **Choose output directory.** Use an empty or separately named folder to avoid confusion with the example artifacts.
6. **Generate.** Click **Generate Solidity + Hardhat**. Record the Solidity file path and generated report paths displayed by the application.
7. **Compile and test.** In the generated project, install Node dependencies and use Hardhat commands as described below. The GUI also exposes **npm install**, **Compile**, and **Test** controls for the selected output folder.
8. **Inspect reports.** Compare the generated CSV/JSON traceability and metrics outputs against the corresponding example files.

**Enterprise Architect workflow:** A running EA session and a selected CPEM package are required by the direct-connection workflow. If the COM integration is unavailable, use the supplied XMI input to exercise the generator instead.

## 6. Usage: command-line transformation

The source tree contains `cli.py`, which accepts a **positional XMI input file** and an optional output directory. From `CPEM_M2T_Tool_v1_1`:

```bash
python cli.py samples/CPEM_Diamond_Traceable_EA.xmi --output generated_project
```

Expected program behavior: parse the XMI model, print validation `INFO`/`WARN`/`ERROR` messages, stop with an error if validation fails, and on success print the generated Solidity path and output project directory.

The CLI exposes a simpler interface than the GUI; unlike the GUI, it does not provide the interactive Primary SmartContract selector. If the sample is incompatible with the current parser or requires a selection/normalization step, use the GUI and record that deviation.

## 7. Compile and test published example artifacts

The pre-generated example is located in `output-artifacts/`. From the repository root:

```bash
cd output-artifacts
npm ci
npx hardhat compile
npx hardhat test
```

`npm ci` uses the included lockfile for repeatable installation. If dependency constraints prevent `npm ci`, record the error and any change made rather than silently replacing the tested environment.

The **currently published** `output-artifacts/test/generated.test.js` contains **one deployment/initial-state smoke test** for the generated contract. The manuscript describes **four automated functional tests** and a **13-step scenario** at study level; do not assume that those additional experiments are represented by this one published test file. Their scripts, execution evidence, and exact association with the manuscript should be deposited or explicitly referenced before claiming full replication of the reported validation.

The Python transformation-tool tests can be started from `CPEM_M2T_Tool_v1_1` using:

```bash
python -m pytest tests
```

**These commands are documented from checked-in source files; successful execution in a clean external environment has not been independently certified by this README.** Please record observed results and software versions in a reproduction report.

## 8. Methodology and provenance of artifacts

The methodology implemented or supported by the published artifacts is:

1. **Business-level modeling:** Define organizational, process, asset, logistics, contractual, and traceability concepts in CPDM using Enterprise Architect.
2. **Model-to-model transformation:** Apply CPDM-to-CPEM mapping rules in the modeling environment to derive an execution-level representation. This phase is **separate from the Python M2T entry point**.
3. **M2T input:** Export or select the resulting CPEM model (XMI or running EA connection).
4. **Model validation:** Inspect CPEM structure and required execution constructs; resolve reported errors.
5. **Code generation:** Generate Solidity smart-contract and Hardhat support artifacts from the CPEM execution model.
6. **Traceability reporting:** Produce machine-readable links and metrics for source/target inspection. Interpret explicit and inferred links separately.
7. **Technical assessment:** Compile and test generated artifacts; compare the output and traceability evidence with the case-study results reported in the paper.

### Published traceability-metric example

The committed `output-artifacts/reports/generation-metrics.json` reports:

| Field | Published value |
| --- | ---: |
| `evaluated_trace_elements` | 55 |
| `traced_elements` | 39 |
| `explicit_trace_links` | 0 |
| `inferred_trace_links` | 39 |
| `traceability_coverage_percent` | 70.91 |
| `cpem_to_solidity_artifacts` | 13 |

These values describe **this published output snapshot**, not an assertion that all source elements or the complete CPDM–CPEM–Solidity chain have explicit links. In particular, the JSON identifies **zero explicit** and **39 inferred** trace links. Readers should examine the individual CSV/JSON records and the tool implementation before drawing conclusions about completeness or the correctness of any inferred source mapping.

## 9. Reproducibility checklist

When independently assessing this work, record:

- Repository URL and **exact commit SHA or tagged release** used.
- Operating system, Python version, Enterprise Architect version, Node.js/npm versions, and resolved package versions.
- Input model file and whether the model was imported through XMI or the live EA connection.
- Selected Primary SmartContract and any manual modeling/configuration changes.
- Validation messages and warnings.
- List and checksums of generated `.sol`, Hardhat, CSV, and JSON files.
- Hardhat compilation and test outputs, including counts of passing/failing tests.
- Whether the evaluation is limited to the published smoke test or includes the additional manuscript tests and end-to-end scenario.
- Any differences between the newly generated results and the committed example artifacts.

## 10. Limitations and interpretation

- The repository directly covers the **M2T implementation**, not a self-contained automated execution of every earlier CPDM modeling/M2M step.
- Some workflows depend on proprietary **Sparx Enterprise Architect** and Windows COM integration; XMI provides an alternative entry point for the published M2T parser but does not reproduce all activities inside EA.
- The published Hardhat example contains **one** test, whereas broader manuscript validation requires additional scripts/evidence to reproduce independently.
- Current traceability reports combine inferred and explicit link categories; the published metrics must not be described as 100% explicit end-to-end traceability.
- The project is a research demonstrator; **no production security audit or suitability for handling real financial assets is claimed**.
- Public research artifacts do not by themselves prove that all data required by PeerJ's curated-dataset and code-availability policies have been formally deposited in the submission system.

## 11. Data availability and code availability statements

**Code availability:** Source files, a CPEM XMI example, generated Solidity/Hardhat artifacts, and traceability reports are publicly available at https://github.com/mohsen3388/CPEM-M2T-Tool . Broader modeling research materials are referenced at https://github.com/mohsen3388/collabchain-platform . The authors should associate the final version/commit or archived DOI with the PeerJ manuscript submission.

**Data availability:** The supplied model files and the CSV/JSON generation reports are example inputs and derived research artifacts. To satisfy any separate request for curated raw data, the authors should identify all actual inputs and supporting evaluation outputs used to derive the reported findings and register them explicitly in the PeerJ data-availability fields or a suitable archived research dataset.

**Stable archiving:** A versioned release and archival DOI (e.g., via a suitable research repository) are recommended before final resubmission. **No DOI is claimed here until one has actually been issued.**

## 12. Citation

If referring to this software before the article has been published, cite the authors, project title, the **exact repository version/commit**, and its public URL. The associated manuscript is titled:

> Khoram Dastjerdi, M., García-García, J. A., and González Enríquez, J. *A Model-Driven Approach to the Definition and Blockchain-Based Execution of Collaborative Supply Chain Processes.* Manuscript submitted to PeerJ Computer Science.

Replace the provisional manuscript reference with the formal publication citation and DOI **only after publication**.

## 13. License and contributions

**License status:** At the time this README was prepared, the repository did **not** contain an identifiable top-level open-source `LICENSE` file or a license declared in repository metadata. Public visibility does **not** itself grant reuse, modification, or redistribution rights. The authors should select and add an appropriate license before asserting an open-source license.

For questions about the research artifacts, use the repository issue tracker or contact the corresponding author listed in the manuscript. Contributions and proposed modifications should be discussed with the maintainers; no separate contribution policy is asserted until one is published.
