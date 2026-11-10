from __future__ import annotations

import asyncio
import json
import os
import secrets
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any

import psutil
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
TOKEN = os.environ.get("NEXUS_TOKEN", "")
app = FastAPI(title="NEXUS Control")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


def run_cmd(args: list[str], timeout: float = 2.0) -> str:
    """Run a fixed, argument-list command; never passes user text to a shell."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return p.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def require_token(value: str | None) -> None:
    if not TOKEN:
        raise HTTPException(503, "NEXUS_TOKEN is not configured")
    if not value or not secrets.compare_digest(value, TOKEN):
        raise HTTPException(401, "Invalid token")



def get_workspaces() -> list[dict[str, Any]]:
    raw = run_cmd(["niri", "msg", "--json", "workspaces"])

    try:
        items = json.loads(raw)
        if not isinstance(items, list):
            return []
    except (json.JSONDecodeError, TypeError):
        return []

    # Pencereleri çalışma alanlarına göre say.
    windows_raw = run_cmd(["niri", "msg", "--json", "windows"])
    window_counts: dict[int, int] = {}

    try:
        windows = json.loads(windows_raw)
        if isinstance(windows, list):
            for window in windows:
                workspace_id = window.get("workspace_id")
                if workspace_id is not None:
                    window_counts[workspace_id] = (
                        window_counts.get(workspace_id, 0) + 1
                    )
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

    # Odaktaki ekranın çalışma alanlarını göster.
    focused = next(
        (w for w in items if w.get("is_focused")),
        None
    )
    focused_output = focused.get("output") if focused else None

    visible_items = [
        w for w in items
        if focused_output is None or w.get("output") == focused_output
    ]

    return [
        {
            "id": w["idx"],
            "name": w.get("name") or str(w["idx"]),
            "monitor": w.get("output"),
            "windows": window_counts.get(w.get("id"), 0),
            "active": bool(w.get("is_focused")),
        }
        for w in sorted(visible_items, key=lambda x: x.get("idx", 0))
        if isinstance(w.get("idx"), int)
    ]
def get_media() -> dict[str, Any]:
    if not shutil.which("playerctl"):
        return {"available": False, "status": "unavailable"}
    status = run_cmd(["playerctl", "status"])
    metadata = run_cmd(["playerctl", "metadata", "--format",
                        "{{title}}|||{{artist}}|||{{album}}|||{{artUrl}}"])
    parts = metadata.split("|||", 3)
    while len(parts) < 4:
        parts.append("")
    return {
        "available": True,
        "status": status.lower() if status else "stopped",
        "title": parts[0], "artist": parts[1], "album": parts[2], "art": parts[3],
    }


def get_audio() -> dict[str, Any]:
    if shutil.which("wpctl"):
        vol = run_cmd(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
        try:
            value = float(vol.split()[1]) * 100
            muted = "[MUTED]" in vol
            return {"volume": round(max(0, min(100, value))), "muted": muted, "backend": "pipewire"}
        except (IndexError, ValueError):
            pass
    if shutil.which("pactl"):
        raw = run_cmd(["pactl", "get-sink-volume", "@DEFAULT_SINK@"])
        try:
            value = int(raw.split("/")[1].strip().rstrip("%"))
            muted = "yes" in run_cmd(["pactl", "get-sink-mute", "@DEFAULT_SINK@"])
            return {"volume": value, "muted": muted, "backend": "pulseaudio"}
        except (IndexError, ValueError):
            pass
    return {"volume": None, "muted": None, "backend": "unavailable"}


def snapshot() -> dict[str, Any]:
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    temps = []
    try:
        for group in (psutil.sensors_temperatures() or {}).values():
            for sensor in group:
                if sensor.current is not None:
                    temps.append(sensor.current)
    except (AttributeError, OSError):
        pass
    net = psutil.net_io_counters()
    return {
        "host": socket.gethostname(),
        "cpu": psutil.cpu_percent(interval=None),
        "memory": {"percent": mem.percent, "used_gb": round(mem.used / 1024**3, 1),
                   "total_gb": round(mem.total / 1024**3, 1)},
        "disk": {"percent": disk.percent, "used_gb": round(disk.used / 1024**3, 1),
                 "total_gb": round(disk.total / 1024**3, 1)},
        "temperature": round(max(temps), 1) if temps else None,
        "network": {"sent_mb": round(net.bytes_sent / 1024**2, 1),
                    "recv_mb": round(net.bytes_recv / 1024**2, 1)},
        "workspaces": get_workspaces(),
        "media": get_media(),
        "audio": get_audio(),
    }


@app.get("/")
async def index():
    return FileResponse(BASE / "static" / "index.html")


@app.get("/api/status")
async def status(x_nexus_token: str | None = Header(default=None)):
    require_token(x_nexus_token)
    return snapshot()


@app.post("/api/action/{action}")
async def action(action: str, x_nexus_token: str | None = Header(default=None), payload: dict | None = None):
    require_token(x_nexus_token)
    # Only predefined actions are accepted. No arbitrary shell command endpoint.
    if action in {"play-pause", "next", "previous"}:
        if not shutil.which("playerctl"):
            raise HTTPException(503, "playerctl is not installed")
        cmd = {"play-pause": ["playerctl", "play-pause"],
               "next": ["playerctl", "next"],
               "previous": ["playerctl", "previous"]}[action]
    elif action == "workspace":
        try:
            wid = int((payload or {}).get("id"))
        except (TypeError, ValueError):
            raise HTTPException(400, "Workspace id must be an integer")

        if wid < 1 or wid > 100:
            raise HTTPException(400, "Workspace id out of range")

        if not shutil.which("niri"):
            raise HTTPException(503, "Niri command not found")

        cmd = ["niri", "msg", "action", "focus-workspace", str(wid)]

    elif action == "volume":
        try:
            amount = int((payload or {}).get("value"))
        except (TypeError, ValueError):
            raise HTTPException(400, "Volume must be an integer")
        amount = max(0, min(100, amount))
        if shutil.which("wpctl"):
            cmd = ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{amount}%"]
        elif shutil.which("pactl"):
            cmd = ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{amount}%"]
        else:
            raise HTTPException(503, "No supported audio control utility found")
    elif action == "mute":
        if shutil.which("wpctl"):
            cmd = ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]
        elif shutil.which("pactl"):
            cmd = ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"]
        else:
            raise HTTPException(503, "No supported audio control utility found")
    else:
        raise HTTPException(404, "Unknown action")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3, check=False)
    if result.returncode:
        raise HTTPException(500, result.stderr.strip() or "Command failed")
    return {"ok": True}


@app.websocket("/ws")
async def websocket_status(ws: WebSocket):
    token = ws.query_params.get("token", "")
    if not TOKEN or not secrets.compare_digest(token, TOKEN):
        await ws.close(code=1008)
        return
    await ws.accept()
    try:
        while True:
            await ws.send_json(snapshot())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


def run():
    import uvicorn
    uvicorn.run("app.main:app", host=os.environ.get("NEXUS_HOST", "127.0.0.1"),
                port=int(os.environ.get("NEXUS_PORT", "8765")), reload=False)
