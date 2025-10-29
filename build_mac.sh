#!/usr/bin/env bash
# build_mac.sh
# Helper script to build POsaver on macOS and ensure data files are included
# Usage: ./build_mac.sh [--spec]

set -euo pipefail

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$REPO_DIR"

PYTHON=${PYTHON:-python3}

echo "Using Python: $PYTHON"

if [ "$1" = "--spec" ] 2>/dev/null; then
  if [ -f POsaver.spec ]; then
    echo "Building with existing POsaver.spec"
    $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install pyinstaller
    $PYTHON -m PyInstaller --clean --noconfirm POsaver.spec
  else
    echo "POsaver.spec not found; falling back to CLI build"
  fi
fi

if [ ! -f POsaver.spec ]; then
  echo "Building with CLI and ensuring data files are included (using ':' separator on macOS)"
  $PYTHON -m pip install --upgrade pip
  $PYTHON -m pip install pyinstaller

  # On macOS, PyInstaller add-data separator is ':' (not ';').
  # We'll create a one-dir build and then package as .app if desired.
  $PYTHON -m PyInstaller --clean --noconfirm --onedir \
    --add-data "share.png:." \
    --add-data "layout.css:." \
    --name POsaver POsaver.py
fi

echo "Collecting output from dist/"
mkdir -p release_artifacts

if [ -d dist/POsaver.app ]; then
  echo "Found POsaver.app - packaging as zip"
  cp -R dist/POsaver.app release_artifacts/
  (cd release_artifacts && zip -r ../POsaver-macos-artifacts.zip POsaver.app)
elif [ -d dist/POsaver ]; then
  echo "Found onedir dist/POsaver - wrapping as .app-like folder"
  cp -R dist/POsaver release_artifacts/POsaver.app || true
  (cd release_artifacts && zip -r ../POsaver-macos-artifacts.zip POsaver.app)
else
  echo "No dist output found; listing dist for debugging:" && ls -la dist || true
fi

echo "Mac build complete. Artifact: POsaver-macos-artifacts.zip (if created)"
