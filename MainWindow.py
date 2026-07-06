import os
import glob

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from commands import execute

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow:

    def __init__(self, app):

        self.builder = Gtk.Builder()

        self.builder.add_from_file(os.path.join(BASE_DIR, "MainWindow.glade"))
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window")
        self.window.set_application(app)

        self.defineComponents()

        self.window.show_all()

    def defineComponents(self):
        self.output_view = self.builder.get_object("output_view")
        self.output_buffer = self.output_view.get_buffer()
        self._show("Fonksiyon Çıktısı")

    def _show(self, text):
        self.output_buffer.set_text(text)

    def _confirm(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=message,
        )
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def on_free_ram_clicked(self, btn):
        self._show(execute(["free", "-h"]))

    def on_clean_cache_clicked(self, btn):
        self._show(execute(["pkexec", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"]))

    def on_kernel_version_clicked(self, btn):
        self._show(execute(["uname", "-r"]))

    def on_sistemi_kapat_clicked(self, btn):
        if not self._confirm("Sistemi kapatmak istediğinize emin misiniz?"):
            return
        self._show(execute(["systemctl", "poweroff"]))

    def on_reboot_clicked(self, btn):
        if not self._confirm("Sistemi yeniden başlatmak istediğinize emin misiniz?"):
            return
        self._show(execute(["systemctl", "reboot"]))

    def on_logout_clicked(self, btn):
        if not self._confirm("Oturumu kapatmak istediğinize emin misiniz?"):
            return
        session_id = os.environ.get("XDG_SESSION_ID")
        if not session_id:
            self._show("Hata: XDG_SESSION_ID bulunamadı, oturum bu ortamda kapatılamıyor.")
            return
        self._show(execute(["loginctl", "terminate-session", session_id]))

    def on_username_clicked(self, btn):
        self._show(execute(["whoami"]))

    def on_disc_usage_clicked(self, btn):
        self._show(execute(["df", "-h"]))

    def on_cpu_info_clicked(self, btn):
        self._show(execute(["lscpu"]))

    def on_network_info_clicked(self, btn):
        self._show(execute(["ip", "-brief", "address"]))

    def on_uptime_clicked(self, btn):
        self._show(execute(["uptime", "-p"]))

    def on_os_info_clicked(self, btn):
        self._show(execute(["cat", "/etc/os-release"]))

    def on_battery_clicked(self, btn):
        capacity_paths = glob.glob("/sys/class/power_supply/BAT*/capacity")
        if not capacity_paths:
            self._show("Pil bulunamadı.")
            return

        capacity_path = capacity_paths[0]
        with open(capacity_path) as f:
            capacity = f.read().strip()

        status = ""
        try:
            with open(capacity_path.replace("capacity", "status")) as f:
                status = f.read().strip()
        except OSError:
            pass

        self._show(f"Pil: %{capacity} ({status})" if status else f"Pil: %{capacity}")
