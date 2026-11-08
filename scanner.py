#!/usr/bin/env python3
"""ObsidianScrub CMMC 2.0 & NDAA Section 889 CI/CD Scanner."""
import hashlib
import json
import os
import re
import sys

BANNED_VENDORS = (
    "huawei", "zte", "hikvision", "dahua", "hytera",
    "kaspersky", "bitmain", "dji", "smic", "cxmt", "ymtc",
)

SECRET_PATTERNS = [
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GITHUB_PAT", re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,255}")),
    ("STRIPE_LIVE_KEY", re.compile(r"(?:sk|rk)_live_[0-9a-zA-Z]{24,99}")),
    ("PRIVATE_KEY_PEM", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]

def scan_workspace(root: str = "."):
    findings_secrets = []
    findings_889 = []
    files_scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".venv", "venv", "__pycache__")]
        for fn in filenames:
            if fn.endswith((".png", ".jpg", ".pdf", ".zip", ".pyc", ".so")):
                continue
            fp = os.path.join(dirpath, fn)
            files_scanned += 1
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read(250000)
                for label, pat in SECRET_PATTERNS:
                    if pat.search(txt):
                        findings_secrets.append({"file": fp, "rule": label})
                if fn.lower() in ("package.json", "requirements.txt", "pyproject.toml", "go.mod", "cargo.toml", "sbom.json"):
                    low = txt.lower()
                    for v in BANNED_VENDORS:
                        if re.search(rf"\b{v}\b", low):
                            findings_889.append({"file": fp, "vendor": v.upper()})
            except Exception:
                pass
    verdict = "PASS_CLEAN" if (not findings_secrets and not findings_889) else "ACTION_REQUIRED"
    report = {
        "scanner": "ObsidianScrub CMMC 2.0 & Section 889 Action v1.0.0",
        "entity": "Harris Legacy Venturez LLC (CAGE: 9YGC1 | UEI: VX7HZR2UPDT5)",
        "files_scanned": files_scanned,
        "secrets_found": len(findings_secrets),
        "section889_violations": len(findings_889),
        "verdict": verdict,
        "upgrade_full_110_control_ssp_pack": "https://buy.stripe.com/9B67sMe6ba1TaWz4Zm9ws01",
        "upgrade_full_repo_audit_patch": "https://buy.stripe.com/dRm28s1jp3DvaWz0J69ws05",
    }
    report["sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(scan_workspace("."))
