# scripts/scrapear_tesla.py

import os
import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URLS = [
    "https://www.tesla.com/model3",
    "https://www.tesla.com/modely",
    "https://www.tesla.com/models",
    "https://www.tesla.com/modelx",
    "https://www.tesla.com/cybertruck",
]

OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def descargar_imagen(url, nombre_archivo):
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(nombre_archivo, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"✅ Imagen guardada: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al descargar {url}: {e}")

def extraer_imagenes_con_hero(html):
    soup = BeautifulSoup(html, "html.parser")
    imagenes = set()

    # Buscar todos los tags que podrían tener imágenes
    for tag in soup.find_all(["img", "source"]):
        url = tag.get("src") or tag.get("srcset")
        if url and "hero" in url.lower():
            # Si srcset tiene múltiples entradas, separar
            if "," in url:
                for part in url.split(","):
                    clean_url = part.strip().split(" ")[0]
                    if "hero" in clean_url.lower():
                        imagenes.add(clean_url)
            else:
                imagenes.add(url)
    return imagenes

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    for url in URLS:
        print(f"🌐 Accediendo a {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)  # esperar 5 segundos
            html = page.content()
            imagenes = extraer_imagenes_con_hero(html)

            if not imagenes:
                print("⚠️  No se encontraron imágenes con 'hero'")
                continue

            for img_url in imagenes:
                nombre = img_url.split("/")[-1]
                path = os.path.join(OUTPUT_DIR, nombre)
                descargar_imagen(img_url, path)
        except Exception as e:
            print(f"❌ Error al obtener {url}: {e}")

    browser.close()
