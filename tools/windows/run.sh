#!/bin/bash
# Native Windows build stages, launched by the GUI with positional arguments.
set -euo pipefail
[[ "${MSYSTEM:-}" == UCRT64 ]] || { echo 'Use MSYS2 UCRT64' >&2; exit 1; }
action=${1:?action} sdk=${2:?sdk} prefix=${3:?prefix} work=${4:?work} jobs=${5:-4} project=${6:-}
build_type=${7:-Release} sdl=${8:-} target=${9:-cmake_check}
extra=()
if (( $# > 9 )); then extra=("${@:10}"); fi
case "$build_type" in Debug|Release|RelWithDebInfo|MinSizeRel) ;; *) echo "Invalid build type" >&2; exit 1;; esac
sdl_args=()
[[ -z "$sdl" ]] || sdl_args=("-DSDL3_DIR=$(cygpath -m "$sdl")")
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo 'Invalid job count' >&2; exit 1; }
for path in "$sdk" "$prefix" "$work"; do
	[[ "$path" != *' '* && "$path" != *$'\n'* ]] || { echo 'Use paths without spaces/newlines' >&2; exit 1; }
done
cd "$sdk"
export PATH="$prefix/bin:/ucrt64/bin:/usr/bin:$PATH"
case "$action" in
	dependencies)
		pacman -S --needed --noconfirm base-devel texinfo git curl patch tar xz \
			mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gmp \
			mingw-w64-ucrt-x86_64-mpfr mingw-w64-ucrt-x86_64-mpc \
			mingw-w64-ucrt-x86_64-python mingw-w64-ucrt-x86_64-cmake \
			mingw-w64-ucrt-x86_64-ninja
		;;
	toolchain)
		PREFIX="$prefix" WORK="$work/toolchain" JOBS="$jobs" bash tools/toolchain/build.sh
		python3 tools/windows/check_tools.py "$prefix"
		;;
	shaders)
		mkdir -p "$work"
		if [[ ! -d "$work/glslang/.git" ]]; then
			[[ ! -e "$work/glslang" ]] || { echo 'glslang directory exists but is not a checkout' >&2; exit 1; }
			git clone --depth 1 --branch xenon https://github.com/xenosworks/glslang-xenon.git "$work/glslang"
		fi
		(cd "$work/glslang" && python3 update_glslang_sources.py)
		cmake -S "$work/glslang" -B "$work/glslang/build-windows" -G Ninja \
			-DCMAKE_BUILD_TYPE=Release -DENABLE_OPT=ON -DSPIRV_SKIP_EXECUTABLES=ON -DGLSLANG_TESTS=OFF
		cmake --build "$work/glslang/build-windows" --parallel "$jobs"
		mkdir -p "$prefix/bin"
		cp "$work/glslang/build-windows/StandAlone/glslang.exe" "$prefix/bin/glslang.exe"
		"$prefix/bin/glslang.exe" --version
		;;
	sdk)
		python3 tools/windows/check_tools.py "$prefix"
		make -j"$jobs" TOOLCHAIN="$prefix/bin/powerpc-xsdk-elf-" PYTHON=python3 HOST_CC=gcc
		[[ -s build/libxsdk.a && -s build/host/libxsc.dll && -s build/xsdk_test.xex ]]
		python3 tools/windows/check_xsc.py
		;;
	validate)
		python3 -m unittest discover -s tests/windows -v
		python3 tools/windows/check_tools.py "$prefix"
		make cmake_check TOOLCHAIN="$prefix/bin/powerpc-xsdk-elf-" PYTHON=python3 HOST_CC=gcc
		python3 tools/windows/check_xsc.py
		;;
	samples)
		[[ -s build/host/libxsc.dll && -s build/libxsdk.a ]] || { echo 'Build the SDK first' >&2; exit 1; }
		python3 tools/windows/samples.py "$sdk" "$prefix" "$jobs" "$build_type" "$sdl" "${extra[@]}"
		[[ -s build/samples/hello/hello.xex && -s build/samples/triangle/triangle.xex ]]
		;;
	advanced)
		python3 tools/windows/advanced.py "$target" "$prefix" "$jobs" "$build_type" "${sdl:+$(cygpath -m "$sdl")}"
		;;
	update)
		python3 tools/windows/update.py "$sdk"
		;;
	bundle)
		python3 tools/windows/package.py "$sdk" "$prefix" "$work/xsdk-windows-portable.zip"
		;;
	project)
		[[ -f "$project/CMakeLists.txt" ]] || { echo 'Select a CMake project' >&2; exit 1; }
		[[ -s build/host/libxsc.dll && -s build/libxsdk.a ]] || { echo 'Build the SDK first' >&2; exit 1; }
		cmake -S "$project" -B "$project/build-xsdk-windows" -G Ninja \
			-DCMAKE_TOOLCHAIN_FILE="$(cygpath -m "$sdk/cmake/xsdk.cmake")" \
			-DXSDK_TOOLCHAIN="$(cygpath -m "$prefix")" -DCMAKE_BUILD_TYPE="$build_type" \
			"${sdl_args[@]}" "${extra[@]}"
		cmake --build "$project/build-xsdk-windows" --parallel "$jobs"
		;;
	diagnose)
		uname -a
		gcc --version
		python3 --version
		cmake --version
		python3 tools/windows/check_tools.py "$prefix"
		;;
	*) echo "Unknown action: $action" >&2; exit 1 ;;
esac
echo "Completed: $action"
