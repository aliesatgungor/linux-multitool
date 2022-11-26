import gi
import time
import datetime
import subprocess



gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio



class MainWindow:

    def __init__(self, app):

        self.builder = Gtk.Builder()


        self.builder.add_from_file("MainWindow.glade")
        self.builder.connect_signals(self)


        self.window = self.builder.get_object("window")
        self.window.set_application(app)
        

        self.defineComponents()
        

        self.window.show_all()
    
    def defineComponents(self):
        self.output_label = self.builder.get_object("output_label")

    def on_free_ram_clicked(self, btn):
        process = subprocess.run(["free","-h"], capture_output=True)
        output = process.stdout.decode("utf-8")
        
        self.output_label.set_label(output)

    def on_clean_cache_clicked(self, btn):
        komut = "pkexec sh -c 'echo 3 >  /proc/sys/vm/drop_caches'  "
        process = subprocess.run(komut.split(),capture_output=True)
        output = process.stdout.decode("utf-8")
        o = "Tamamlandı!"
        self.output_label.set_label(o)

    def on_kernel_version_clicked(self, btn):
        process = subprocess.run(["uname","-r"], capture_output=True)
        output = process.stdout.decode("utf-8")
        
        self.output_label.set_label(output)
    def on_sistemi_kapat_clicked(self,btn):
        komut = "systemctl poweroff -i"
        process = subprocess.run(komut.split(),capture_output=True)    
        output = process.stdout.decode("utf-8")

        self.output_label.set_label(output)
    def on_reboot_clicked(self,btn):
        komut = "systemctl reboot now"
        process = subprocess.run(komut.split(),capture_output= True)
        output = process.stdout.decode("utf-8") 
        self.output_label.set_label(output)   
    def on_logout_clicked(self,btn):
        komut = "logout"
        process = subprocess.run(komut.split(),capture_output=True)
        output = process.stdout.decode("utf-8")   
        self.output_label.set_label(output) 
    def on_username_clicked(self,btn):
        komut = "whoami"
        process = subprocess.run(komut.split(),capture_output=True) 
        output = process.stdout.decode("utf-8")  
        self.output_label.set_label(output) 
    def on_disc_usage_clicked(self,btn):
        komut = "df -h"
        process = subprocess.run(komut.split(),capture_output=True)    
        output = process.stdout.decode("utf-8")
        self.output_label.set_label(output)