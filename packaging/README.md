# Distribution packaging

Target: Nexus Control 0.3.4, GPL-3.0-only, x86_64.

- arch/: AUR PKGBUILD template.
- fedora/: RPM spec template.
- debian/: Debian/Ubuntu source package skeleton.
- flatpak/: initial manifest scaffold; not Flathub-ready yet.
- shared/: desktop entry.

Before AUR submission:
1. Publish release asset nexus-control-0.3.4.tar.gz under tag v0.3.4.
2. Update PKGBUILD and .SRCINFO SHA256 checksums to the final source archive.
3. Verify package names, build with makepkg, and test in a clean Arch environment.
4. AUR publishing requires an AUR account and SSH key.

Debian PySide6 package availability differs by release. Verify dependencies on
each supported Ubuntu/Debian version. Fedora package names also need validation
on the target Fedora release. Do not claim target support until built and tested.
