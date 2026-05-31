#!/usr/bin/env bash
set -e

echo "Python version check..."
python --version

# Ensure we're using the right Python
if ! python --version | grep -q "3.10"; then
    echo "ERROR: Wrong Python version detected!"
    python --version
    exit 1
fi

echo "Setting up Cargo for writable directory..."
export CARGO_HOME=/tmp/cargo
export CARGO_TARGET_DIR=/tmp/cargo-target

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo "Build completed successfully!"