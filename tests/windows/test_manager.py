"""Discovery reuses installations; status checks never build or update components."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools/windows"))
from manager import discover, fingerprint, inspect, mark


class ManagerTests(unittest.TestCase):
    def test_discovery_preserves_existing_tools_and_explicit_shader(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            compiler = root / "compiler/bin"
            compiler.mkdir(parents=True)
            (compiler / "powerpc-xsdk-elf-gcc.exe").write_bytes(b"MZ")
            shader = root / "my-glslang.exe"
            shader.write_bytes(b"MZ")
            values = {"prefix": str(compiler.parent), "msys": str(root / "msys"), "glslang": str(shader)}
            with mock.patch("manager.shutil.which", return_value=None):
                found = discover(values)
            self.assertEqual(found["prefix"], str(compiler.parent))
            self.assertEqual(found["glslang"], str(shader))

    def test_existing_unregistered_tools_are_not_reported_outdated(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "tools/toolchain").mkdir(parents=True)
            (root / "tools/toolchain/build.sh").write_text("GCC=gcc-15.3.0\n")
            (root / "bin").mkdir()
            for name in ("gcc", "g++"):
                (root / ("bin/powerpc-xsdk-elf-" + name + ".exe")).write_bytes(b"MZ")
            values = {"sdk": str(root), "prefix": str(root), "work": str(root / "work"), "msys": str(root)}

            def output(args, env=None):
                if args[-1] == "-dumpfullversion":
                    return "15.3.0"
                if args[-1] == "-dumpmachine":
                    return "powerpc-xsdk-elf"
                return ""

            with mock.patch("manager.command", side_effect=output):
                report = inspect(values)
            compiler = next(row for row in report["rows"] if row["key"] == "toolchain")
            self.assertIn("sin registro", compiler["status"])
            self.assertNotIn("Versión distinta", compiler["status"])
            self.assertFalse((root / "work").exists())

    def test_recipe_changes_are_recorded_outside_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sdk = root / "sdk"
            (sdk / "src").mkdir(parents=True)
            source = sdk / "src/test.c"
            source.write_text("int value;\n")
            before = fingerprint(sdk, "sdk")
            mark(sdk, root / "compiler", root / "work", "sdk")
            self.assertTrue((root / "work/components.json").is_file())
            source.write_text("int changed;\n")
            self.assertNotEqual(before, fingerprint(sdk, "sdk"))
            self.assertFalse((sdk / "components.json").exists())


if __name__ == "__main__":
    unittest.main()
