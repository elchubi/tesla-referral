import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL de la galería oficial de Tesla
GALERIA_URL = "https://www.tesla.com/es_MX/tesla-gallery"
OUTPUT_DIR = "output"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Quitar esto si deseas ver el navegador
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")
    return webdriver.Chrome(options=chrome_options)

def extraer_urls_imagenes(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.find_all("img")
    urls = []

    for img in imgs:
        src = img.get("src")
        if src and (".jpg" in src or ".png" in src):
            full_url = urljoin(base_url, src)
            urls.append(full_url)
    
    return list(set(urls))  # eliminar duplicados

def descargar_imagen(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nombre_archivo = url.split("/")[-1]
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)

    print(f"⬇️  {url}")
    try:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(resp.content)
        print(f"✅ Guardado como {ruta}")
    except Exception as e:
        print(f"❌ Error al descargar {url}: {e}")

def main():
    print(f"🌐 Accediendo a {GALERIA_URL}")
    driver = iniciar_driver()
    driver.get(GALERIA_URL)
    time.sleep(5)  # Espera por carga de JS

    html = driver.page_source
    driver.quit()

    print("🔍 Buscando imágenes...")
    urls = extraer_urls_imagenes(html, GALERIA_URL)

    print(f"📸 Se encontraron {len(urls)} imágenes.")
    for url in urls:
        descargar_imagen(url)

    print("🎉 Proceso completado.")

if __name__ == "__main__":
    main()
