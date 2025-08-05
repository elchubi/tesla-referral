from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import os
import re

URLS = {
    "model3": "https://www.tesla.com/model3",
    "modely": "https://www.tesla.com/modely",
    "models": "https://www.tesla.com/models",
    "modelx": "https://www.tesla.com/modelx",
    "cybertruck": "https://www.tesla.com/cybertruck",
}

OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extraer_urls_con_hero(tag, attrs=["src", "srcset", "data-iesrc"]):
    urls = set()
    for attr in attrs:
        val = tag.get(attr)
        if not val:
            continue
        # Soporte para srcset con múltiples URLs separadas por coma
        parts = re.split(r",\s*", val)
        for part in parts:
            match = re.search(r"(https?://[^\s]+)", part)
            if match and "hero" in match.group(1).lower():
                clean_url = match.group(1).split()[0]
                urls.add(clean_url)
    return urls

def descargar_imagen(url, filename):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "wb") as f:
            f.write(resp.content)
        print(f"✅ Guardada: {filename}")
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for modelo, url in URLS.items():
        print(f"\n🌐 Accediendo a {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(7000)  # Esperar carga dinámica
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            all_urls = set()
            for tag in soup.find_all(["img", "source", "picture"]):
                all_urls.update(extraer_urls_con_hero(tag))

            if not all_urls:
                print("⚠️  No se encontraron imágenes con 'hero'")
                continue

            for i, img_url in enumerate(sorted(all_urls)):
                ext = os.path.splitext(img_url)[1].split("?")[0]
                if not ext:
                    ext = ".png"
                filename = f"{modelo}-{i+1}{ext}"
                descargar_imagen(img_url, filename)

        except Exception as e:
            print(f"❌ Error: {e}")

    browser.close()
