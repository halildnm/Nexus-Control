# Flatpak packaging status

This is an initial local-build scaffold, not ready for Flathub submission.
The application needs FastAPI, Uvicorn, psutil and PySide6. Flathub builds
cannot access the network during build, so all Python dependencies and their
transitive dependencies must be pinned and vendored as manifest sources.
The KDE runtime branch and availability of PySide6 must also be verified.
Do not publish this manifest as a working Flathub package until those steps
and a real Flatpak build have succeeded.
