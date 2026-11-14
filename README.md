# ArchDeck

A desktop control center for Arch Linux with system overview, update checks, package browsing, user service status, and cleanup inspection. It does not install, remove, or modify anything yet.

## Install on Arch Linux

```sh
sudo pacman -S pyside6
./run.sh
```

The project-local `.venv` uses system site packages so it can use PySide6 installed from the Arch repository. No Python package is fetched from PyPI.

## Current screens

- **Overview** — CPU, memory, root filesystem, and shortcuts.
- **Updates** — checks official repository updates with `checkupdates` when available, or the local pacman database otherwise; checks AUR updates with `yay` when installed. Shows installed and available versions. Checks start only when requested.
- **Services** — lists active user services when requested.
- **Packages** — browse, search, and inspect installed packages.
- **System** — read-only host, kernel, processor, memory, storage, and uptime details.
- **Cleanup** — inspect the size of files in the pacman cache and orphaned packages; removal is not available.

All external commands are started only after an explicit button press. No privileged command is run by ArchDeck.
