import os
import glob

import gi
from gi.repository import Gtk, GLib
from commands import execute
gi.require_version('Gtk', '4.0')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# GTK4'te Gtk.Builder.connect_signals() kaldırıldı; butonlar id -> handler
# eşlemesiyle burada elle bağlanıyor.
BUTTON_HANDLERS = {
    "free_ram": "on_free_ram_clicked",
    "clean_cache": "on_clean_cache_clicked",
    "kernel_version": "on_kernel_version_clicked",
    "sistemi_kapat": "on_sistemi_kapat_clicked",
    "reboot": "on_reboot_clicked",
    "logout": "on_logout_clicked",
    "username": "on_username_clicked",
    "disc_usage": "on_disc_usage_clicked",
    "cpu_info": "on_cpu_info_clicked",
    "network_info": "on_network_info_clicked",
    "uptime": "on_uptime_clicked",
    "os_info": "on_os_info_clicked",
    "battery": "on_battery_clicked",
    "process_list": "on_process_list_clicked",
    "load_avg": "on_load_avg_clicked",
    "gpu_info": "on_gpu_info_clicked",
    "ping": "on_ping_clicked",
    "open_ports": "on_open_ports_clicked",
    "failed_services": "on_failed_services_clicked",
    "recent_logs": "on_recent_logs_clicked",
    "error_logs": "on_error_logs_clicked",
    "lsblk": "on_lsblk_clicked",
    "lsusb": "on_lsusb_clicked",
    "sessions": "on_sessions_clicked",
    "last_logins": "on_last_logins_clicked",
    "copy_output": "on_copy_output_clicked",
    "system_info": "on_system_info_clicked",
    "kernel_modules": "on_kernel_modules_clicked",
    "disk_inode": "on_disk_inode_clicked",
    "ip_route": "on_ip_route_clicked",
    "dns_info": "on_dns_info_clicked",
    "boot_time": "on_boot_time_clicked",
    "slowest_services": "on_slowest_services_clicked",
    "kernel_warnings": "on_kernel_warnings_clicked",
    "clear_output": "on_clear_output_clicked",
    "save_output": "on_save_output_clicked",
    "font_decrease": "on_font_decrease_clicked",
    "font_increase": "on_font_increase_clicked",
}

MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 24
DEFAULT_FONT_SIZE = 10

# "clicked" dışında sinyal kullanan togglebutton'lar ayrı bağlanıyor.
TOGGLE_HANDLERS = {
    "dark_mode": "on_dark_mode_toggled",
    "auto_refresh": "on_auto_refresh_toggled",
}


