import os
import glob
import json
import threading
import locale

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Adw  # noqa: E402
from commands import execute  # noqa: E402


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 24
DEFAULT_FONT_SIZE = 10

CONFIG_DIR = os.path.expanduser("~/.config/linux-multitool")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_settings():
    defaults = {
        "dark_mode": False,
        "font_size": DEFAULT_FONT_SIZE
    }
    if not os.path.exists(CONFIG_PATH):
        return defaults
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            defaults.update(data)
            return defaults
    except Exception:
        return defaults


def save_settings(settings):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Ayarlar kaydedilemedi: {e}")


# Yerelleştirme (i18n) Entegrasyonu
TRANSLATIONS = {
    "en": {
        "Fonksiyon Çıktısı": "Function Output",
        "Çalıştırılıyor...": "Running...",
        "Hata: XDG_SESSION_ID bulunamadı, oturum bu ortamda kapatılamıyor.": "Error: XDG_SESSION_ID not found, session cannot be terminated in this environment.",
        "Pil bulunamadı.": "Battery not found.",
        "GPU bilgisi bulunamadı.": "GPU info not found.",
        "Hata: Yetkilendirme (Polkit) işlemi kullanıcı tarafından iptal edildi.": "Error: Authorization (Polkit) process was cancelled by the user.",
        "Sistemi kapatmak istediğinize emin misiniz?": "Are you sure you want to shut down the system?",
        "Sistemi yeniden başlatmak istediğinize emin misiniz?": "Are you sure you want to reboot the system?",
        "Oturumu kapatmak istediğinize emin misiniz?": "Are you sure you want to log out?",
        "Çıktıyı Kaydet": "Save Output",
        "Hata: Lütfen sonlandırılacak PID veya süreç adını girin.": "Error: Please enter the PID or process name to terminate.",
        "sürecini sonlandırmak istediğinize emin misiniz?": "process, are you sure you want to terminate it?",
        "Lütfen işlem yapılacak servis adını girin.": "Please enter the service name to operate on.",
        "servisini başlatmak istediğinize emin misiniz?": "service, are you sure you want to start it?",
        "servisini durdurmak istediğinize emin misiniz?": "service, are you sure you want to stop it?",
        "servisini yeniden başlatmak istediğinize emin misiniz?": "service, are you sure you want to restart it?",
    }
}

try:
    lang, _encoding = locale.getdefaultlocale()
    lang_code = lang.split("_")[0] if lang else "tr"
except Exception:
    lang_code = "tr"


