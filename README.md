# ArchDeck

A desktop control center for Arch Linux. The first scaffold focuses on a readable system overview, update checks, and user service status. It does not install, remove, or modify anything yet.

## Install on Arch Linux

```sh
sudo pacman -S pyside6
./run.sh
```

The project-local `.venv` uses system site packages so it can use PySide6 installed from the Arch repository. No Python package is fetched from PyPI.

## Current screens

- **Overview** — CPU, memory, root filesystem, and shortcuts.
- **Updates** — checks available repository updates with `checkupdates` when requested.
- **Services** — lists active user services when requested.
- **Packages** — browse, search, and inspect installed packages. **System** — read-only host, kernel, processor, memory, storage, and uptime details. **Cleanup** — navigation scaffold for follow-up work.

All external commands are started only after an explicit button press. No privileged command is run by ArchDeck.
