import subprocess


def execute(cmd):
    try:
        proc = subprocess.run(cmd, capture_output=True)
    except FileNotFoundError:
        return f"Hata: '{cmd[0]}' komutu bulunamadı."
    except OSError as e:
        return f"Hata: {e}"

    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        combined = (out + err).strip()
        return combined or f"Hata: komut {proc.returncode} koduyla sonlandı."

    return out or "(çıktı yok)"
