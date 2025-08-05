import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Config
BASE_URL = "https://www.tesla.com"
MODEL_PATHS = ["/model3", "/modely", "/modelx", "/models", "/cybertruck"]
OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Regex para detectar "hero" en el nombre (sin importar posición o mayúsculas)
HERO_PATTERN = re.compile(r".*hero.*\.(jpg|jpeg|png|webp|avif)", re.IGNORECASE)

# Función para obtener imágenes de una página
def extraer_imagenes_de_modelo(path):
    url = urljoin(BASE_URL, path)
    print(f"Accediendo a {url}...")
    
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Error al obtener {url}: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    tags = soup.find_all(["img", "source"])

    for tag in tags:
        src = tag.get("src") or tag.get("srcset")
        if not src:
            continue

        if not HERO_PATTERN.search(src):
            continue

        # Construir URL absoluta si es necesario
        if src.startswith("/"):
            src = urljoin(BASE_URL, src)
        elif src.startswith("//"):
            src = "https:" + src

        filename = os.path.basename(src.split("?")[0])
        output_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(output_path):
            print(f"Ya descargada: {filename}")
            continue

        print(f"Descargando: {filename}...")
        try:
            img_data = requests.get(src, timeout=15).content
            with open(output_path, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"Error al descargar {src}: {e}")

# === MAIN ===
if __name__ == "__main__":
    for path in MODEL_PATHS:
        extraer_imagenes_de_modelo(path)
