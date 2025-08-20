import os
import json
import cv2
import numpy as np
import easyocr
from PIL import Image

IMAGES_DIR = "imagens"
OUTPUT_DIR = "imagens_sem_texto"
JSON_PATH = "cartas.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(JSON_PATH, encoding="utf-8") as f:
    cartas = json.load(f)

reader = easyocr.Reader(['fr', 'en'], gpu=True)

def remove_text_from_image(image_path, output_path):
    img = cv2.imread(image_path)
    if img is None:
        return False
    results = reader.readtext(image_path)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for (bbox, text, conf) in results:
        (tl, tr, br, bl) = bbox
        pts = np.array([tl, tr, br, bl], dtype=np.int32)
        cv2.fillPoly(mask, [pts], 255)
    inpainted = cv2.inpaint(img, mask, 7, cv2.INPAINT_TELEA)
    cv2.imwrite(output_path, inpainted)
    return True

for carta in cartas:
    img_path = carta.get("image")
    if not img_path or not os.path.exists(img_path):
        continue
    out_path = os.path.join(OUTPUT_DIR, os.path.basename(img_path))
    remove_text_from_image(img_path, out_path)

print("Imagens sem texto geradas em imagens_sem_texto.")