def _(text):
    if lang_code in TRANSLATIONS and text in TRANSLATIONS[lang_code]:
        return TRANSLATIONS[lang_code][text]
    return text



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
    "kill_process": "on_kill_process_clicked",
    "service_start": "on_service_start_clicked",
    "service_stop": "on_service_stop_clicked",
    "service_restart": "on_service_restart_clicked",
    "service_status": "on_service_status_clicked",
}



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
        self._settings = load_settings()
        self._font_size = self._settings.get("font_size", DEFAULT_FONT_SIZE)
        self._command_running = False

        self.defineComponents()
        self._connect_signals()
        self._start_resource_monitor()

        self.window.present()

    def defineComponents(self):
        self.output_view = self.builder.get_object("output_view")
        self.output_buffer = self.output_view.get_buffer()
        self.search_entry = self.builder.get_object("search_entry")
        self.spinner = self.builder.get_object("spinner")
        self.search_tag = self.output_buffer.create_tag(
            "search-highlight", background="yellow", foreground="black"
        )
        self.error_tag = self.output_buffer.create_tag("error-tag", foreground="red")
        self.warning_tag = self.output_buffer.create_tag("warning-tag", foreground="orange")
        self.success_tag = self.output_buffer.create_tag("success-tag", foreground="green")
        self.header_tag = self.output_buffer.create_tag("header-tag", weight=700)

        self._font_provider = Gtk.CssProvider()
        self.output_view.get_style_context().add_provider(
            self._font_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Load theme setting
        style_manager = Adw.StyleManager.get_default()
        if self._settings.get("dark_mode", False):
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
        dark_toggle = self.builder.get_object("dark_mode")
        dark_toggle.set_active(self._settings.get("dark_mode", False))

        self._apply_font_size()

        self._show(_("Fonksiyon Çıktısı"))

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
        self._highlight_output()

    def _highlight_output(self):
        buf = self.output_buffer

        # Apply header bolding to first line
        start = buf.get_start_iter()
        end_first = start.copy()
        end_first.forward_to_line_end()
        buf.apply_tag(self.header_tag, start, end_first)

        # Iterate over lines
        line_count = buf.get_line_count()
        for i in range(line_count):
            _, line_start = buf.get_iter_at_line(i)
            line_end = line_start.copy()
            line_end.forward_to_line_end()
            line_text = buf.get_text(line_start, line_end, True)

            # Check if line is an error or warning
            lower_text = line_text.lower()
            if any(k in lower_text for k in ["hata:", "error:", "critical", "fail"]):
                buf.apply_tag(self.error_tag, line_start, line_end)
            elif any(k in lower_text for k in ["uyari:", "warning:", "warn"]):
                buf.apply_tag(self.warning_tag, line_start, line_end)

            # Highlight specific keywords in-place
            for word, tag in [("active (running)", self.success_tag),
                              ("inactive (dead)", self.warning_tag),
                              ("enabled", self.success_tag),
                              ("disabled", self.warning_tag)]:
                current_start = line_start.copy()
                while True:
                    match = current_start.forward_search(word, Gtk.TextSearchFlags.CASE_INSENSITIVE, line_end)
                    if not match:
                        break
                    match_start, match_end = match
                    buf.apply_tag(tag, match_start, match_end)
                    current_start = match_end.copy()

    def _run_async(self, cmd, callback=None):
        self._set_busy(True)
        self._show(_("Çalıştırılıyor..."))

        def worker():
            result = execute(cmd)
            GLib.idle_add(self._on_command_finished, result, callback)

        threading.Thread(target=worker, daemon=True).start()

    def _on_command_finished(self, result, callback):
        self._show(_(result))
        self._set_busy(False)
        if callback:
            callback(result)

    def _set_busy(self, busy):
        self._command_running = busy
        self.builder.get_object("categories_stack").set_sensitive(not busy)
        self.builder.get_object("copy_output").set_sensitive(not busy)
        self.builder.get_object("save_output").set_sensitive(not busy)
        self.builder.get_object("clear_output").set_sensitive(not busy)
        if busy:
            self.spinner.start()
        else:
            self.spinner.stop()

    def _save_current_settings(self):
        self._settings["font_size"] = self._font_size
        self._settings["dark_mode"] = self.builder.get_object("dark_mode").get_active()
        save_settings(self._settings)

    def _start_resource_monitor(self):
        self._last_cpu_total = 0
        self._last_cpu_idle = 0
        self._update_resources()
        GLib.timeout_add_seconds(1, self._update_resources)

    def _update_resources(self):
        # Update CPU
        try:
            with open("/proc/stat", "r") as f:
                first_line = f.readline()
            parts = first_line.split()[1:]
            parts = [int(p) for p in parts]
            idle = parts[3] + parts[4]
            total = sum(parts)

            if self._last_cpu_total > 0:
                total_delta = total - self._last_cpu_total
                idle_delta = idle - self._last_cpu_idle
                if total_delta > 0:
                    cpu_fraction = 1.0 - (idle_delta / total_delta)
                    self.builder.get_object("cpu_progress").set_fraction(cpu_fraction)
                    self.builder.get_object("cpu_progress").set_text(f"{int(cpu_fraction * 100)}%")
            self._last_cpu_total = total
            self._last_cpu_idle = idle
        except Exception as e:
            print(f"CPU okuma hatası: {e}")

        # Update RAM
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem_total = 0
            mem_available = 0
            for line in lines:
                if "MemTotal" in line:
                    mem_total = int(line.split()[1])
                elif "MemAvailable" in line:
                    mem_available = int(line.split()[1])
            if mem_total > 0:
                used = mem_total - mem_available
                ram_fraction = used / mem_total
                used_gb = used / 1024 / 1024
                total_gb = mem_total / 1024 / 1024
                self.builder.get_object("ram_progress").set_fraction(ram_fraction)
                self.builder.get_object("ram_progress").set_text(
                    f"{used_gb:.1f} GB / {total_gb:.1f} GB ({int(ram_fraction * 100)}%)"
                )
        except Exception as e:
            print(f"RAM okuma hatası: {e}")

        return GLib.SOURCE_CONTINUE

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
        self._run_async(["free", "-h"])

    def on_clean_cache_clicked(self, btn):
        self._run_async(["pkexec", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"])

    def on_kernel_version_clicked(self, btn):
        self._run_async(["uname", "-r"])

    def on_sistemi_kapat_clicked(self, btn):
        self._confirm(
            _("Sistemi kapatmak istediğinize emin misiniz?"),
            lambda: self._run_async(["systemctl", "poweroff"]),
        )

    def on_reboot_clicked(self, btn):
        self._confirm(
            _("Sistemi yeniden başlatmak istediğinize emin misiniz?"),
            lambda: self._run_async(["systemctl", "reboot"]),
        )

    def on_logout_clicked(self, btn):
        self._confirm(_("Oturumu kapatmak istediğinize emin misiniz?"), self._do_logout)

    def _do_logout(self):
        session_id = os.environ.get("XDG_SESSION_ID")
        if not session_id:
            self._show(_("Hata: XDG_SESSION_ID bulunamadı, oturum bu ortamda kapatılamıyor."))
            return
        self._run_async(["loginctl", "terminate-session", session_id])

    def on_username_clicked(self, btn):
        self._run_async(["whoami"])

    def on_disc_usage_clicked(self, btn):
        self._run_async(["df", "-h"])

    def on_cpu_info_clicked(self, btn):
        self._run_async(["lscpu"])

    def on_network_info_clicked(self, btn):
        self._run_async(["ip", "-brief", "address"])

    def on_uptime_clicked(self, btn):
        self._run_async(["uptime", "-p"])

    def on_os_info_clicked(self, btn):
        self._run_async(["cat", "/etc/os-release"])

    def on_battery_clicked(self, btn):
        capacity_paths = glob.glob("/sys/class/power_supply/BAT*/capacity")
        if not capacity_paths:
            self._show(_("Pil bulunamadı."))
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
        filter_text = self.builder.get_object("process_filter").get_text().strip().lower()

        def callback(output):
            lines = output.splitlines()
            if not filter_text:
                self._show("\n".join(lines[:20]))
            else:
                header = lines[0]
                matches = [line for line in lines[1:] if filter_text in line.lower()]
                result = [header] + matches
                self._show("\n".join(result[:40]))
        self._run_async(["ps", "aux", "--sort=-%mem"], callback)

    def on_kill_process_clicked(self, btn):
        target = self.builder.get_object("process_kill_target").get_text().strip()
        if not target:
            self._show(_("Hata: Lütfen sonlandırılacak PID veya süreç adını girin."))
            return

        if target.isdigit():
            cmd = ["kill", "-9", target]
        else:
            cmd = ["pkill", "-f", target]

        msg = f"'{target}' " + _("sürecini sonlandırmak istediğinize emin misiniz?")
        self._confirm(msg, lambda: self._run_async(cmd))

    def on_load_avg_clicked(self, btn):
        with open("/proc/loadavg") as f:
            self._show(f.read().strip())

    def on_gpu_info_clicked(self, btn):
        def callback(output):
            matches = [
                line for line in output.splitlines()
                if "vga" in line.lower() or "3d controller" in line.lower()
            ]
            self._show("\n".join(matches) if matches else _("GPU bilgisi bulunamadı."))
        self._run_async(["lspci"], callback)

    def on_ping_clicked(self, btn):
        target = self.builder.get_object("ping_target").get_text().strip()
        if not target:
            target = "1.1.1.1"
        self._run_async(["ping", "-c", "3", "-W", "2", target])

    def on_open_ports_clicked(self, btn):
        self._run_async(["ss", "-tulpn"])

    def on_failed_services_clicked(self, btn):
        self._run_async(["systemctl", "--failed"])

    def on_service_start_clicked(self, btn):
        service = self.builder.get_object("service_name_entry").get_text().strip()
        if not service:
            self._show(_("Lütfen işlem yapılacak servis adını girin."))
            return
        msg = f"'{service}' " + _("servisini başlatmak istediğinize emin misiniz?")
        self._confirm(msg, lambda: self._run_async(["pkexec", "systemctl", "start", service]))

    def on_service_stop_clicked(self, btn):
        service = self.builder.get_object("service_name_entry").get_text().strip()
        if not service:
            self._show(_("Lütfen işlem yapılacak servis adını girin."))
            return
        msg = f"'{service}' " + _("servisini durdurmak istediğinize emin misiniz?")
        self._confirm(msg, lambda: self._run_async(["pkexec", "systemctl", "stop", service]))

    def on_service_restart_clicked(self, btn):
        service = self.builder.get_object("service_name_entry").get_text().strip()
        if not service:
            self._show(_("Lütfen işlem yapılacak servis adını girin."))
            return
        msg = f"'{service}' " + _("servisini yeniden başlatmak istediğinize emin misiniz?")
        self._confirm(msg, lambda: self._run_async(["pkexec", "systemctl", "restart", service]))

    def on_service_status_clicked(self, btn):
        service = self.builder.get_object("service_name_entry").get_text().strip()
        if not service:
            self._show(_("Lütfen işlem yapılacak servis adını girin."))
            return
        self._run_async(["systemctl", "status", service])

    def on_recent_logs_clicked(self, btn):
        self._run_async(["journalctl", "-n", "50", "--no-pager"])

    def on_error_logs_clicked(self, btn):
        self._run_async(["journalctl", "-p", "err", "-n", "50", "--no-pager"])

    def on_lsblk_clicked(self, btn):
        self._run_async(["lsblk"])

    def on_lsusb_clicked(self, btn):
        self._run_async(["lsusb"])

    def on_sessions_clicked(self, btn):
        self._run_async(["who"])

    def on_last_logins_clicked(self, btn):
        self._run_async(["last", "-n", "10"])

    def on_system_info_clicked(self, btn):
        self._run_async(["uname", "-a"])

    def on_kernel_modules_clicked(self, btn):
        self._run_async(["lsmod"])

    def on_disk_inode_clicked(self, btn):
        self._run_async(["df", "-i"])

    def on_ip_route_clicked(self, btn):
        self._run_async(["ip", "route"])

    def on_dns_info_clicked(self, btn):
        with open("/etc/resolv.conf") as f:
            self._show(f.read())

    def on_boot_time_clicked(self, btn):
        self._run_async(["systemd-analyze"])

    def on_slowest_services_clicked(self, btn):
        self._run_async(["systemd-analyze", "blame"])

    def on_kernel_warnings_clicked(self, btn):
        def callback(output):
            self._show("\n".join(output.splitlines()[-50:]))
        self._run_async(["dmesg", "--level=err,warn", "-T"], callback)

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
        self._save_current_settings()

    def on_font_decrease_clicked(self, btn):
        self._font_size = max(self._font_size - 1, MIN_FONT_SIZE)
        self._apply_font_size()
        self._save_current_settings()

    def on_copy_output_clicked(self, btn):
        text = self.output_buffer.get_text(
            self.output_buffer.get_start_iter(), self.output_buffer.get_end_iter(), True
        )
        self.window.get_clipboard().set(text)

    def on_dark_mode_toggled(self, btn):
        style_manager = Adw.StyleManager.get_default()
        if btn.get_active():
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
        self._save_current_settings()

    def on_auto_refresh_toggled(self, btn):
        if btn.get_active():
            self._auto_refresh_id = GLib.timeout_add_seconds(2, self._auto_refresh_tick)
        elif self._auto_refresh_id is not None:
            GLib.source_remove(self._auto_refresh_id)
            self._auto_refresh_id = None

    def _auto_refresh_tick(self):
        if self._command_running:
            return GLib.SOURCE_CONTINUE
        self._show(execute(["free", "-h"]))
        return GLib.SOURCE_CONTINUE
