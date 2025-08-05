# scripts/scrapear_tesla.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import requests

# === Configuración ===
URLS = {
    "model3": "https://www.tesla.com/model3",
    "modely": "https://www.tesla.com/modely",
    "models": "https://www.tesla.com/models",
    "modelx": "https://www.tesla.com/modelx",
    "cybertruck": "https://www.tesla.com/cybertruck",
}

OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Función para guardar imagen ===
def descargar_imagen(url, filename):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"✅ Imagen guardada: {path}")
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")

# === Proceso principal con Playwright ===
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for modelo, url in URLS.items():
        print(f"\n🌐 Accediendo a {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)  # Esperar 5 segundos para carga completa
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            imagenes = []

            # Buscar <img src=...>
            for img in soup.find_all("img"):
                src = img.get("src", "")
                if "hero" in src.lower():
                    imagenes.append(src)

            # Buscar <source srcset=...>
            for source in soup.find_all("source"):
                srcset = source.get("srcset", "")
                for candidate in srcset.split(","):
                    url_part = candidate.strip().split(" ")[0]
                    if "hero" in url_part.lower():
                        imagenes.append(url_part)

            if not imagenes:
                print("⚠️  No se encontraron imágenes con 'hero'")
                continue

            for i, img_url in enumerate(set(imagenes)):
                ext = os.path.splitext(img_url)[1].split("?")[0] or ".png"
                filename = f"{modelo}-{i+1}{ext}"
                descargar_imagen(img_url, filename)

        except Exception as e:
            print(f"❌ Error procesando {url}: {e}")

    browser.close()
