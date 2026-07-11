#!/usr/bin/env bash
# Checks that everyone needs before running this demo. Run this right
# after cloning — it tells you exactly what's missing, no guessing.
set -uo pipefail

PASS=0
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  local hint="$3"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "  OK   $name"
    PASS=$((PASS + 1))
  else
    echo "  MISSING  $name  ->  $hint"
    FAIL=$((FAIL + 1))
  fi
}

echo "Checking required tools..."
check "python3"        "command -v python3"        "install from https://www.python.org/downloads/"
check "docker CLI"      "command -v docker"          "install Docker Desktop, or 'brew install colima docker docker-compose' on macOS"
check "docker daemon"    "docker info"                 "start Docker Desktop, or run 'colima start'"
check "docker-compose"    "command -v docker-compose || docker compose version" "install docker-compose, or use a Docker Desktop version that bundles it"

echo
echo "Checking Kubernetes tools (only needed for docs/04 onward)..."
check "kubectl"    "command -v kubectl"    "brew install kubectl  (or see https://kubernetes.io/docs/tasks/tools/)"
check "kind"        "command -v kind"        "brew install kind  (or see https://kind.sigs.k8s.io/docs/user/quick-start/#installation)"

echo
echo "$PASS OK, $FAIL missing."
if [ "$FAIL" -gt 0 ]; then
  echo "Fix the MISSING items above before continuing. Docker items are required for docs/01-03; kubectl/kind only for docs/04 onward."
  exit 1
fi
echo "All set — start at docs/01-train-models.md"
