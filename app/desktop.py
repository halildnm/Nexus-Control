from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QCheckBox, QGroupBox,
    QFormLayout, QMessageBox, QSystemTrayIcon, QMenu, QStyle
)

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "nexus-control"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "nexus-control"
LOG_FILE = LOG_DIR / "server.log"


def load_config():
    try:
        data = json.loads(CONFIG_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        data = {}
    data.setdefault("host", "0.0.0.0")
    data.setdefault("port", 8765)
    data.setdefault("token", secrets.token_urlsafe(32))
    data.setdefault("open_on_start", False)
    return data


class NexusWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.server = None
        self.setWindowTitle("Nexus Control")
        self.setMinimumSize(480, 460)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        heading = QLabel("NEXUS CONTROL")
        heading.setStyleSheet("font-size:23px;font-weight:800;letter-spacing:2px")
        subtitle = QLabel("iPad kontrol panelini masaüstünden yönet")
        subtitle.setStyleSheet("color:#a4a6bc")
        layout.addWidget(heading)
        layout.addWidget(subtitle)

        self.status = QLabel("● Sunucu kontrol ediliyor…")
        self.status.setStyleSheet("font-size:14px;font-weight:700;color:#e8c58e")
        layout.addWidget(self.status)

        server_box = QGroupBox("Sunucu ayarları")
        form = QFormLayout(server_box)
        self.host = QLineEdit(self.cfg["host"])
        self.port = QSpinBox()
        self.port.setRange(1024, 65535)
        self.port.setValue(int(self.cfg["port"]))
        self.token = QLineEdit(self.cfg["token"])
        self.token.setEchoMode(QLineEdit.Password)
        self.token.setMinimumWidth(250)
        self.show_token = QCheckBox("Erişim anahtarını göster")
        self.show_token.toggled.connect(
            lambda checked: self.token.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        form.addRow("Dinleme adresi", self.host)
        form.addRow("Port", self.port)
        form.addRow("Erişim anahtarı", self.token)
        form.addRow("", self.show_token)
        layout.addWidget(server_box)

        self.url_label = QLabel()
        self.url_label.setTextInteractionFlags(
            self.url_label.textInteractionFlags() | self.url_label.textInteractionFlags()
        )
        self.url_label.setWordWrap(True)
        self.url_label.setStyleSheet("color:#c4b8ff;padding:8px")
        layout.addWidget(self.url_label)

        buttons = QHBoxLayout()
        self.start_btn = QPushButton("▶  Sunucuyu başlat")
        self.stop_btn = QPushButton("■  Durdur")
        self.open_btn = QPushButton("↗  Paneli aç")
        buttons.addWidget(self.start_btn)
        buttons.addWidget(self.stop_btn)
        buttons.addWidget(self.open_btn)
        layout.addLayout(buttons)

        self.save_btn = QPushButton("Ayarları kaydet")
        self.save_btn.clicked.connect(self.save_config)
        layout.addWidget(self.save_btn)

        note = QLabel(
            "iPad ve bilgisayar aynı Wi-Fi ağına bağlı olmalı. "
            "Erişim anahtarını yalnızca güvendiğin cihazlarla paylaş."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#9297ad;font-size:11px")
        layout.addWidget(note)
        layout.addStretch(1)
        self.setCentralWidget(central)

        self.start_btn.clicked.connect(self.start_server)
        self.stop_btn.clicked.connect(self.stop_server)
        self.open_btn.clicked.connect(self.open_panel)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray.setToolTip("Nexus Control")
        menu = QMenu()
        show_action = QAction("Nexus Control'ü aç", self)
        show_action.triggered.connect(self.showNormal)
        start_action = QAction("Sunucuyu başlat", self)
        start_action.triggered.connect(self.start_server)
        stop_action = QAction("Sunucuyu durdur", self)
        stop_action.triggered.connect(self.stop_server)
        open_action = QAction("iPad panelini aç", self)
        open_action.triggered.connect(self.open_panel)
        quit_action = QAction("Tamamen çıkış", self)
        quit_action.triggered.connect(self.quit_app)
        for action in (show_action, start_action, stop_action, open_action):
            menu.addAction(action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(2500)
        self.refresh_status()
        if self.cfg.get("open_on_start"):
            self.start_server()

        self.setStyleSheet("""
            QMainWindow,QWidget { background:#171923; color:#f0effb; font-family:Inter,sans-serif; }
            QGroupBox { border:1px solid #41445a; border-radius:12px; margin-top:12px; padding:14px; font-weight:700; }
            QGroupBox::title { subcontrol-origin:margin; left:12px; padding:0 5px; color:#c4b8ff; }
            QLineEdit,QSpinBox { background:#242838; border:1px solid #484b62; border-radius:8px; padding:8px; color:#fff; }
            QPushButton { background:#34364b; border:1px solid #55536f; border-radius:9px; padding:10px 12px; }
            QPushButton:hover { background:#484361; }
            QPushButton:pressed { background:#62578f; }
        """)

    def save_config(self):
        token = self.token.text().strip()
        if not token:
            QMessageBox.warning(self, "Eksik bilgi", "Erişim anahtarı boş olamaz.")
            return
        self.cfg.update({
            "host": self.host.text().strip() or "0.0.0.0",
            "port": self.port.value(),
            "token": token,
        })
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.cfg, indent=2))
        CONFIG_FILE.chmod(0o600)
        self.update_url()
        self.status.setText("● Ayarlar kaydedildi")
        self.status.setStyleSheet("font-weight:700;color:#9de4cc")
        if self.server and self.server.poll() is None:
            QMessageBox.information(
                self, "Yeniden başlatma gerekli",
                "Sunucu ayarları kaydedildi. Yeni ayarların uygulanması için sunucuyu durdurup yeniden başlat."
            )

    def update_url(self):
        ip = self.detect_ip()
        self.url_label.setText(
            f"Bu bilgisayarda: http://127.0.0.1:{self.port.value()}\n"
            f"iPad bağlantısı: http://{ip}:{self.port.value()}"
        )

    @staticmethod
    def detect_ip():
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("192.0.2.1", 80))
            return sock.getsockname()[0]
        except OSError:
            return "BILGISAYAR_IP"
        finally:
            sock.close()

    def start_server(self):
        self.save_config()
        if self.server and self.server.poll() is None:
            return
        env = os.environ.copy()
        env["NEXUS_TOKEN"] = self.cfg["token"]
        env["NEXUS_HOST"] = self.cfg["host"]
        env["NEXUS_PORT"] = str(self.cfg["port"])
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log = open(LOG_FILE, "a", buffering=1)
        try:
            self.server = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app",
                 "--host", self.cfg["host"], "--port", str(self.cfg["port"])],
                cwd=PROJECT_DIR, env=env, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True
            )
        except OSError as exc:
            log.close()
            QMessageBox.critical(self, "Başlatılamadı", str(exc))
            return
        log.close()
        self.refresh_status()
        QTimer.singleShot(900, self.refresh_status)

    def stop_server(self):
        if self.server and self.server.poll() is None:
            self.server.terminate()
            try:
                self.server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.server.kill()
        self.server = None
        self.refresh_status()

    def api_status(self):
        url = f"http://127.0.0.1:{self.port.value()}/api/status"
        request = urllib.request.Request(
            url, headers={"X-Nexus-Token": self.token.text().strip()}
        )
        with urllib.request.urlopen(request, timeout=1.2) as response:
            return json.loads(response.read())

    def refresh_status(self):
        self.update_url()
        try:
            data = self.api_status()
            self.status.setText(
                f"● Çalışıyor  ·  CPU {data.get('cpu', 0):.0f}%  ·  "
                f"RAM {data.get('memory', {}).get('percent', 0):.0f}%"
            )
            self.status.setStyleSheet("font-size:14px;font-weight:700;color:#9de4cc")
            self.tray.setToolTip("Nexus Control · Çalışıyor")
        except Exception:
            running = self.server is not None and self.server.poll() is None
            self.status.setText("● Başlatılıyor…" if running else "● Durduruldu")
            self.status.setStyleSheet(
                "font-size:14px;font-weight:700;color:#e8c58e" if running
                else "font-size:14px;font-weight:700;color:#e58b9c"
            )
            self.tray.setToolTip("Nexus Control · " + ("Başlatılıyor" if running else "Durduruldu"))

    def open_panel(self):
        QDesktopServices.openUrl(QUrl(f"http://127.0.0.1:{self.port.value()}"))

    def tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def quit_app(self):
        self.stop_server()
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray.isVisible():
            event.ignore()
            self.hide()
            self.tray.showMessage(
                "Nexus Control", "Uygulama sistem tepsisinde çalışmaya devam ediyor.",
                QSystemTrayIcon.Information, 2500
            )
        else:
            event.accept()


def run_desktop():
    app = QApplication(sys.argv)
    app.setApplicationName("Nexus Control")
    app.setQuitOnLastWindowClosed(False)
    window = NexusWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_desktop()
