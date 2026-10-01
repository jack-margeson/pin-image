# pin-image

Pin an image to the desktop (scroll to zoom, drag to move).

Liked the feature from Flameshot, wanted the functionality when using Spectacle (KDE Plasma's built-in screenshot tool)

## Install:
- `sudo chmod +x ./install.sh`
- `./install.sh`
Drops a desktop entry in `~/.local/share/applications` to register it as a program.

## Usage:
- Highlight a region for a screenshot with Spectacle (or other screenshot tool)
- Export tab > "Other Application..."
- Choose "Pin Image"
- Image will be pinned to the desktop. Use M1 to move, scroll wheel to zoom, Ctrl + scroll wheel to change opacity (10%–100%)
- M2 brings up the context menu to reset zoom/opacity or close the pinned image
- "Pin Image" will appear under Export option for future screenshots
  