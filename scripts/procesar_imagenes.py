import os
import requests
import base64
import time
from PIL import Image

REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

INPUT_FOLDER = "assets"
OUTPUT_FOLDER = "assets-editados"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convertir_avif_a_png(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"Error al convertir AVIF: {e}")
        return False

def quitar_fondo(input_path, output_path):
    with open(input_path, "rb") as image_file:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": image_file},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY},
        )
    if response.status_code == 200:
        with open(output_path, "wb") as out:
            out.write(response.content)
        return True
    else:
        print(f"Remove.bg error: {response.status_code} - {response.text}")
        return False

def ejecutar_replicate(image_path, version):
    with open(image_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": version,
        "input": {
            "image": f"data:image/png;base64,{b64_img}"
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 201:
        print(f"Replicate error: {response.status_code} - {response.text}")
        return None

    prediction_url = response.json()["urls"]["get"]

    # Poll hasta que termine
    for _ in range(20):
        poll = requests.get(prediction_url, headers=headers)
        result = poll.json()
        if result["status"] == "succeeded":
            return result["output"]
        elif result["status"] == "failed":
            print("Replicate falló.")
            return None
        time.sleep(3)

    print("Replicate se tardó demasiado.")
    return None

def descargar_imagen(url, output_path):
    img_data = requests.get(url).content
    with open(output_path, "wb") as f:
        f.write(img_data)

for filename in os.listdir(INPUT_FOLDER):
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".avif"]:
        continue

    input_path = os.path.join(INPUT_FOLDER, filename)

    # 1. Convertir AVIF a PNG si aplica
    if ext == ".avif":
        converted_path = os.path.join(OUTPUT_FOLDER, f"{name}-converted.png")
        if convertir_avif_a_png(input_path, converted_path):
            input_path = converted_path
        else:
            continue

    temp_nobg_path = os.path.join(OUTPUT_FOLDER, f"{name}-nobg.png")
    upscale_path = os.path.join(OUTPUT_FOLDER, f"{name}-upscaled.png")
    portrait_path = os.path.join(OUTPUT_FOLDER, f"{name}-portrait.png")

    if os.path.exists(portrait_path):
        print(f"Ya procesada: {portrait_path}")
        continue

    print(f"Procesando {filename}...")

    # 2. Quitar fondo
    if not os.path.exists(temp_nobg_path):
        if not quitar_fondo(input_path, temp_nobg_path):
            continue

    # 3. Upscale
    if not os.path.exists(upscale_path):
        output_url = ejecutar_replicate(
            temp_nobg_path,
            version="6a9f6d70a6c5a1e6917a19d3fe42b15d2b52f239154a3fc49ccde0d70c2cfc3c"  # Real-ESRGAN
        )
        if not output_url:
            continue
        descargar_imagen(output_url, upscale_path)

    # 4. Estilo artístico tipo retrato
    if not os.path.exists(portrait_path):
        output_url = ejecutar_replicate(
            upscale_path,
            version="2a1e7618e50fa826f63e07fa9fe4081337645b358fcf10ef83510f0cd38af50b"  # portrait-v1.0.1
        )
        if not output_url:
            continue
        descargar_imagen(output_url, portrait_path)

    print(f"✓ Imagen final guardada: {portrait_path}")
