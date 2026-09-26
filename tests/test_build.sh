#!/usr/bin/env bash
# Loop FULL_TEST gate = Fast source checks only. No fresh runtime/24k/144k claim.
set -euo pipefail
cd "$(dirname "$0")/.."
printf 'GATE_SCOPE=fast; runtime=NOT_RUN; multiplayer=NOT_RUN\n'
make check
