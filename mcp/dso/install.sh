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
venv_dir="$(cd -- "$venv_dir" && pwd)"
printf 'Installed DSO dependencies, scanners and the dso command in %s\n' "$venv_dir"
printf 'Run it directly: %s/bin/dso doctor\n' "$venv_dir"
printf 'Or put only dso on PATH: ln -s "%s/bin/dso" ~/.local/bin/dso\n' "$venv_dir"
