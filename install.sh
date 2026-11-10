#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(command -v python3 || true)"
if [[ -z "$PYTHON" ]]; then
  zenity --error --text="Python 3 bulunamadı. Dağıtımınızın paket yöneticisinden Python 3 kurun." 2>/dev/null || true
  exit 1
fi

if command -v pacman >/dev/null 2>&1; then
  if ! "$PYTHON" -c 'import PySide6' >/dev/null 2>&1; then
    if command -v pkexec >/dev/null 2>&1; then
      pkexec pacman -S --needed --noconfirm pyside6 python-pip playerctl wireplumber
    else
      zenity --error --text="PySide6 kurulumu için pkexec bulunamadı. python-pyside6 paketini kurup tekrar deneyin." 2>/dev/null || true
      exit 1
    fi
  fi
fi

VENV="$HOME/.local/share/nexus-control/venv"
mkdir -p "$(dirname "$VENV")" "$HOME/.local/bin" "$HOME/.local/share/applications"
"$PYTHON" -m venv --system-site-packages "$VENV"
"$VENV/bin/pip" install --upgrade pip
if ! "$VENV/bin/python" -c 'import PySide6' >/dev/null 2>&1; then
  "$VENV/bin/pip" install "PySide6>=6.7"
fi
"$VENV/bin/pip" install -e "$ROOT"

cat > "$HOME/.local/bin/nexus-control-desktop" <<EOF
#!/usr/bin/env bash
cd "$ROOT"
exec "$VENV/bin/python" -m app.desktop "\$@"
EOF
chmod +x "$HOME/.local/bin/nexus-control-desktop"

sed "s|Exec=nexus-control-desktop|Exec=$HOME/.local/bin/nexus-control-desktop|" \
  "$ROOT/integrations/niri/nexus-control.desktop" \
  > "$HOME/.local/share/applications/nexus-control.desktop"

if [[ -d "$HOME/.config/dms/plugins" ]]; then
  mkdir -p "$HOME/.config/dms/plugins"
  rm -rf "$HOME/.config/dms/plugins/NexusControl"
  cp -r "$ROOT/integrations/dux-nexus" "$HOME/.config/dms/plugins/NexusControl"
  if command -v dms >/dev/null 2>&1; then
    dms ipc call plugins reload nexusControl >/dev/null 2>&1 || true
  fi
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi

zenity --info --title="Nexus Control" --text="Kurulum tamamlandı.\n\nUygulama menüsünden Nexus Control'ü açabilirsiniz.\nDux eklentisi kurulduysa Dux Ayarlar → Plugins bölümünden etkinleştirin." 2>/dev/null || true
