![resim](https://user-images.githubusercontent.com/78855338/204103223-3525f530-e921-47c8-a88f-3f9050068aba.png)

# Linux Multitool

GTK4 + PyGObject ile yazılmış, temel Linux sistem araçlarını tek bir pencereden
sunan basit bir masaüstü uygulaması. Araçlar, üstteki sekme çubuğuyla
kategorilere ayrılmıştır; log alanı ve alt araç çubuğu (kopyala/kaydet/
temizle/tema/otomatik yenile/ara) tüm sekmelerde ortak ve her zaman görünür.

## Özellikler

### Sistem
RAM kullanımı, kernel versiyonu, detaylı sistem bilgisi (`uname -a`),
çalışma süresi, dağıtım bilgisi, sistem yükü, süreç listesi (en çok RAM
kullananlar), çekirdek modülleri (`lsmod`).

### Donanım & Depolama
İşlemci bilgisi, ekran kartı bilgisi, disk kullanımı, inode kullanımı,
disk/bölüm listesi (`lsblk`), USB cihazları, pil durumu (varsa).

### Ağ
Ağ arayüzleri, bağlantı testi (`ping`), açık/dinleyen portlar (`ss -tulpn`),
yönlendirme tablosu (`ip route`), DNS sunucuları.

### Güç & Oturum
Sistemi kapat / yeniden başlat / oturumu kapat (onay diyaloğu ile), kullanıcı
adı, RAM önbelleğini temizleme (polkit ile yetkilendirilmiş).

### Loglar & Servisler
Başarısız systemd servisleri, son 50 journal kaydı, yalnızca hata seviyesi
kayıtlar, çekirdek uyarıları (`dmesg`), açılış süresi ve en yavaş başlayan
servisler (`systemd-analyze`), aktif oturumlar (`who`), son girişler (`last`).

### Araç çubuğu (tüm sekmelerde ortak)
Çıktıyı panoya kopyalama, dosyaya kaydetme, temizleme; karanlık/açık tema
anahtarı; RAM kullanımını 2 saniyede bir otomatik yenileme (aç/kapa); çıktı
içinde arama (ilk eşleşmeyi vurgulayıp oraya kaydırır); yazı tipi boyutu
büyüt/küçült.

## Gereksinimler

- Python 3
- PyGObject (`python3-gi`) ve GTK4 introspection verileri (`gir1.2-gtk-4.0`)
- `policykit-1` (önbellek temizleme için `pkexec`)
- `iproute2` (`ip`, `ss`), `util-linux` (`lscpu`, `uptime`, `lsblk`),
  `procps` (`ps`), `pciutils` (`lspci`), `usbutils` (`lsusb`),
  `iputils-ping`, `systemd` (`systemctl`, `journalctl`) — bunların hepsi
  çoğu dağıtımda zaten kurulu gelir. Eksik olan bir araç varsa ilgili
  buton çökmek yerine "komut bulunamadı" mesajı gösterir.

GTK4, çoğu güncel dağıtımda hazır gelir (Ubuntu 22.04+, Debian 12+, Fedora
36+ ve sonrası). Daha eski sürümlerde `gir1.2-gtk-4.0` paketi bulunamayabilir;
uygulama bu durumda çökmek yerine anlaşılır bir hata mesajıyla çıkar.

Debian/Ubuntu türevlerinde:

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 policykit-1
```

## Kurulum ve Çalıştırma

```bash
git clone <repo-url>
cd linux-multitool
python3 main.py
```

Masaüstü menüsüne eklemek isterseniz `linux-multitool.desktop` dosyasındaki
`Exec` satırını projenin kurulu olduğu yola göre düzenleyip
`~/.local/share/applications/` altına kopyalayabilirsiniz.

## Geliştirme

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check .
```

`commands.py` içindeki `execute()` fonksiyonu GTK'dan bağımsızdır; testler GTK
veya bir ekran (display) gerektirmeden çalışır.

## Gelecek Yol Haritası

Aşağıdakiler bilinçli olarak kapsam dışında bırakıldı, ileride ayrı işler
olarak ele alınabilir:

- libadwaita ile modern GNOME görünümüne geçiş
- Flatpak olarak paketleme
- i18n / `gettext` ile çoklu dil desteği
- Paket yöneticisi güncelleme kontrolü (dağıtımdan bağımsız bir çözüm gerektirir)
- Servis başlatma/durdurma (şu an yalnızca başarısız servisleri listeleme var)
- Sıcaklık sensörleri, Wi-Fi detayı, firewall durumu (dağıtıma/DE'ye özel araçlar gerektirir)
