#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
KERNEL_NAME="clean-air-agent"
KERNEL_DISPLAY_NAME="Clean Air Agent (.venv)"

cd "${PROJECT_ROOT}"

if [[ "${1:-}" != "" ]]; then
  PYTHON_BIN="$1"
elif command -v python3.14 >/dev/null 2>&1; then
  PYTHON_BIN="python3.14"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Could not find python3.14 or python3 on PATH." >&2
  exit 1
fi

echo "Using Python: $(${PYTHON_BIN} -c 'import sys; print(sys.executable)')"
TARGET_VERSION="$("${PYTHON_BIN}" -c 'import platform; print(platform.python_version())')"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Creating virtual environment at ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
else
  CURRENT_VERSION="$("${VENV_DIR}/bin/python" -c 'import platform; print(platform.python_version())' 2>/dev/null || true)"
  if [[ "${CURRENT_VERSION}" != "${TARGET_VERSION}" ]]; then
    echo "Recreating virtual environment at ${VENV_DIR} (${CURRENT_VERSION:-unknown} -> ${TARGET_VERSION})"
    "${PYTHON_BIN}" -m venv --clear "${VENV_DIR}"
  else
    echo "Using existing virtual environment at ${VENV_DIR}"
  fi
fi

VENV_PYTHON="${VENV_DIR}/bin/python"

echo "Ensuring pip is available in the virtual environment"
"${VENV_PYTHON}" -m ensurepip --upgrade

echo "Upgrading packaging tools"
"${VENV_PYTHON}" -m pip install --upgrade pip setuptools wheel

echo "Installing project dependencies"
"${VENV_PYTHON}" -m pip install -r requirements.txt

echo "Registering Jupyter kernel: ${KERNEL_DISPLAY_NAME}"
"${VENV_PYTHON}" -m ipykernel install \
  --user \
  --name "${KERNEL_NAME}" \
  --display-name "${KERNEL_DISPLAY_NAME}"

cat <<EOF

Setup complete.

Use this interpreter:
  ${VENV_PYTHON}

In VS Code / Jupyter, select this kernel:
  ${KERNEL_DISPLAY_NAME}

Run tests with:
  ${VENV_PYTHON} -m pytest -q
EOF
