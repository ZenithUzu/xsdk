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
if [[ -n "${XSDK_GLSLANG_OVERRIDE:-}" ]]; then
	shader_path=$(cygpath -u "$XSDK_GLSLANG_OVERRIDE")
	export PATH="$(dirname "$shader_path"):$PATH"
	if [[ "$action" == project ]]; then extra+=("-DXSDK_GLSLANG=$(cygpath -m "$shader_path")"); fi
fi
if [[ "$action" == shaders_update ]]; then
	python3 tools/windows/update.py "$work/glslang" shaders
	action=shaders
fi
case "$action" in
	dependencies)
		pacman -S --needed --noconfirm base-devel texinfo git curl patch tar xz \
			mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gmp \
			mingw-w64-ucrt-x86_64-mpfr mingw-w64-ucrt-x86_64-mpc \
			mingw-w64-ucrt-x86_64-python mingw-w64-ucrt-x86_64-cmake \
			mingw-w64-ucrt-x86_64-ninja
		;;
	toolchain|toolchain_fresh)
		toolchain_work="$work/toolchain"
		if [[ "$action" == toolchain_fresh ]]; then
			[[ ! -e "$prefix" ]] || { echo 'Choose a new compiler folder; the existing tools will be kept' >&2; exit 1; }
			toolchain_work="$work/toolchain-updates/$(date +%Y%m%d-%H%M%S)"
		fi
		PREFIX="$prefix" WORK="$toolchain_work" JOBS="$jobs" bash tools/toolchain/build.sh
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
		python3 tools/windows/update.py "$sdk" sdk "$work/sdk-updates"
		;;
	bundle)
		python3 tools/windows/package.py "$sdk" "$prefix" "$work/xsdk-windows-portable.zip"
		;;
	project|project_check)
		if [[ -f "$project/xsdk-project.json" ]]; then
			[[ ${#extra[@]} == 0 ]] || { echo 'Port recipes use their own build configuration, not extra CMake arguments' >&2; exit 1; }
			check=()
			[[ "${XSDK_RESTORE_INPUTS:-0}" != 1 ]] || check+=(--restore-inputs)
			[[ "$action" != project_check ]] || check+=(--check-only)
			python3 tools/windows/project.py "$(cygpath -m "$project")" \
				--sdk "$(cygpath -m "$sdk")" --compiler "$(cygpath -m "$prefix")" \
				--msys "$(cygpath -m /)" --work "$(cygpath -m "$work")" \
				--sdl "${sdl:+$(cygpath -m "$sdl")}" --rom "${XSDK_PROJECT_ROM:-}" \
				--jobs "$jobs" --build-type "$build_type" "${check[@]}"
			exit 0
		fi
		[[ "$action" != project_check ]] || { echo 'Choose a port root containing xsdk-project.json' >&2; exit 1; }
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
case "$action" in
	toolchain|toolchain_fresh) python3 tools/windows/manager.py mark "$sdk" "$prefix" "$work" toolchain "$toolchain_work" ;;
	shaders|sdk) python3 tools/windows/manager.py mark "$sdk" "$prefix" "$work" "$action" ;;
esac
echo "Completed: $action"
