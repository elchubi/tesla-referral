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

def convertir_a_png(input_path):
    name, _ = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(OUTPUT_FOLDER, f"{name}-converted.png")
    try:
        with Image.open(input_path) as img:
            img.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Error al convertir {input_path} a PNG: {e}")
        return None

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

def upscale_imagen(input_path, output_path):
    with open(input_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "9280fe26d34fa4f8c85593b8e4b9ba83de5f1c33e665947cecc17d3c3c47f8c2",
        "input": {
            "image": f"data:image/png;base64,{b64_img}"
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 201:
        print(f"Replicate upscale error: {response.status_code} - {response.text}")
        return False

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    for _ in range(10):
        poll = requests.get(prediction_url, headers=headers)
        result = poll.json()
        if result["status"] == "succeeded":
            image_url = result["output"]
            img_data = requests.get(image_url).content
            with open(output_path, "wb") as f:
                f.write(img_data)
            return True
        elif result["status"] == "failed":
            print("Upscale falló.")
            return False
        time.sleep(5)

    print("Upscale timeout.")
    return False

def arte_digital(input_path, output_path):
    with open(input_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "6a9f6d70a6c5a1e6917a19d3fe42b15d2b52f239154a3fc49ccde0d70c2cfc3c",
        "input": {
            "image": f"data:image/png;base64,{b64_img}",
            "prompt": "professional digital portrait, clean lighting, sharp focus"
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 201:
        print(f"Replicate arte error: {response.status_code} - {response.text}")
        return False

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    for _ in range(12):
        poll = requests.get(prediction_url, headers=headers)
        result = poll.json()
        if result["status"] == "succeeded":
            image_url = result["output"]
            img_data = requests.get(image_url).content
            with open(output_path, "wb") as f:
                f.write(img_data)
            return True
        elif result["status"] == "failed":
            print("Arte falló.")
            return False
        time.sleep(5)

    print("Arte timeout.")
    return False

for filename in os.listdir(INPUT_FOLDER):
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".avif"]:
        continue

    raw_path = os.path.join(INPUT_FOLDER, filename)
    converted_path = raw_path

    if ext in [".webp", ".avif"]:
        converted_path = convertir_a_png(raw_path)
        if not converted_path:
            continue

    temp_nobg = os.path.join(OUTPUT_FOLDER, f"{name}-nobg.png")
    temp_upscaled = os.path.join(OUTPUT_FOLDER, f"{name}-upscaled.png")
    temp_artistic = os.path.join(OUTPUT_FOLDER, f"{name}-artistic.png")

    if os.path.exists(temp_artistic):
        print(f"{temp_artistic} ya existe, se omite.")
        continue

    print(f"Procesando: {filename}")

    if quitar_fondo(converted_path, temp_nobg):
        if upscale_imagen(temp_nobg, temp_upscaled):
            arte_digital(temp_upscaled, temp_artistic)
