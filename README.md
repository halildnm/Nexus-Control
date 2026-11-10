# Nexus Control

**Turn your iPad into a Linux desktop control panel.**

Nexus Control is a Linux desktop companion that transforms your iPad into a remote control center for your computer.

## Features

- Real-time CPU, RAM and disk monitoring
- Niri workspace management
- Media playback controls
- Audio volume management
- Remote access from iPad
- Token-based API authentication
- Desktop management application
- System tray integration
- Dux Shell 2.0 widget

## Download

Download the latest release and distribution packages:

[**Nexus Control – GitHub Releases**](https://github.com/halildnm/Nexus-Control/releases/latest)

## Installation

Choose the instructions for your Linux distribution. The prebuilt packages in release v0.3.4 are for **x86_64 / amd64** systems.

### Arch Linux

The Arch package is built from the official Git repository. Install the build tools, clone the repository, and build/install the package:

```bash
sudo pacman -S --needed git base-devel
git clone https://github.com/halildnm/Nexus-Control.git
cd Nexus-Control/packaging/arch
makepkg -si
```

When prompted, review and confirm the package installation. `makepkg -si` installs the dependencies declared by the package as well.

**Note:** AUR publication is not available yet. Until the package is published to AUR, use the build-from-source instructions above.

### Debian / Ubuntu

1. Open the [latest Releases page](https://github.com/halildnm/Nexus-Control/releases/latest).
2. Download the file named `nexus-control_<version>-1_amd64.deb`.
3. Open a terminal in the download folder and run:

```bash
sudo apt install ./nexus-control_*_amd64.deb
```

If APT reports missing dependencies, run:

```bash
sudo apt --fix-broken install
```

### Fedora

1. Open the [latest Releases page](https://github.com/halildnm/Nexus-Control/releases/latest).
2. Download the `.rpm` file for your release and architecture.
3. Open a terminal in the download folder and run:

```bash
sudo dnf install ./nexus-control-*.rpm
```

### Other Linux distributions

There is currently no official package for openSUSE, NixOS, Alpine, or other distributions. Do not install the Debian or Fedora package on a different distribution. Check the [release page](https://github.com/halildnm/Nexus-Control/releases/latest) for newly supported formats.

**Flatpak is not available yet.** It will be listed here after the sandbox permissions, dependencies, and real installation/runtime tests are complete.

## Starting the application

After installation, find **Nexus Control** in your desktop application menu. You can also start it from a terminal:

```bash
nexus-control-desktop
```

The desktop application lets you start/stop the local server, configure its port and access token, and open the control panel.

## iPad Connection

1. Connect your iPad and Linux computer to the same Wi-Fi network.
2. Start Nexus Control on the computer and start its server.
3. Note the iPad connection address shown in the desktop application.
4. Open that address in Safari on your iPad and use the configured access token when prompted.

## Desktop Integration

### Niri

- Desktop application launcher
- System tray integration through a compatible tray host
- Workspace controls (requires Niri)

### Dux Shell 2.0

- Dedicated Nexus Control widget
- Connection status
- CPU usage indicator
- Quick access to the dashboard

## Technologies

- Python
- FastAPI
- PySide6
- Linux
- Niri
- Dux Shell

## Security

Nexus Control uses token-based authentication.

Only use the application on trusted local networks. Do not expose the service directly to the public internet. Keep your access token private.

## Support and downloads

- [GitHub Releases](https://github.com/halildnm/Nexus-Control/releases)
- [Report a bug or request a feature](https://github.com/halildnm/Nexus-Control/issues)

## Developer

Created by [halildnm](https://github.com/halildnm)

## License

Nexus Control is licensed under the **GNU General Public License v3.0 only (GPL-3.0-only)**. See [LICENSE](LICENSE).
