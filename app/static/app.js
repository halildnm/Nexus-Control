const $ = id => document.getElementById(id);
let token = sessionStorage.getItem("nexus-token") || "";
let socket, reconnectTimer, volumeTimer;

function setConnected(ok) {
  $("dot").classList.toggle("online", ok);
  $("connection").textContent = ok ? "Bağlı" : "Bağlantı kesildi";
}
function showLogin(message = "") {
  $("login").classList.remove("hidden");
  $("login-error").textContent = message;
}
function authHeaders() {
  return { "Content-Type": "application/json", "X-Nexus-Token": token };
}
function setMeter(id, value) {
  $(id).style.width = `${Math.max(0, Math.min(100, Number(value) || 0))}%`;
}
function render(data) {
  $("host").textContent = `${data.host || "Desktop"} · Arch Linux · Niri`;
  $("cpu").innerHTML = `${Math.round(data.cpu ?? 0)}<small>%</small>`;
  setMeter("cpu-bar", data.cpu);
  $("ram").innerHTML = `${data.memory.used_gb}<small> GB</small>`;
  $("ram-detail").textContent = `${data.memory.percent}% · ${data.memory.total_gb} GB toplam`;
  setMeter("ram-bar", data.memory.percent);
  $("disk").innerHTML = `${data.disk.percent}<small>%</small>`;
  $("disk-detail").textContent = `${data.disk.used_gb} / ${data.disk.total_gb} GB`;
  setMeter("disk-bar", data.disk.percent);
  $("temp").textContent = data.temperature == null ? "N/A" : `${data.temperature}°`;
  setMeter("temp-bar", data.temperature == null ? 0 : Math.min(100, data.temperature));
  $("sent").textContent = `${data.network.sent_mb} MB`;
  $("recv").textContent = `${data.network.recv_mb} MB`;

  const media = data.media || {};
  $("media-status").textContent = media.status || "Beklemede";
  $("track-title").textContent = media.title || "Şu anda çalan medya yok";
  $("track-artist").textContent = media.artist || (media.available ? "Playerctl hazır" : "playerctl kurulu değil");
  $("track-album").textContent = media.album || "";
  const cover = $("cover");
  const art = typeof media.art === "string" && /^https?:\/\//i.test(media.art) ? media.art : "";
  cover.style.backgroundImage = art ? `url("${art.replaceAll('"', "")}")` : "none";
  cover.textContent = art ? "" : "♫";

  const workspaces = data.workspaces || [];
  $("workspace-count").textContent = `${workspaces.length} alan`;
  const area = $("workspaces");
  area.replaceChildren();
  if (!workspaces.length) {
    const empty = document.createElement("span");
    empty.className = "empty-state";
    empty.textContent = "Çalışma alanı bulunamadı. Niri oturumunu kontrol et.";
    area.append(empty);
  }
  workspaces.forEach(workspace => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `workspace${workspace.active ? " active" : ""}`;
    const title = document.createElement("span");
    title.textContent = String(workspace.name ?? workspace.id);
    const detail = document.createElement("small");
    detail.textContent = `${workspace.windows || 0} pencere`;
    button.append(title, detail);
    button.setAttribute("aria-label", `${workspace.name ?? workspace.id} numaralı çalışma alanına geç`);
    button.setAttribute("aria-pressed", workspace.active ? "true" : "false");
    button.addEventListener("click", () => sendAction("workspace", { id: workspace.id }));
    area.append(button);
  });

  const audio = data.audio || {};
  if (audio.volume !== null && audio.volume !== undefined) {
    $("volume").value = audio.volume;
    $("volume-value").textContent = `${audio.volume}%${audio.muted ? " · Sessiz" : ""}`;
  }
  $("audio-backend").textContent = audio.backend || "Ses servisi bulunamadı";
}
function connect() {
  if (!token) { showLogin(); return; }
  clearTimeout(reconnectTimer);
  const scheme = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${scheme}://${location.host}/ws?token=${encodeURIComponent(token)}`);
  socket.onopen = () => { setConnected(true); $("login").classList.add("hidden"); };
  socket.onmessage = event => {
    try { render(JSON.parse(event.data)); }
    catch (error) { console.error("NEXUS snapshot parse error:", error); }
  };
  socket.onerror = () => setConnected(false);
  socket.onclose = event => {
    setConnected(false);
    if (event.code === 1008) {
      token = "";
      sessionStorage.removeItem("nexus-token");
      showLogin("Erişim anahtarı geçersiz. Yeniden gir.");
      return;
    }
    if (token) reconnectTimer = setTimeout(connect, 2500);
  };
}
async function sendAction(name, payload = {}) {
  try {
    const response = await fetch(`/api/action/${name}`, {
      method: "POST", headers: authHeaders(), body: JSON.stringify(payload)
    });
    if (response.status === 401) {
      token = "";
      sessionStorage.removeItem("nexus-token");
      showLogin("Erişim anahtarı geçersiz.");
      return;
    }
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      window.alert(detail.detail || "İşlem başarısız.");
    }
  } catch {
    window.alert("Bilgisayara ulaşılamıyor.");
  }
}

document.querySelectorAll("[data-action]").forEach(button => {
  button.addEventListener("click", () => sendAction(button.dataset.action));
});
$("mute").addEventListener("click", () => sendAction("mute"));
$("volume").addEventListener("input", event => {
  $("volume-value").textContent = `${event.target.value}%`;
  clearTimeout(volumeTimer);
  volumeTimer = setTimeout(() => sendAction("volume", { value: Number(event.target.value) }), 180);
});
$("token-form").addEventListener("submit", event => {
  event.preventDefault();
  token = $("token-input").value.trim();
  if (!token) return;
  sessionStorage.setItem("nexus-token", token);
  $("login").classList.add("hidden");
  connect();
});
if (token) connect(); else showLogin();