class MainWindow:

    def __init__(self, app):

        self.builder = Gtk.Builder()

        self.builder.add_from_file(os.path.join(BASE_DIR, "MainWindow.ui"))

        self.window = self.builder.get_object("window")
        self.window.set_application(app)

        self._auto_refresh_id = None
        self._font_size = DEFAULT_FONT_SIZE

        self.defineComponents()
        self._connect_signals()

        self.window.present()

    def defineComponents(self):
        self.output_view = self.builder.get_object("output_view")
        self.output_buffer = self.output_view.get_buffer()
        self.search_entry = self.builder.get_object("search_entry")
        self.search_tag = self.output_buffer.create_tag(
            "search-highlight", background="yellow", foreground="black"
        )

        self._font_provider = Gtk.CssProvider()
        self.output_view.get_style_context().add_provider(
            self._font_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self._apply_font_size()

        self._show("Fonksiyon Çıktısı")

    def _connect_signals(self):
        for widget_id, handler_name in BUTTON_HANDLERS.items():
            button = self.builder.get_object(widget_id)
            button.connect("clicked", getattr(self, handler_name))
        for widget_id, handler_name in TOGGLE_HANDLERS.items():
            toggle = self.builder.get_object(widget_id)
            toggle.connect("toggled", getattr(self, handler_name))
        self.search_entry.connect("search-changed", self.on_search_changed)

    def _show(self, text):
        self.output_buffer.set_text(text)

    def _confirm(self, message, on_yes):
        # GtkDialog.run() GTK4'te kaldırıldı; onay artık "response" sinyaliyle asenkron alınıyor.
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=message,
        )

        def on_response(dlg, response):
            dlg.destroy()
            if response == Gtk.ResponseType.YES:
                on_yes()

        dialog.connect("response", on_response)
        dialog.present()

    def on_free_ram_clicked(self, btn):
        self._show(execute(["free", "-h"]))

    def on_clean_cache_clicked(self, btn):
        self._show(execute(["pkexec", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"]))

    def on_kernel_version_clicked(self, btn):
        self._show(execute(["uname", "-r"]))

    def on_sistemi_kapat_clicked(self, btn):
        self._confirm(
            "Sistemi kapatmak istediğinize emin misiniz?",
            lambda: self._show(execute(["systemctl", "poweroff"])),
        )

    def on_reboot_clicked(self, btn):
        self._confirm(
            "Sistemi yeniden başlatmak istediğinize emin misiniz?",
            lambda: self._show(execute(["systemctl", "reboot"])),
        )

    def on_logout_clicked(self, btn):
        self._confirm("Oturumu kapatmak istediğinize emin misiniz?", self._do_logout)

    def _do_logout(self):
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

    def on_process_list_clicked(self, btn):
        output = execute(["ps", "aux", "--sort=-%mem"])
        lines = output.splitlines()
        self._show("\n".join(lines[:7]))

    def on_load_avg_clicked(self, btn):
        with open("/proc/loadavg") as f:
            self._show(f.read().strip())

    def on_gpu_info_clicked(self, btn):
        output = execute(["lspci"])
        matches = [
            line for line in output.splitlines()
            if "vga" in line.lower() or "3d controller" in line.lower()
        ]
        self._show("\n".join(matches) if matches else "GPU bilgisi bulunamadı.")

    def on_ping_clicked(self, btn):
        self._show(execute(["ping", "-c", "3", "-W", "2", "1.1.1.1"]))

    def on_open_ports_clicked(self, btn):
        self._show(execute(["ss", "-tulpn"]))

    def on_failed_services_clicked(self, btn):
        self._show(execute(["systemctl", "--failed"]))

    def on_recent_logs_clicked(self, btn):
        self._show(execute(["journalctl", "-n", "50", "--no-pager"]))

    def on_error_logs_clicked(self, btn):
        self._show(execute(["journalctl", "-p", "err", "-n", "50", "--no-pager"]))

    def on_lsblk_clicked(self, btn):
        self._show(execute(["lsblk"]))

    def on_lsusb_clicked(self, btn):
        self._show(execute(["lsusb"]))

    def on_sessions_clicked(self, btn):
        self._show(execute(["who"]))

    def on_last_logins_clicked(self, btn):
        self._show(execute(["last", "-n", "10"]))

    def on_system_info_clicked(self, btn):
        self._show(execute(["uname", "-a"]))

    def on_kernel_modules_clicked(self, btn):
        self._show(execute(["lsmod"]))

    def on_disk_inode_clicked(self, btn):
        self._show(execute(["df", "-i"]))

    def on_ip_route_clicked(self, btn):
        self._show(execute(["ip", "route"]))

    def on_dns_info_clicked(self, btn):
        with open("/etc/resolv.conf") as f:
            self._show(f.read())

    def on_boot_time_clicked(self, btn):
        self._show(execute(["systemd-analyze"]))

    def on_slowest_services_clicked(self, btn):
        self._show(execute(["systemd-analyze", "blame"]))

    def on_kernel_warnings_clicked(self, btn):
        output = execute(["dmesg", "--level=err,warn", "-T"])
        self._show("\n".join(output.splitlines()[-50:]))

    def on_clear_output_clicked(self, btn):
        self._show("")

    def on_save_output_clicked(self, btn):
        dialog = Gtk.FileChooserNative.new(
            "Çıktıyı Kaydet", self.window, Gtk.FileChooserAction.SAVE, "Kaydet", "İptal"
        )
        dialog.set_current_name("cikti.txt")

        def on_response(dlg, response):
            if response == Gtk.ResponseType.ACCEPT:
                path = dlg.get_file().get_path()
                text = self.output_buffer.get_text(
                    self.output_buffer.get_start_iter(), self.output_buffer.get_end_iter(), True
                )
                try:
                    with open(path, "w") as f:
                        f.write(text)
                except OSError as e:
                    self._show(f"Hata: {e}")
            dlg.destroy()

        dialog.connect("response", on_response)
        dialog.show()

    def on_search_changed(self, entry):
        buf = self.output_buffer
        buf.remove_tag(self.search_tag, buf.get_start_iter(), buf.get_end_iter())

        query = entry.get_text()
        if not query:
            return

        match = buf.get_start_iter().forward_search(
            query, Gtk.TextSearchFlags.CASE_INSENSITIVE, None
        )
        if match:
            match_start, match_end = match
            buf.apply_tag(self.search_tag, match_start, match_end)
            self.output_view.scroll_to_iter(match_start, 0.0, False, 0, 0)

    def _apply_font_size(self):
        css = f"textview {{ font-size: {self._font_size}pt; }}"
        self._font_provider.load_from_data(css.encode())

    def on_font_increase_clicked(self, btn):
        self._font_size = min(self._font_size + 1, MAX_FONT_SIZE)
        self._apply_font_size()

    def on_font_decrease_clicked(self, btn):
        self._font_size = max(self._font_size - 1, MIN_FONT_SIZE)
        self._apply_font_size()

    def on_copy_output_clicked(self, btn):
        text = self.output_buffer.get_text(
            self.output_buffer.get_start_iter(), self.output_buffer.get_end_iter(), True
        )
        self.window.get_clipboard().set(text)

    def on_dark_mode_toggled(self, btn):
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", btn.get_active()
        )

    def on_auto_refresh_toggled(self, btn):
        if btn.get_active():
            self._auto_refresh_id = GLib.timeout_add_seconds(2, self._auto_refresh_tick)
        elif self._auto_refresh_id is not None:
            GLib.source_remove(self._auto_refresh_id)
            self._auto_refresh_id = None

    def _auto_refresh_tick(self):
        self._show(execute(["free", "-h"]))
        return GLib.SOURCE_CONTINUE
