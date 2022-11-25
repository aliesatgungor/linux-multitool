import time
import gi
import datetime
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio

import subprocess

class MainWindow:
    def __init__(self, app):
        # Gtk Builder
        self.builder = Gtk.Builder()

        # Import UI file:
        self.builder.add_from_file("MainWindow.glade")
        self.builder.connect_signals(self)

        # Window
        self.window = self.builder.get_object("window")
        self.window.set_application(app)
        
        # Glade'deki elemanlari kullanmak icin degiskene atayalim:
        self.defineComponents()
        
        # Show window
        self.window.show_all()
    
    def defineComponents(self):
        self.output_label = self.builder.get_object("output_label")
    
    def on_free_ram_clicked(self, btn):
        process = subprocess.run(["free","-h"], capture_output=True)
        output = process.stdout.decode("utf-8")
        
        self.output_label.set_label(output)
    
    def on_clean_cache_clicked(self, btn):
        process = subprocess.run(["echo", "4"," | ","tee"," /proc/sys/vm/drop_caches"], capture_output=True)
        process = subprocess.run(["echo", "3"," | ","tee"," /proc/sys/vm/drop_caches"], capture_output=True)
        time.sleep(0.1)
        process = subprocess.run(["echo", "0"," | ","tee"," /proc/sys/vm/drop_caches"], capture_output=True)
        output = process.stdout.decode("utf-8")
        o = "Tamamlandı!"
        self.output_label.set_label(o)
    def on_kernel_version_clicked(self, btn):
        process = subprocess.run(["uname","-r"], capture_output=True)
        output = process.stdout.decode("utf-8")
        
        self.output_label.set_label(output)
        