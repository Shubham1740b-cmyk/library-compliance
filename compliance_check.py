#!/usr/bin/env python3
"""Compliance as Code - 3 policies checked automatically on every push.

  POLICY 1 : No hardcoded API keys / secrets
  POLICY 2 : Debug mode disabled
  POLICY 3 : Application logging enabled (to a separate file)

Exit code 0 -> all PASS (pipeline continues)
Exit code 1 -> any FAIL (pipeline stops)
"""
import os
import re
import sys
from datetime import datetime

ROOT = "."
REPORT = "compliance_report.txt"
SKIP_DIRS = {".git", "__pycache__", "venv", ".venv", "logs", "node_modules"}
SKIP_FILES = {"compliance_check.py"}          # this file contains the regex patterns

SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub token", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("Hardcoded secret assignment", re.compile(
        r"""(?i)\b(api[_-]?key|secret[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*["'][^"'\s]{8,}["']""")),
]
DEBUG_PATTERNS = [
    re.compile(r"(?i)\bdebug\s*=\s*true\b"),
    re.compile(r"""(?i)["']debug["']\s*\]?\s*=\s*true\b"""),
    re.compile(r"(?i)FLASK_DEBUG\s*=\s*1"),
]
LOGGING_PATTERNS = [re.compile(r"FileHandler\s*\("),
                    re.compile(r"logging\.basicConfig\([^)]*filename\s*=")]


def source_files(exts):
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(exts) and f not in SKIP_FILES:
                yield os.path.join(folder, f)


def read_lines(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        return fh.read().splitlines()


def check_no_hardcoded_secrets():
    issues = []
    for path in source_files((".py", ".env", ".json", ".yml", ".yaml", ".cfg", ".ini")):
        for no, line in enumerate(read_lines(path), 1):
            if line.strip().startswith("#"):
                continue
            for label, rx in SECRET_PATTERNS:
                if rx.search(line):
                    issues.append(f"{path}:{no}  {label}")
    return issues


def check_debug_disabled():
    issues = []
    for path in source_files((".py", ".env", ".cfg", ".ini")):
        for no, line in enumerate(read_lines(path), 1):
            if line.strip().startswith("#"):
                continue
            if any(rx.search(line) for rx in DEBUG_PATTERNS):
                issues.append(f"{path}:{no}  debug mode is ON")
    return issues


def check_logging_enabled():
    for path in source_files((".py",)):
        text = "\n".join(read_lines(path))
        if any(rx.search(text) for rx in LOGGING_PATTERNS):
            return []                                  # found file-based logging
    return ["No FileHandler / basicConfig(filename=...) found - logs not going to a separate file"]


POLICIES = [
    ("P1", "No hardcoded API keys", check_no_hardcoded_secrets),
    ("P2", "Debug mode disabled", check_debug_disabled),
    ("P3", "Application logging enabled (separate file)", check_logging_enabled),
]


def main():
    lines = ["=" * 62, "        COMPLIANCE REPORT - Library Management System", "=" * 62,
             f"Generated : {datetime.now():%Y-%m-%d %H:%M:%S}", ""]
    failed = 0
    for pid, title, fn in POLICIES:
        issues = fn()
        status = "PASS" if not issues else "FAIL"
        failed += bool(issues)
        lines.append(f"[{status}] {pid}: {title}")
        lines += [f"         -> {i}" for i in issues]
    lines += ["", "-" * 62,
              f"POLICIES PASSED : {len(POLICIES) - failed}/{len(POLICIES)}",
              "FINAL RESULT    : " + ("COMPLIANT - pipeline may continue" if not failed
                                      else "NON-COMPLIANT - pipeline blocked"),
              "=" * 62]
    report = "\n".join(lines)
    print(report)
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write(report + "\n")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
