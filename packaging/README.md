# Distribution packaging

Target: Nexus Control 0.3.4, GPL-3.0-only, x86_64.

- arch/: Arch Linux PKGBUILD using the tagged Git source; package builds are checked by GitHub Actions.
- fedora/: RPM spec template.
- debian/: Debian/Ubuntu source package skeleton.
- flatpak/: initial manifest scaffold; not Flathub-ready yet.
- shared/: desktop entry.

Before AUR submission:
1. Verify the PKGBUILD and generated .SRCINFO with makepkg in a clean Arch environment.
2. Confirm the package builds and installs on a current Arch Linux system.
3. Review the package dependencies against the current Arch repositories.
4. AUR publishing requires an AUR account and SSH key.

The Arch PKGBUILD uses the v${pkgver} Git tag directly, so it does not depend on a separately uploaded release tarball. Its VCS source checksum is intentionally SKIP; makepkg verifies the checked-out tag through Git rather than a fixed archive checksum.

Flatpak is not ready for publication. FastAPI, Uvicorn, psutil, PySide6 and their transitive dependencies still need a pinned, offline-compatible dependency build, followed by a successful Flatpak build and runtime test.

Debian PySide6 package availability differs by release. Verify dependencies on each supported Ubuntu/Debian version. Fedora package names also need validation on the target Fedora release. Do not claim target support until built and tested.
