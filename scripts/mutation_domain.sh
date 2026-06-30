#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

session="mutation.sqlite"
report="MUTATION-REPORT.txt"

cosmic-ray init --force cosmic-ray.toml "$session"
cosmic-ray exec cosmic-ray.toml "$session"
cr-report "$session" | tee "$report"
