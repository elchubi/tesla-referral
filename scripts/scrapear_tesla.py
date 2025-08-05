import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

MODELOS = {
    "model3": "https://www.tesla.com/model3",
    "modely": "https://www.tesla.com/modely",
    "models": "https://www.tesla.com/models",
    "modelx": "https://www.tesla.com/modelx",
    "cybertruck": "https://www.tesla.com/cybertruck"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36"
}

OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def descargar_imagen(url, nombre):
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            path = os.path.join(OUTPUT_DIR, nombre)
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"📥 Descargada: {nombre}")
        else:
            print(f"⚠️ Error descargando {url} - Código {r.status_code}")
    except Exception as e:
        print(f"❌ Excepción descargando imagen: {e}")

for modelo, url in MODELOS.items():
    print(f"🔎 Scrapeando {modelo}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("srcset")
            if not src:
                continue

            if "hero" in src.lower() and not src.startswith("data:"):
                full_url = urljoin(url, src)
                ext = full_url.split(".")[-1].split("?")[0]
                nombre_archivo = f"{modelo}-" + full_url.split("/")[-1].split("?")[0]
                descargar_imagen(full_url, nombre_archivo)
    except Exception as e:
        print(f"❌ Error con {modelo}: {e}")
