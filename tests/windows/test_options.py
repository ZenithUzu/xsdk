"""Reject unsafe build options and updates that could overwrite user work."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools/windows"))
from build_plan import plan
from options import cmake_options
from update import update


class OptionsTests(unittest.TestCase):
    def test_windows_options_remain_separate_arguments(self):
        args, _ = plan("C:/msys64", "C:/sdk", "C:/compiler", "C:/work", 4, "project", "C:/project",
                       "Debug", "C:/SDL build", '["-DNAME=hello world;$(whoami)"]')
        self.assertEqual(args[8:12], ["/c/project", "Debug", "/c/SDL build", "cmake_check"])
        self.assertEqual(args[-1], "-DNAME=hello world;$(whoami)")
        self.assertNotIn("-c", args)

    def test_reject_options_that_replace_build_paths(self):
        for value in ('["-S"]', '["-DCMAKE_TOOLCHAIN_FILE=x"]', '["-DSDL3_DIR:PATH=x"]',
                      '["-DCMAKE_BUILD_TYPE=Debug"]', '["-DXSDK_TOOLCHAIN=x"]', '{}', '[1]', 'bad'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                cmake_options(value)
        with self.assertRaises(ValueError):
            plan("C:/msys64", "C:/sdk", "C:/compiler", "C:/work", 4, "advanced", target="clean;whoami")

    def test_zip_update_refuses_to_overwrite_files(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaisesRegex(ValueError, "copia es ZIP"):
            update(folder)

    def test_dirty_update_never_fetches_or_merges(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            with mock.patch("update.subprocess.check_output", side_effect=[
                    "https://github.com/ZenithUzu/xsdk.git\n", " M README.md\n"]) as git:
                with self.assertRaisesRegex(ValueError, "cambios locales"):
                    update(folder)
                self.assertEqual(git.call_count, 2)

    def test_clean_update_uses_fast_forward_only(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".git").mkdir()
            with mock.patch("update.subprocess.check_output", side_effect=[
                    "https://github.com/ZenithUzu/xsdk.git\n", "", "main", "", "", "abcdef0"] ) as git:
                update(folder)
                self.assertIn(["git", "-C", folder, "merge", "--ff-only", "refs/remotes/origin/main"],
                              [call.args[0] for call in git.call_args_list])

class PackageTests(unittest.TestCase):
    def test_bundle_contains_sources_not_private_build_files(self):
        import hashlib
        import zipfile
        from package import package
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sdk, compiler, work = root / "sdk", root / "compiler", root / "work"
            sdk.mkdir()
            (sdk / "LICENSE").write_text("license")
            (compiler / "bin").mkdir(parents=True)
            (compiler / "bin/glslang.exe").write_bytes(b"MZ")
            sources = work / "toolchain/src"
            sources.mkdir(parents=True)
            for name in ("gcc", "binutils", "newlib"):
                (sources / (name + ".tar.xz")).write_bytes(b"source fixture")
            glslang = work / "glslang"
            glslang.mkdir()
            (glslang / "CMakeLists.txt").write_text("source")
            (glslang / ".git").mkdir()
            (glslang / ".git/config").write_text("private remote configuration")
            (glslang / "build-windows").mkdir()
            (glslang / "build-windows/cache").write_text("build")
            output = work / "bundle.zip"
            with mock.patch("package.check"), mock.patch("package.subprocess.check_output", side_effect=[b"LICENSE\0", b"CMakeLists.txt\0"]):
                package(sdk, compiler, output)
            with zipfile.ZipFile(output) as archive:
                self.assertIn("sources/gcc.tar.xz", archive.namelist())
                self.assertIn("sdk/LICENSE", archive.namelist())
                self.assertNotIn("sources/glslang/.git/config", archive.namelist())
                self.assertNotIn("sources/glslang/build-windows/cache", archive.namelist())
            actual = hashlib.sha256(output.read_bytes()).hexdigest()
            self.assertTrue(Path(str(output) + ".sha256").read_text().startswith(actual))


if __name__ == "__main__":
    unittest.main()
