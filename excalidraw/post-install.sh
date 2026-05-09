#!/bin/sh
# `cryptography` is required by upload.py for AES-GCM client-side
# encryption of diagrams before upload to excalidraw.com.
set -eu

pip3 install --no-cache-dir --break-system-packages cryptography
