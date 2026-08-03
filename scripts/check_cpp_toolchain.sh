#!/usr/bin/env bash
set -Eeuo pipefail

mode="check"
case "${1:-}" in
  --print-compiler) mode="compiler" ;;
  --print-sdkroot) mode="sdkroot" ;;
  "") ;;
  *) echo "ERROR: unsupported argument: $1" >&2; exit 2 ;;
esac

compiler=""
sdkroot=""
use_xcrun=false

# An explicit compiler always wins. This is useful for Homebrew GCC:
#   ALMA_CXX="$(brew --prefix gcc)/bin/g++-16" make cpp
if [[ -n "${ALMA_CXX:-}" ]]; then
  compiler="$ALMA_CXX"
  [[ -x "$compiler" ]] || {
    echo "ERROR: ALMA_CXX is not executable: $compiler" >&2
    exit 2
  }
elif [[ "$(uname -s)" == "Darwin" ]]; then
  command -v xcrun >/dev/null 2>&1 || {
    echo "ERROR: xcrun is unavailable. Run: xcode-select --install" >&2
    exit 2
  }

  compiler="$(xcrun --sdk macosx --find clang++ 2>/dev/null || true)"
  sdkroot="$(xcrun --sdk macosx --show-sdk-path 2>/dev/null || true)"
  [[ -n "$compiler" && -x "$compiler" ]] || {
    echo "ERROR: Apple clang++ is unavailable through xcrun." >&2
    exit 2
  }
  [[ -n "$sdkroot" && -d "$sdkroot" ]] || {
    echo "ERROR: the macOS SDK could not be resolved through xcrun." >&2
    exit 2
  }
  use_xcrun=true
else
  compiler="$(command -v c++ || command -v g++ || command -v clang++ || true)"
  [[ -n "$compiler" ]] || {
    echo "ERROR: no C++ compiler was found." >&2
    exit 2
  }
fi

case "$mode" in
  compiler)
    printf '%s\n' "$compiler"
    exit 0
    ;;
  sdkroot)
    printf '%s\n' "$sdkroot"
    exit 0
    ;;
esac

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
cat > "$tmpdir/probe.cpp" <<'CPP'
#include <algorithm>
#include <complex>
#include <iostream>
#include <vector>
int main() {
    std::vector<int> values{3, 1, 2};
    std::sort(values.begin(), values.end());
    std::cout << values.front() << "\n";
    return 0;
}
CPP

if $use_xcrun; then
  compile=(xcrun --sdk macosx clang++ -isysroot "$sdkroot")
else
  compile=("$compiler")
fi

if ! "${compile[@]}" -std=c++17 "$tmpdir/probe.cpp" -o "$tmpdir/probe" \
    2>"$tmpdir/error.log"; then
  echo "ERROR: the selected C++ compiler cannot compile standard-library headers." >&2
  echo "Compiler: $compiler" >&2
  [[ -n "$sdkroot" ]] && echo "SDK root: $sdkroot" >&2
  cat "$tmpdir/error.log" >&2
  if [[ "$(uname -s)" == "Darwin" && -z "${ALMA_CXX:-}" ]]; then
    cat >&2 <<'MSG'

This is a macOS developer-tool configuration problem, not an error in
fft_reference.cpp.

Supported fallback:
  brew install gcc
  GXX="$(find "$(brew --prefix gcc)/bin" -maxdepth 1 -type f -name 'g++-*' | head -1)"
  ALMA_CXX="$GXX" make cpp
MSG
  fi
  exit 2
fi

"$tmpdir/probe" >/dev/null
if [[ -n "$sdkroot" ]]; then
  printf 'C++17 toolchain preflight: PASS (%s; SDK %s)\n' "$compiler" "$sdkroot"
else
  printf 'C++17 toolchain preflight: PASS (%s)\n' "$compiler"
fi
