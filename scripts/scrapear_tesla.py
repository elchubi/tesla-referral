import os
import time
from pathlib import Path
from urllib.parse import urljoin
from requests_html import HTMLSession

BASE_URLS = [
    "https://www.tesla.com/model3",
    "https://www.tesla.com/modely",
    "https://www.tesla.com/modelx",
    "https://www.tesla.com/models",
    "https://www.tesla.com/cybertruck"
]

OUTPUT_FOLDER = "assets"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

session = HTMLSession()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
})

def es_url_valida(url):
    ext = url.split("?")[0].split(".")[-1].lower()
    return ext in ["jpg", "jpeg", "png", "webp", "avif"]

def contiene_hero(url):
    return "hero" in url.lower()

def descargar_imagen(url, nombre):
    try:
        r = session.get(url)
        r.raise_for_status()
        ruta = os.path.join(OUTPUT_FOLDER, nombre)
        with open(ruta, "wb") as f:
            f.write(r.content)
        print(f"✅ Guardada: {ruta}")
    except Exception as e:
        print(f"❌ Error al descargar {url}: {e}")

def procesar_pagina(url_base):
    print(f"\n🌐 Accediendo a {url_base}")
    try:
        r = session.get(url_base)
        r.html.render(timeout=20, sleep=2)
        imgs = r.html.find("img")

        for img in imgs:
            src = img.attrs.get("src")
            if not src:
                continue
            full_url = urljoin(url_base, src)
            if contiene_hero(full_url) and es_url_valida(full_url):
                nombre = Path(full_url).name.split("?")[0]
                descargar_imagen(full_url, nombre)

        time.sleep(2)
    except Exception as e:
        print(f"❌ Error al obtener {url_base}: {e}")

# === Ejecutar ===
for url in BASE_URLS:
    procesar_pagina(url)
