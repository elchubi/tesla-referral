import os
import requests
import zipfile
import hashlib
import shutil
import tempfile
import json
from datetime import datetime

GALERIA_URLS = [
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-cybercab.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-new-model-y.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-model-s.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-cybertruck.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-model-3-performance.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-roadster.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-model-3-2024.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-model-x.zip",
    "https://digitalassets.tesla.com/tesla-contents/raw/upload/tesla-gallery-group.zip"
]

CACHE_FILE = "cache/hashes.json"
ASSETS_DIR = "assets"
GALERIA_JSON = os.path.join(ASSETS_DIR, "galeria.json")

def sha256sum(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(data):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_galeria():
    if os.path.exists(GALERIA_JSON):
        with open(GALERIA_JSON, "r") as f:
            return json.load(f)
    return []

def save_galeria(entries):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(GALERIA_JSON, "w") as f:
        json.dump(entries, f, indent=2)

def descargar_y_procesar_zip(url, cache, galeria_entries):
    print(f"⬇️  Descargando: {url}")
    with tempfile.TemporaryDirectory() as tempdir:
        local_zip = os.path.join(tempdir, "galeria.zip")

        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(local_zip, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        with zipfile.ZipFile(local_zip, 'r') as zip_ref:
            zip_ref.extractall(tempdir)

        nuevas = 0
        for root, _, files in os.walk(tempdir):
            for name in files:
                if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    continue
                full_path = os.path.join(root, name)
                file_hash = sha256sum(full_path)

                if file_hash not in cache:
                    print(f"🆕 Nueva imagen: {name}")
                    os.makedirs(ASSETS_DIR, exist_ok=True)
                    destino = os.path.join(ASSETS_DIR, name)
                    shutil.copy2(full_path, destino)
                    cache[file_hash] = name
                    galeria_entries.append({
                        "filename": name,
                        "hash": file_hash,
                        "fecha_adicion": datetime.utcnow().isoformat(),
                        "origen_zip": os.path.basename(url)
                    })
                    nuevas += 1

        print(f"✅ {nuevas} imágenes nuevas copiadas desde {os.path.basename(url)}.\n")

def main():
    cache = load_cache()
    galeria = load_galeria()

    for url in GALERIA_URLS:
        try:
            descargar_y_procesar_zip(url, cache, galeria)
        except Exception as e:
            print(f"❌ Error procesando {url}: {e}")

    save_cache(cache)
    save_galeria(galeria)
    print(f"🗂️  Galería JSON generada con {len(galeria)} imágenes.")
    print("🏁 Proceso finalizado.")

if __name__ == "__main__":
    main()
