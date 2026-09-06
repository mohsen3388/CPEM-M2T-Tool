from __future__ import annotations
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from csc_mde.xmi_parser import parse_xmi
from csc_mde.ea_connector import connect_to_running_ea
from csc_mde.validator import validate
from csc_mde.pipeline import generate_project
from csc_mde.hardhat import run_command, tool_status

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPEM → Solidity M2T Tool v1.1")
        self.geometry("1180x760")
        self.model = None
        self.out_dir = tk.StringVar(value=str(Path.cwd() / "generated_project"))
        self.primary_contract = tk.StringVar()
        self.contract_name_to_id = {}
        self.node_status = tk.StringVar(value="Checking Node.js/npm...")
        self._build(); self.after(300, self.refresh_tool_status)

    def _build(self):
        top = ttk.Frame(self, padding=10); top.pack(fill="x")
        ttk.Button(top, text="Connect to Enterprise Architect", command=self.load_ea).pack(side="left", padx=4)
        ttk.Button(top, text="Import CPEM XMI", command=self.load_xmi).pack(side="left", padx=4)
        ttk.Button(top, text="Validate", command=self.do_validate).pack(side="left", padx=4)
        ttk.Button(top, text="Generate Solidity + Hardhat", command=self.generate).pack(side="left", padx=4)

        sel = ttk.Frame(self, padding=(10,0)); sel.pack(fill="x")
        ttk.Label(sel, text="Primary SmartContract:").pack(side="left")
        self.contract_combo = ttk.Combobox(sel, textvariable=self.primary_contract, state="readonly", width=55)
        self.contract_combo.pack(side="left", padx=6)
        ttk.Label(sel, text="Select the process-level contract when more than one SmartContract exists.").pack(side="left", padx=8)

        out = ttk.Frame(self, padding=(10,5)); out.pack(fill="x")
        ttk.Label(out, text="Output folder:").pack(side="left")
        ttk.Entry(out, textvariable=self.out_dir).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(out, text="Browse", command=self.choose_out).pack(side="left")

        hh = ttk.LabelFrame(self, text="Hardhat", padding=8); hh.pack(fill="x", padx=10, pady=8)
        ttk.Button(hh, text="npm install", command=lambda:self.run_hh("install")).pack(side="left", padx=4)
        ttk.Button(hh, text="Compile", command=lambda:self.run_hh("compile")).pack(side="left", padx=4)
        ttk.Button(hh, text="Test", command=lambda:self.run_hh("test")).pack(side="left", padx=4)
        ttk.Button(hh, text="Refresh tool status", command=self.refresh_tool_status).pack(side="left", padx=8)
        ttk.Label(hh, textvariable=self.node_status).pack(side="left", padx=12)

        cols = ("name","stereotype","trace","method")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for c, t, w in [("name","Element",300),("stereotype","CPEM stereotype",180),("trace","CPDM trace source",330),("method","Trace method",190)]:
            self.tree.heading(c,text=t); self.tree.column(c,width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=6)

        self.log = tk.Text(self, height=14, wrap="word"); self.log.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.say("Ready. Open EA and select the CPEM package, or import an XMI file.")

    def say(self, msg): self.log.insert("end", msg + "\n"); self.log.see("end")
    def choose_out(self):
        d = filedialog.askdirectory()
        if d: self.out_dir.set(d)

    def refresh_tool_status(self):
        s = tool_status()
        if s["node"] and s["npm"] and s["npx"]:
            self.node_status.set("Node.js/npm/npx detected ✓")
        else:
            missing = [k for k,v in s.items() if not v]
            self.node_status.set("Missing: " + ", ".join(missing) + " — install Node.js LTS and reopen app")

    def load_xmi(self):
        p = filedialog.askopenfilename(filetypes=[("XMI/XML", "*.xmi *.xml"), ("All", "*.*")])
        if not p: return
        try:
            self.model = parse_xmi(p); self.refresh_model(); self.say(f"Loaded XMI: {p}")
        except Exception as e: messagebox.showerror("XMI", str(e))

    def load_ea(self):
        try:
            self.model = connect_to_running_ea(); self.refresh_model(); self.say(f"Connected to EA package: {self.model.name}")
        except Exception as e: messagebox.showerror("Enterprise Architect", str(e))

    def refresh_model(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        self.contract_name_to_id = {}; self.contract_combo["values"] = (); self.primary_contract.set("")
        if not self.model: return
        # Only display CPEM-side elements, not CPDM shadow elements used for trace resolution.
        for e in self.model.elements.values():
            if e.stereotype.lower() in {"activity","product","order","supplychainprocess","decision","metric","indicator","okr","traceabilityrule","riskassessment","contract","payment","event","insurance","transportconditions","criticalactivity","integratedrepository"} or e.stereotype.lower().startswith("cpdm"):
                continue
            src, method = self.model.traced_source_with_method(e.id)
            self.tree.insert("", "end", values=(e.name, e.stereotype, src.name if src else "", method if src else ""))
        contracts = self.model.by_stereotype("SmartContract")
        names = []
        for c in contracts:
            label = c.name; names.append(label); self.contract_name_to_id[label] = c.id
        self.contract_combo["values"] = names
        if len(names) == 1:
            self.primary_contract.set(names[0])
        elif names:
            # Prefer the process-level contract, but leave it visible and user-changeable.
            preferred = next((n for n in names if "processcontract" in n.lower() or "p0" in n.lower() or "purchasing diamond" in n.lower()), names[0])
            self.primary_contract.set(preferred)
            self.say(f"Primary SmartContract preselected: {preferred} (change it if needed).")

    def primary_id(self): return self.contract_name_to_id.get(self.primary_contract.get())

    def do_validate(self):
        if not self.model: return messagebox.showwarning("Validate", "Load a model first")
        r = validate(self.model, self.primary_id())
        self.say("--- Validation ---")
        for x in r.info: self.say("INFO: " + x)
        for x in r.warnings: self.say("WARN: " + x)
        for x in r.errors: self.say("ERROR: " + x)
        if r.ok: messagebox.showinfo("Validation", "Model is valid for M2T v1.1")

    def generate(self):
        if not self.model: return messagebox.showwarning("Generate", "Load a model first")
        if len(self.model.by_stereotype("SmartContract")) > 1 and not self.primary_id():
            return messagebox.showwarning("Generate", "Select the Primary SmartContract first")
        try:
            res = generate_project(self.model, self.out_dir.get(), self.primary_id())
            self.say(f"Generated Solidity: {res['solidity']}")
            for f in res['trace_files']: self.say(f"Generated report: {f}")
            self.say("Hardhat project prepared. Run npm install, then Compile and Test.")
            messagebox.showinfo("Generated", f"Project generated in:\n{self.out_dir.get()}")
        except Exception as e: messagebox.showerror("Generate", str(e))

    def run_hh(self, action):
        def work():
            try:
                self.say(f"$ {action} ...")
                code, text = run_command(self.out_dir.get(), action)
                self.say(text.strip() or "(no output)"); self.say(f"Exit code: {code}")
                if code == 0: self.say(f"SUCCESS: Hardhat {action} completed.")
                else: self.say(f"FAILED: Hardhat {action} returned exit code {code}.")
            except Exception as e: self.say("ERROR: " + str(e))
        threading.Thread(target=work, daemon=True).start()

if __name__ == "__main__": App().mainloop()
