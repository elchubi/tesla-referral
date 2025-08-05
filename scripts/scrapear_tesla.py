# scripts/scrapear_tesla.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import requests

URLS = {
    "model3": "https://www.tesla.com/model3",
    "modely": "https://www.tesla.com/modely",
    "models": "https://www.tesla.com/models",
    "modelx": "https://www.tesla.com/modelx",
    "cybertruck": "https://www.tesla.com/cybertruck",
}

OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def descargar_imagen(url, filename):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"✅ Imagen guardada: {path}")
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for modelo, url in URLS.items():
        print(f"\n🌐 Accediendo a {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(7000)  # esperar carga de JS

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            imagenes = set()

            # Buscar en src, srcset y data-iesrc
            for tag in soup.find_all(["img", "source", "picture"]):
                for attr in ["src", "srcset", "data-iesrc"]:
                    val = tag.get(attr)
                    if val and "hero" in val.lower():
                        for candidate in val.split(","):
                            candidate_url = candidate.strip().split(" ")[0]
                            if candidate_url.startswith("http") and "hero" in candidate_url.lower():
                                imagenes.add(candidate_url)

            if not imagenes:
                print("⚠️  No se encontraron imágenes con 'hero'")
                continue

            for i, img_url in enumerate(imagenes):
                ext = os.path.splitext(img_url)[1].split("?")[0] or ".png"
                filename = f"{modelo}-{i+1}{ext}"
                descargar_imagen(img_url, filename)

        except Exception as e:
            print(f"❌ Error procesando {url}: {e}")

    browser.close()
