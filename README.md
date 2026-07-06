![resim](https://user-images.githubusercontent.com/78855338/204103223-3525f530-e921-47c8-a88f-3f9050068aba.png)

# Linux Multitool

GTK3 + PyGObject ile yazılmış, temel Linux sistem araçlarını tek bir pencereden
sunan basit bir masaüstü uygulaması.

## Özellikler

- RAM kullanımı (`free -h`)
- RAM önbelleğini temizleme (polkit üzerinden yetkilendirilmiş)
- Kernel versiyonu
- Sistemi kapat / yeniden başlat / oturumu kapat (onay diyaloğu ile)
- Kullanıcı adı
- Disk kullanımı (`df -h`)
- İşlemci bilgisi (`lscpu`)
- Ağ bilgisi (`ip -brief address`)
- Sistem çalışma süresi (`uptime -p`)
- Dağıtım bilgisi (`/etc/os-release`)
- Pil durumu (varsa)

## Gereksinimler

- Python 3
- PyGObject (`python3-gi`) ve GTK3 introspection verileri (`gir1.2-gtk-3.0`)
- `policykit-1` (önbellek temizleme için `pkexec`)
- `iproute2` (ağ bilgisi için `ip`) ve `util-linux` (`lscpu`, `uptime`) — çoğu
  dağıtımda zaten kurulu

Debian/Ubuntu türevlerinde:

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 policykit-1
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

- GTK4 / libadwaita geçişi
- Flatpak olarak paketleme
- i18n / `gettext` ile çoklu dil desteği
- Paket yöneticisi güncelleme kontrolü (dağıtımdan bağımsız bir çözüm gerektirir)
- Servis yöneticisi paneli (`systemctl` birimlerini listeleme/başlatma/durdurma)
- Journal/log görüntüleyici
