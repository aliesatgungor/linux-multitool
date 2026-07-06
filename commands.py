import subprocess
import locale

# Simple translation catalog for commands.py
TRANSLATIONS = {
    "en": {
        "Hata: Yetkilendirme (Polkit) işlemi kullanıcı tarafından iptal edildi.": "Error: Authorization (Polkit) process was cancelled by the user.",
        "(çıktı yok)": "(no output)",
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


def execute(cmd):
    try:
        proc = subprocess.run(cmd, capture_output=True)
    except FileNotFoundError:
        return f"Error: Command '{cmd[0]}' not found." if lang_code == "en" else f"Hata: '{cmd[0]}' komutu bulunamadı."
    except OSError as e:
        return f"Error: {e}" if lang_code == "en" else f"Hata: {e}"

    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        if cmd[0] == "pkexec" and proc.returncode in (126, 127):
            return _("Hata: Yetkilendirme (Polkit) işlemi kullanıcı tarafından iptal edildi.")
        combined = (out + err).strip()
        if combined:
            return combined
        return f"Error: command terminated with code {proc.returncode}." if lang_code == "en" else f"Hata: komut {proc.returncode} koduyla sonlandı."

    return out or _("(çıktı yok)")
