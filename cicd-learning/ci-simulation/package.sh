#!/usr/bin/env bash
set -euo pipefail

echo "Packaging started..."

# Ensure build output exists
test -d dist || { echo "ERROR: dist/ not found. Run build first."; exit 1; }

# Prepare artifact folder
mkdir -p ci-artifacts

# Versioned artifact name using commit SHA if available
SHA="${GITHUB_SHA:-local}"
ARTIFACT_NAME="app-build-${SHA}.zip"

# Create zip
zip -r "ci-artifacts/${ARTIFACT_NAME}" dist >/dev/null

echo "Packaging completed: ci-artifacts/${ARTIFACT_NAME}"
ls -l ci-artifacts
