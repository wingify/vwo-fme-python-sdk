#!/usr/bin/env bash
# Copyright 2024-2026 Wingify Software Pvt. Ltd.
#
# Build both brand-specific source distributions from the same codebase.
#
# Usage:
#   ./scripts/build_wheels.sh
#
# Outputs:
#   dist/vwo-fme-python-sdk-<version>.tar.gz
#   dist/wingify-fme-python-sdk-<version>.tar.gz

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf dist/ build/ *.egg-info wingify.egg-info vwo.egg-info 2>/dev/null || true

echo "=== Building VWO source distribution ==="
SDK_BRAND=vwo python3 setup.py sdist

echo "=== Building Wingify source distribution ==="
SDK_BRAND=wingify python3 setup.py sdist

echo "=== Done ==="
ls -la dist/
