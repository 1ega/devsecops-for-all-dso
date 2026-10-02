#!/usr/bin/env bash
# Installs only into the specified private virtual environment; no sudo needed.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
venv_dir="${1:-$script_dir/.venv}"
python_bin="${PYTHON:-python3}"
"$python_bin" -c 'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,14) else "DSO requires Python 3.10–3.14")' 
"$python_bin" -m venv "$venv_dir"
"$venv_dir/bin/python" -m pip install --require-hashes -r "$script_dir/requirements-standalone.lock"
"$venv_dir/bin/python" "$script_dir/install_scanners.py" --bin-dir "$venv_dir/bin"
printf 'Installed DSO dependencies and scanners in %s\n' "$venv_dir"
printf 'Activate with: source "%s/bin/activate"\n' "$venv_dir"
