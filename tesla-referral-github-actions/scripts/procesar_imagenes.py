import os
import requests
import base64
import time

REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

INPUT_FOLDER = "assets"
OUTPUT_FOLDER = "assets-editados"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
        "version": "9280fe26d34fa4f8c85593b8e4b9ba83de5f1c33e665947cecc17d3c3c47f8c2",  # Real-ESRGAN
        "input": {
            "image": f"data:image/png;base64,{b64_img}"
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 201:
        print(f"Replicate init error: {response.status_code} - {response.text}")
        return False

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    # Poll for completion
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
            print("Replicate failed.")
            return False
        time.sleep(5)

    print("Replicate timed out.")
    return False

for filename in os.listdir(INPUT_FOLDER):
    name, ext = os.path.splitext(filename)
    if ext.lower() not in [".jpg", ".jpeg", ".png"]:
        continue

    input_path = os.path.join(INPUT_FOLDER, filename)
    temp_output = os.path.join(OUTPUT_FOLDER, f"{name}-nobg.png")
    final_output = os.path.join(OUTPUT_FOLDER, f"{name}-upscaled.png")

    if os.path.exists(final_output):
        print(f"Ya procesada: {final_output}")
        continue

    print(f"Procesando {filename}...")

    if quitar_fondo(input_path, temp_output):
        upscale_imagen(temp_output, final_output)
