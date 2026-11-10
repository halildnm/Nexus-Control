# NEXUS Control 0.2 — Arch Linux + Niri

NEXUS Control, Arch Linux masaüstünü iPad veya başka bir yerel ağ cihazından yönetmek için hazırlanmış bir web kontrol panelidir. Arayüz DMS/Material You görsel dilini iPadOS benzeri dokunmatik kullanım ile birleştirir; dikey ve yatay ekranlara uyum sağlar.

## Özellikler

- CPU, RAM, disk ve erişilebilen sıcaklık sensörleri
- Niri çalışma alanlarını listeleme ve çalışma alanına geçiş
- MPRIS medya kontrolü (`playerctl`)
- PipeWire (`wpctl`) veya PulseAudio (`pactl`) ses seviyesi ve sessize alma
- Ağ gönderim/alım toplam sayaçları
- WebSocket üzerinden bir saniyelik canlı durum güncellemeleri
- Token korumalı API ve WebSocket bağlantısı
- iPad portre/yatay uyumlu responsive arayüz

## Kurulum

Arch Linux'ta gerekli paketler:

```bash
sudo pacman -S --needed python python-pip playerctl wireplumber niri
```

Proje klasöründe:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Bilgisayarda çalıştırma

Bir token oluştur ve sunucuyu başlat:

```bash
export NEXUS_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
nexus-control
```

Bilgisayarda `http://127.0.0.1:8765` adresini aç.

## iPad veya yerel ağ cihazından erişim

Bilgisayar ve iPad aynı güvenilir Wi-Fi ağına bağlı olmalı. NEXUS'u yerel ağa aç:

```bash
export NEXUS_HOST=0.0.0.0
export NEXUS_PORT=8765
export NEXUS_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
nexus-control
```

Bilgisayarın IP adresini bul:

```bash
ip -4 route get 1.1.1.1
```

Çıktıdaki `src` adresini iPad Safari'de `http://BILGISAYAR_IP:8765` biçiminde aç ve terminalde üretilen token'ı gir.

## Niri entegrasyonu

Backend Niri IPC komutlarını kullanır:

- `niri msg --json workspaces` — çalışma alanı bilgileri
- `niri msg --json windows` — çalışma alanı başına pencere sayısı (Niri sürümünün JSON alanlarıyla uyumluysa)
- `niri msg action focus-workspace N` — çalışma alanına geçiş

NEXUS'u Niri oturumunun içinden başlat. `niri` komutu terminalde çalışıyor olmalı.

## Güvenlik notları

- Yalnızca güvendiğin yerel ağda kullan. İnternete açma ve modeminde port yönlendirmesi oluşturma.
- Token'ı kimseyle paylaşma. Token'ı terminal geçmişine veya herkese açık dosyalara koyma.
- Bu sürüm yerel ağ prototipidir; HTTP kullanır. Hassas/uzaktan kullanım için HTTPS ve daha sıkı oturum yönetimi eklenmelidir.
- Sunucu varsayılan olarak `127.0.0.1:8765` adresine bağlanır. iPad erişimi için `NEXUS_HOST=0.0.0.0` gerekir.

## Henüz eklenmeyenler

GPU telemetrisi, Wi-Fi/Bluetooth anahtarları, canlı ağ hız grafikleri, uygulama başlatıcı, pencere yönetimi ve otomatik systemd kullanıcı servisi sonraki sürümlere bırakılmıştır.


## Nexus Control Desktop (0.3.3)

Masaüstü yönetim uygulaması eklendi. Grafik arayüz üzerinden sunucuyu başlatıp durdurabilir, portu ve erişim anahtarını değiştirebilir, yerel panel adresini görebilir ve uygulamayı sistem tepsisinden yönetebilirsiniz.

### Terminal kullanmadan kurulum (Arch Linux)

1. Arşivi çıkarın.
2. `install.sh` dosyasına sağ tıklayıp **Çalıştır** seçeneğini kullanın (dosya yöneticiniz bu seçeneği sunmuyorsa dosya özelliklerinden çalıştırılabilir yapın).
3. Sistem paketleri için grafik yetki penceresi açılırsa onaylayın.
4. Uygulama menüsünden **Nexus Control** uygulamasını açın.

Gerekli temel paketler: Python, PySide6, playerctl ve WirePlumber. Kurulum betiği Arch tabanlı sistemlerde PySide6 ve medya/ses araçlarını `pkexec` ile kurmayı dener. Uygulama Python sanal ortamını kullanıcı dizinine kurar; sistem Python'unu değiştirmez.

### Masaüstü uygulaması

- Sunucuyu başlatma/durdurma
- Otomatik token üretimi ve ayarların kullanıcı dizininde saklanması
- iPad için LAN URL'sini gösterme
- Sistem tepsisi menüsü (tepsi sunucusu bulunan Niri/Dux oturumlarında)
- Pencereyi kapatınca tepsiye küçültme
- Sunucu günlük dosyası: `~/.local/state/nexus-control/server.log`

### Dux Shell 2.0 eklentisi

`integrations/dux-nexus/` klasörü Dux Shell 2.0 bar widget eklentisini içerir.

Kurulum betiği Dux yapılandırma dizini mevcutsa eklentiyi `~/.config/dms/plugins/NexusControl` konumuna kopyalar. Ardından:

1. Dux Settings → Plugins bölümünde **Nexus Control** eklentisini etkinleştirin.
2. Bar widget listesine ekleyin.
3. Eklenti ayarlarında Nexus adresini (ör. `http://192.168.1.20:8765`) ve masaüstü uygulamasındaki token'ı girin.

Widget bağlantı durumunu ve CPU kullanımını gösterir; tıklandığında Nexus web panelini açar. Dux Shell 2.0 plugin manifest/QML yapısına göre hazırlanmıştır.

### Niri ve sistem tepsisi

Niri bir sistem tepsisi sağlayıcısı değildir; tepsi simgeleri Dux Shell veya Waybar gibi bir StatusNotifierItem tepsi sunucusu tarafından gösterilir. Nexus Desktop Qt sistem tepsisi simgesi yayınlar. Dux Shell'in tepsisi etkinse simge orada görünür. Yalın Niri kullanıyorsanız bir tepsi sunucusu etkinleştirin; uygulama penceresi tepsi olmasa da çalışır.

### Güvenlik

- Varsayılan olarak `0.0.0.0:8765` üzerinde dinler; böylece iPad aynı ağdan erişebilir.
- Token `~/.config/nexus-control/config.json` içinde `0600` izinleriyle saklanır.
- Yalnızca güvendiğiniz LAN'da kullanın; portu internete yönlendirmeyin.
- HTTP kullanımı nedeniyle güvenilmeyen ağlarda kullanmayın.


### Dux Shell 2.0.1 düzeltmesi

Dux Shell 2.0'da `DIcon` bileşeni `qs.DCommon.Widgets` modülünden içe aktarılır. NexusWidget.qml bu import ile güncellendi.
