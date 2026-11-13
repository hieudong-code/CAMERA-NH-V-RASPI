#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="$(command -v "${PYTHON:-python3}")"
case "$PYTHON" in /*) ;; *) PYTHON="$PWD/$PYTHON" ;; esac
"$PYTHON" -m unittest discover -s software/tests -v
(cd simulation && "$PYTHON" -m unittest -v test_simulation test_controller_integration)
"$PYTHON" cad/kiemtra_mesh.py
bash cad/kiemtra_render.sh
(cd voice && "$PYTHON" -m unittest -v test_voice_chat)
