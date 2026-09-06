from __future__ import annotations
import json, subprocess, shutil, os
from pathlib import Path


def prepare_hardhat_project(out_dir: str | Path, contract_name: str):
    out = Path(out_dir)
    (out / "test").mkdir(parents=True, exist_ok=True)
    package = {
        "name": "cpem-generated-hardhat-project",
        "version": "1.1.0",
        "private": True,
        "scripts": {"compile": "hardhat compile", "test": "hardhat test"},
        "devDependencies": {
            "hardhat": "^2.22.10",
            "@nomicfoundation/hardhat-toolbox": "^5.0.0",
            "@openzeppelin/contracts": "^5.0.2"
        }
    }
    (out / "package.json").write_text(json.dumps(package, indent=2), encoding="utf-8")
    (out / "hardhat.config.js").write_text(
        'require("@nomicfoundation/hardhat-toolbox");\nmodule.exports = { solidity: "0.8.24" };\n', encoding="utf-8"
    )
    test_js = f'''const {{ expect }} = require("chai");
const {{ ethers }} = require("hardhat");

describe("Generated CPEM contract", function () {{
  it("deploys and exposes initial state", async function () {{
    const F = await ethers.getContractFactory("{contract_name}");
    const c = await F.deploy();
    await c.waitForDeployment();
    expect(await c.state()).to.equal(0n);
  }});
}});
'''
    (out / "test" / "generated.test.js").write_text(test_js, encoding="utf-8")


def tool_status():
    return {
        "node": shutil.which("node.exe") or shutil.which("node"),
        "npm": shutil.which("npm.cmd") or shutil.which("npm.exe") or shutil.which("npm"),
        "npx": shutil.which("npx.cmd") or shutil.which("npx.exe") or shutil.which("npx"),
    }


def _run_windows_batch(exe: str, args: list[str], cwd: Path):
    comspec = os.environ.get("COMSPEC") or shutil.which("cmd.exe") or "cmd.exe"
    # cmd.exe is required for npm.cmd/npx.cmd on Windows.
    cmdline = subprocess.list2cmdline([exe, *args])
    return subprocess.run([comspec, "/d", "/s", "/c", cmdline], cwd=cwd, capture_output=True, text=True)


def run_command(out_dir: str | Path, command: str):
    out = Path(out_dir)
    if not (out / "package.json").exists():
        raise RuntimeError("Generated Hardhat project not found. Generate Solidity + Hardhat first.")
    if command not in {"install", "compile", "test"}:
        raise ValueError(command)
    status = tool_status()
    if command == "install":
        exe, args = status["npm"], ["install"]
        missing = "npm"
    else:
        exe, args = status["npx"], ["hardhat", command]
        missing = "npx"
    if not exe:
        raise RuntimeError(f"{missing} not found. Install Node.js LTS, reopen the terminal/application, and try again.")
    if os.name == "nt" and str(exe).lower().endswith((".cmd", ".bat")):
        p = _run_windows_batch(str(exe), args, out)
    else:
        p = subprocess.run([str(exe), *args], cwd=out, capture_output=True, text=True, shell=False)
    return p.returncode, p.stdout + p.stderr
