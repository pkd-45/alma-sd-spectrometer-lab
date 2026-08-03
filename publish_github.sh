#!/bin/bash
set -euo pipefail

REPO="pkd-45/alma-sd-spectrometer-lab"
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "GitHub CLI (gh) is required" >&2; exit 1; }
gh auth status

if [[ ! -d .git ]]; then
  git init -b main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Add ALMA JD1/JD2 software demonstrator"
fi

if gh repo view "$REPO" >/dev/null 2>&1; then
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/${REPO}.git"
  git push -u origin main
else
  gh repo create "$REPO" --public --source=. --remote=origin --push \
    --description "Synthetic ALMA single-dish processing and spectrometer-control demonstrator"
fi

echo "Published: https://github.com/${REPO}"
