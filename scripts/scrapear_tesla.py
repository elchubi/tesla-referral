import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

BASE_URLS = [
    "https://www.tesla.com/model3",
    "https://www.tesla.com/modely",
    "https://www.tesla.com/modelx",
    "https://www.tesla.com/models",
    "https://www.tesla.com/cybertruck"
]

OUTPUT_FOLDER = "assets"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def es_url_valida(url):
    ext = url.split("?")[0].split(".")[-1].lower()
    return ext in ["jpg", "jpeg", "png", "webp", "avif"]

def contiene_hero(url):
    return "hero" in url.lower()

def descargar_imagen(url, nombre):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        ruta = os.path.join(OUTPUT_FOLDER, nombre)
        with open(ruta, "wb") as f:
            f.write(response.content)
        print(f"✅ Guardada: {ruta}")
    except Exception as e:
        print(f"❌ Error al descargar {url}: {e}")

def procesar_pagina(url_base):
    print(f"\n🌐 Accediendo a {url_base}")
    try:
        response = requests.get(url_base, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        imgs = soup.find_all("img")

        for img in imgs:
            src = img.get("src")
            if not src:
                continue

            src_abs = urljoin(url_base, src)
            if contiene_hero(src_abs) and es_url_valida(src_abs):
                nombre = Path(src_abs).name.split("?")[0]
                descargar_imagen(src_abs, nombre)
        time.sleep(2)  # Espera para evitar ser bloqueado
    except Exception as e:
        print(f"❌ Error al obtener {url_base}: {e}")

# === Ejecutar ===
for url in BASE_URLS:
    procesar_pagina(url)
