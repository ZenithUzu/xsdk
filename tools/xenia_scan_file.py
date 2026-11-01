#!/usr/bin/env python3
"""Run objdump and feed its disassembly to xenia_scan.py on every host."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: xenia_scan_file.py <objdump> <elf>", file=sys.stderr)
        return 2
    output = subprocess.run(
        [sys.argv[1], "-d", sys.argv[2]],
        check=False,
        stdout=subprocess.PIPE,
        text=True,
    )
    scanner = subprocess.run(
        [sys.executable, __file__.replace("xenia_scan_file.py", "xenia_scan.py")],
        input=output.stdout,
        text=True,
        check=False,
    )
    return output.returncode or scanner.returncode


if __name__ == "__main__":
    raise SystemExit(main())
