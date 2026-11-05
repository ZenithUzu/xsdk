#!/bin/bash
# Explicit setup action only. No user value is interpolated as shell code.
set -euo pipefail
[[ "${MSYSTEM:-}" == UCRT64 ]] || { echo 'Use MSYS2 UCRT64' >&2; exit 1; }
export PATH="/ucrt64/bin:/usr/bin:$PATH"
if [[ ! -x /ucrt64/bin/python.exe ]]; then
    pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-python
fi
exec /ucrt64/bin/python.exe "$@"
