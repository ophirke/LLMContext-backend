#!/usr/bin/env bash

# if .venv doesnt exist, create it
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# activate the virtual environment
source .venv/bin/activate

# install the requirements
pip install -r requirements.txt

# Define platform-specific variables for the wheel files
declare -A wheels
wheels[macos]="intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-macosx_10_9_universal2.whl"
wheels[linux_x86_64]="intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
wheels[linux_aarch64]="intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"
wheels[win32]="intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-win32.whl"
wheels[win_amd64]="intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-win_amd64.whl"

# Determine the required wheel based on the platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    platform="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [[ $(uname -m) == "x86_64" ]]; then
        platform="linux_x86_64"
    elif [[ $(uname -m) == "aarch64" ]]; then
        platform="linux_aarch64"
    fi
elif [[ "$OSTYPE" == "msys" ]]; then
    if [[ $(uname -m) == "x86_64" ]]; then
        platform="win_amd64"
    elif [[ $(uname -m) == "i686" ]]; then
        platform="win32"
    fi
fi

# Install the wheel file
if [[ -n "$platform" ]]; then
    echo "Detected platform: $platform"
    echo "Installing wheel file: ${wheels[$platform]}"
    pip install "./install/${wheels[$platform]}"
else
    echo "Unsupported platform: $OSTYPE"
    exit 1
fi