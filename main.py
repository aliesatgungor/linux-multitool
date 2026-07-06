#!/usr/bin/env python3

import sys

import gi

try:
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gio, Adw
except (ValueError, ImportError):
    sys.exit(
        "GTK4 veya Libadwaita bulunamadı. Lütfen dağıtımınızda "
        "'gir1.2-gtk-4.0' ve 'gir1.2-adw-1' (veya karşılıklarını) kurun."
    )

from MainWindow import MainWindow


class Uygulama(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
            application_id="com.aliesatgungor.ilk",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
            **kwargs)
    
    def do_activate(self): # do_active metodu program açıldığında çalışır.
        self.window = MainWindow(self) # MainWindow nesnemizi oluşturduk.
        # Burada sadece oluşturmamız yeterli çünkü göstermeyi MainWindow'un içinde yaptık.

# Uygulama nesnemizi olusturup calistiralim.
app = Uygulama()
app.run(sys.argv)