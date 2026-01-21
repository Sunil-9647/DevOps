#!/usr/bin/env bash
set -euo pipefail

echo "Build started..."

# Clean previous output (deterministic build)
rm -rf dist
mkdir -p dist

# Create build output (simulate real build)
echo "Hello from CI build output" > dist/app.txt

# Add build metadata (versioning concept)
echo "BUILD_COMMIT=${GITHUB_SHA:-local}" > dist/version.txt
echo "BUILD_TIME_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> dist/version.txt

echo "Build completed. Output created in dist/"
ls -l dist

