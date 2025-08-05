import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from io import BytesIO

TESLA_GALLERY_URL = "https://www.tesla.com/es_MX/tesla-gallery"
OUTPUT_DIR = "assets"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Accediendo a {TESLA_GALLERY_URL}")
resp = requests.get(TESLA_GALLERY_URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")
links = soup.find_all("a", href=True)

zip_links = [link['href'] for link in links if link['href'].lower().endswith(".zip")]

if not zip_links:
    print("⚠️ No se encontraron archivos .zip")
else:
    for zip_url in zip_links:
        full_url = zip_url if zip_url.startswith("http") else f"https://www.tesla.com{zip_url}"
        filename = os.path.basename(full_url)
        folder_name = filename.replace(".zip", "").lower().replace("-", "_")

        print(f"⬇️ Descargando {filename}...")
        zip_resp = requests.get(full_url)
        zip_resp.raise_for_status()

        model_dir = os.path.join(OUTPUT_DIR, folder_name)
        os.makedirs(model_dir, exist_ok=True)

        with ZipFile(BytesIO(zip_resp.content)) as zip_file:
            zip_file.extractall(model_dir)

        print(f"✅ Extraído en: {model_dir}")
