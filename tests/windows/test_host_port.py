"""Host-only checks; Windows bootstrap/XEX execution are separate acceptance tests."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/windows"))
from build_plan import plan, msys_path  # noqa: E402
from check_tools import check  # noqa: E402


class BuildPlanTests(unittest.TestCase):
    def test_paths_and_positional_arguments(self):
        args, env = plan("C:/msys64", "C:/repo/xsdk", "D:/tools/compiler", "D:/work", 4, "sdk")
        self.assertEqual(args[1:4], ["--login", "/c/repo/xsdk/tools/windows/run.sh", "sdk"])
        self.assertEqual(args[4:8], ["/c/repo/xsdk", "/d/tools/compiler", "/d/work", "4"])
        self.assertEqual(env["MSYSTEM"], "UCRT64")

    def test_project_is_not_shell_code(self):
        project = "C:/projects/has space;$(whoami)"
        args, _ = plan("C:/msys64", "C:/sdk", "C:/compiler", "C:/work", 2, "project", project)
        self.assertEqual(args[8], "/c/projects/has space;$(whoami)")
        self.assertNotIn("-c", args)

    def test_reject_bad_environment(self):
        for jobs in (0, -1, 65, "four"):
            with self.assertRaises(ValueError):
                plan("C:/msys64", "C:/sdk", "C:/compiler", "C:/work", jobs, "sdk")
        with self.assertRaises(ValueError):
            plan("C:/msys64", "C:/SDK space", "C:/compiler", "C:/work", 4, "sdk")
        for path in ("/home/linux", "//server/share", "C:/repo\ncmd", "relative"):
            with self.assertRaises(ValueError):
                msys_path(path)

    def test_backslashes(self):
        self.assertEqual(msys_path(r"C:\Users\Axel\xsdk"), "/c/Users/Axel/xsdk")

    def test_missing_compiler_is_an_error(self):
        with self.assertRaises(RuntimeError):
            check(ROOT / "does-not-exist")

    def test_incomplete_or_non_windows_toolchain_is_rejected(self):
        names = ("gcc", "g++", "as", "ld", "ar", "ranlib", "objcopy", "objdump", "nm", "readelf", "strip")
        with tempfile.TemporaryDirectory() as folder:
            binary_dir = Path(folder) / "bin"
            binary_dir.mkdir()
            for name in names:
                (binary_dir / ("powerpc-xsdk-elf-" + name + ".exe")).write_bytes(b"MZ")
            cxx = binary_dir / "powerpc-xsdk-elf-g++.exe"
            cxx.unlink()
            with self.assertRaisesRegex(RuntimeError, r"Missing native tool.*g\+\+"):
                check(folder)
            cxx.write_bytes(b"\x7fELF")
            with self.assertRaisesRegex(RuntimeError, "Not a Windows PE"):
                check(folder)
            cxx.write_bytes(b"MZ")
            with mock.patch("check_tools.subprocess.check_output", return_value="x86_64-w64-mingw32"):
                with self.assertRaisesRegex(RuntimeError, "Wrong target compiler"):
                    check(folder)
            with mock.patch("check_tools.subprocess.check_output", return_value="powerpc-xsdk-elf"), \
                    mock.patch("check_tools.subprocess.run") as run:
                run.side_effect = [None, subprocess.CalledProcessError(1, "g++")]
                with self.assertRaises(subprocess.CalledProcessError):
                    check(folder)
                self.assertIn("-std=c++23", run.call_args.args[0])

    def test_host_library_name(self):
        for platform, suffix in (("win32", ".dll"), ("linux", ".so")):
            spec = importlib.util.spec_from_file_location("port_native", ROOT / "xenos-toolchain/xsc/native.py")
            module = importlib.util.module_from_spec(spec)
            with mock.patch.object(sys, "platform", platform):
                spec.loader.exec_module(module)
            self.assertEqual(module.LIBRARY.suffix, suffix)

    def test_toolchain_host_flags_without_building(self):
        import os
        script = str(ROOT / "tools/toolchain/build.sh")
        for system, expected in (("", False), ("UCRT64", True)):
            env = dict(os.environ, MSYSTEM=system, PREFIX="/tmp/xsdk-native-compiler", WORK="/tmp/xsdk-native-work")
            result = subprocess.run(["bash", script, "--print-config"], env=env, check=False,
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.name == "nt" and not system:
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Open the MSYS2 UCRT64 environment", result.stderr)
                continue
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual("--host=x86_64-w64-mingw32" in result.stdout, expected)
            self.assertIn("--target=powerpc-xsdk-elf", result.stdout)

    def test_make_windows_links_dll(self):
        result = subprocess.run(["make", "-Bn", "OS=Windows_NT", "build/host/libxsc.dll"],
                                cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        self.assertIn("--export-all-symbols", result.stdout)
        self.assertIn("-o build/host/libxsc.dll", result.stdout)
        self.assertNotIn("-fPIC", result.stdout)


if __name__ == "__main__":
    unittest.main()
