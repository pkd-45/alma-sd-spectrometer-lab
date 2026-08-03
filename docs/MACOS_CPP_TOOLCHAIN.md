# macOS C++ toolchain

The repository supports both AppleClang and Homebrew GCC.

## AppleClang

The preflight resolves both `clang++` and the macOS SDK through `xcrun`.
CMake receives the same compiler and SDK root:

```bash
unset ALMA_CXX
make cpp
```

## Homebrew GCC fallback

```bash
brew install gcc
GXX="$(find "$(brew --prefix gcc)/bin" -maxdepth 1 -type f -name 'g++-*' | head -1)"
ALMA_CXX="$GXX" make cpp
```

Using the GCC fallback does not modify the system compiler.
