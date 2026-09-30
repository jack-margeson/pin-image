#!/bin/sh
# Installs pin-image for the current user (no root needed).
set -e
cd "$(dirname "$0")"
mkdir -p ~/.local/bin ~/.local/share/applications
install -m 755 pin-image.py ~/.local/bin/pin-image
sed "s|^Exec=pin-image|Exec=$HOME/.local/bin/pin-image|" pin-image.desktop \
    > ~/.local/share/applications/pin-image.desktop
update-desktop-database ~/.local/share/applications 2>/dev/null || true
echo "Installed: ~/.local/bin/pin-image"
