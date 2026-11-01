"""Exercise the host compiler library with the upstream SPIR-V fixture."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "xenos-toolchain"))
from xsc import native  # noqa: E402

if __name__ == "__main__":
    library = native._load()
    print(f"Loaded: {native.LIBRARY}")
    # Existing fixture includes a normal vertex shader, not an empty stub.
    fixtures = sorted((root / "xenos-toolchain/xsc/testdata").glob("*.vert.spv"))
    if not fixtures:
        raise SystemExit("No SPIR-V vertex fixture found")
    resolved = native.resolve_spirv(fixtures[0].read_bytes())
    if not isinstance(resolved, dict):
        raise SystemExit("The shader resolver returned no interface")
    print(f"PASS: native library resolved {fixtures[0].name}")
