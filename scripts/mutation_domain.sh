#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

run_mutation() {
  label="$1"
  config="$2"
  session="$3"

  printf '\n== %s ==\n' "$label"
  cosmic-ray init --force "$config" "$session"
  cosmic-ray exec "$config" "$session"
  cr-report "$session"
}

run_mutation "amounts.py" "cosmic-ray.toml" "mutation-amounts.sqlite"
run_mutation "refunds.py" "cosmic-ray-refunds.toml" "mutation-refunds.sqlite"
run_mutation "auth.py" "cosmic-ray-auth.toml" "mutation-auth.sqlite"
run_mutation "api.py" "cosmic-ray-api.toml" "mutation-api.sqlite"
