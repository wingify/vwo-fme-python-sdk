#!/usr/bin/env bash
# Copyright 2024-2026 Wingify Software Pvt. Ltd.
#
# Tag the current version, build both brand sdists, and upload to PyPI.
# Skips if the tag already exists (safe for docs-only merges).
#
# Usage (CI — called by GitHub Actions):
#   ./scripts/release.sh
#
# Usage (local dry-run, no upload, no tag push):
#   DRY_RUN=1 ./scripts/release.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION=$(python3 setup.py --version)
TAG="v${VERSION}"
DRY_RUN="${DRY_RUN:-0}"

echo "=== Version: ${VERSION} / Tag: ${TAG} ==="

# Skip if this version was already tagged on origin (e.g. docs-only merge after a release)
if git ls-remote --tags origin "${TAG}" | grep -q "refs/tags/${TAG}$"; then
  echo "Tag ${TAG} already exists on origin. Skipping release."
  exit 0
fi

# ---- Build first, tag and upload only after both sdists succeed ----

# Build both brand sdists
./scripts/build_wheels.sh

VWO_TARBALL="dist/vwo_fme_python_sdk-${VERSION}.tar.gz"
WINGIFY_TARBALL="dist/wingify_fme_python_sdk-${VERSION}.tar.gz"

if [ ! -f "${VWO_TARBALL}" ] || [ ! -f "${WINGIFY_TARBALL}" ]; then
  echo "ERROR: Expected tarballs not found:"
  ls -la dist/
  exit 1
fi

if [ "${DRY_RUN}" = "1" ]; then
  echo "=== DRY_RUN: skipping tag push and twine upload ==="
  echo "Would upload:"
  echo "  ${VWO_TARBALL}"
  echo "  ${WINGIFY_TARBALL}"
else
  # Upload to PyPI first — if this fails, no tag is pushed so re-run is safe
  echo "=== Uploading to PyPI ==="
  twine upload "${VWO_TARBALL}" "${WINGIFY_TARBALL}"

  # Tag only after successful upload
  if [ -n "${CI:-}" ]; then
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
  fi

  # Delete stale local tag if it exists (e.g. from a previous failed attempt)
  if git tag -l "${TAG}" | grep -q "${TAG}"; then
    echo "Removing stale local tag ${TAG}"
    git tag -d "${TAG}"
  fi

  git tag -a "${TAG}" -m "Release ${VERSION}"
  git push origin "${TAG}"
  echo "=== Pushed tag ${TAG} ==="
fi

# Clean up build artifacts
rm -rf dist/ build/ *.egg-info 2>/dev/null || true

echo "=== Release ${VERSION} done ==="
