Name:           nexus-control
Version:        0.3.4
Release:        1%{?dist}
Summary:        Linux desktop companion and iPad control dashboard
License:        GPL-3.0-only
URL:            https://github.com/halildnm/Nexus-Control
Source0:        %{url}/releases/download/v%{version}/nexus-control-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3
Requires:       python3-fastapi
Requires:       python3-uvicorn
Requires:       python3-psutil
Requires:       python3-pyside6
Recommends:     playerctl
Recommends:     wireplumber
Recommends:     niri

%description
Nexus Control provides an iPad dashboard and desktop companion for Linux.

%prep
%autosetup -n nexus-control-%{version}

%build
:

%install
install -d %{buildroot}%{_libdir}/nexus-control
cp -a app %{buildroot}%{_libdir}/nexus-control/
install -Dpm 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE
install -Dpm 0644 README.md %{buildroot}%{_docdir}/%{name}/README.md
install -Dpm 0644 packaging/shared/nexus-control.desktop %{buildroot}%{_datadir}/applications/nexus-control.desktop
install -d %{buildroot}%{_datadir}/nexus-control/integrations
cp -a integrations/dux-nexus %{buildroot}%{_datadir}/nexus-control/integrations/
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/nexus-control-desktop <<'EOF'
#!/bin/sh
export PYTHONPATH="%{_libdir}/nexus-control${PYTHONPATH:+:$PYTHONPATH}"
exec /usr/bin/python3 -m app.desktop "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/nexus-control-desktop

%files
%{_bindir}/nexus-control-desktop
%{_libdir}/nexus-control/
%{_datadir}/applications/nexus-control.desktop
%{_datadir}/nexus-control/
%{_licensedir}/%{name}/LICENSE
%{_docdir}/%{name}/README.md

%changelog
* Tue Nov 10 2026 halildnm <halildnm@users.noreply.github.com> - 0.3.4-1
- Initial Fedora package
