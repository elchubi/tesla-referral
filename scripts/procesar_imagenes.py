import os
import base64
import time
import requests
from PIL import Image

# === Config ===
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

INPUT_FOLDER = "assets"
OUTPUT_FOLDER = "assets-editados"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Funciones ===

def convertir_avif_a_png(input_path, output_path):
    try:
        with Image.open(input_path) as im:
            im.save(output_path, "PNG")
        print(f"Convertido AVIF a PNG: {output_path}")
        return True
    except Exception as e:
        print(f"Error convirtiendo AVIF: {e}")
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
        print(f"Fondo eliminado: {output_path}")
        return True
    else:
        print(f"Remove.bg error: {response.status_code} - {response.text}")
        return False

def esperar_resultado(prediction_url, headers):
    for _ in range(10):
        poll = requests.get(prediction_url, headers=headers)
        result = poll.json()
        if result["status"] == "succeeded":
            return result["output"]
        elif result["status"] == "failed":
            print("Replicate: procesamiento fallido.")
            return None
        time.sleep(5)
    print("Replicate: tiempo de espera agotado.")
    return None

def upscale_imagen(input_path, output_path):
    with open(input_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "version": "f94d7ed4a1f7e1ffed0d51e4089e4911609d5eeee5e874ef323d2c7562624bed",  # real-esrgan-a100
        "input": {
            "image": f"data:image/png;base64,{b64_img}",
            "face_enhance": True
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 201:
        print(f"Replicate upscale error: {response.status_code} - {response.text}")
        return False

    image_url = esperar_resultado(response.json()["urls"]["get"], headers)
    if not image_url:
        return False

    img_data = requests.get(image_url).content
    with open(output_path, "wb") as f:
        f.write(img_data)
    print(f"Imagen mejorada: {output_path}")
    return True

def aplicar_arte_digital(input_path, output_path):
    with open(input_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "version": "d3380ed57abbd6e14446d90542cf014da3777243d144b8d6a9cb9f0e7be6b0c4",  # model estilo retrato (portrait)
        "input": {
            "image": f"data:image/png;base64,{b64_img}"
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 201:
        print(f"Replicate arte error: {response.status_code} - {response.text}")
        return False

    image_url = esperar_resultado(response.json()["urls"]["get"], headers)
    if not image_url:
        return False

    img_data = requests.get(image_url).content
    with open(output_path, "wb") as f:
        f.write(img_data)
    print(f"Arte digital aplicado: {output_path}")
    return True

# === Proceso ===

for filename in os.listdir(INPUT_FOLDER):
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in [".png", ".jpg", ".jpeg", ".avif"]:
        continue

    input_path = os.path.join(INPUT_FOLDER, filename)
    converted_path = os.path.join(OUTPUT_FOLDER, f"{name}-converted.png") if ext == ".avif" else input_path
    nobg_path = os.path.join(OUTPUT_FOLDER, f"{name}-nobg.png")
    upscaled_path = os.path.join(OUTPUT_FOLDER, f"{name}-upscaled.png")
    final_output = os.path.join(OUTPUT_FOLDER, f"{name}-portrait.png")

    if os.path.exists(final_output):
        print(f"Ya procesada: {final_output}")
        continue

    print(f"Procesando {filename}...")

    # Convertir AVIF a PNG
    if ext == ".avif" and not convertir_avif_a_png(input_path, converted_path):
        continue

    if not quitar_fondo(converted_path, nobg_path):
        continue

    if not upscale_imagen(nobg_path, upscaled_path):
        continue

    aplicar_arte_digital(upscaled_path, final_output)
