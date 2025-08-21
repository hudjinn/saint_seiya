import os
import json
import cv2
import numpy as np
import easyocr
from PIL import Image


IMAGES_DIR = "imagens"
MASKS_DIR = "imagens_mascaras"
OUTPUT_DIR = "imagens_sem_texto"
JSON_PATH = "cartas.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(JSON_PATH, encoding="utf-8") as f:
    cartas = json.load(f)

reader = easyocr.Reader(['fr', 'en'], gpu=True)

def save_text_mask(image_path, mask_path, expand_x=20):
    img = cv2.imread(image_path)
    if img is None:
        return False
    results = reader.readtext(image_path)
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    expand_y_bottom = 8  # pixels extras para baixo
    for (bbox, text, conf) in results:
        poly = np.array(bbox, dtype=np.int32)
        x, y, x2, y2 = poly[:,0].min(), poly[:,1].min(), poly[:,0].max(), poly[:,1].max()
        # Expande a caixa para baixo
        y2_exp = min(h, y2 + expand_y_bottom)
        roi = img[y:y2_exp, x:x2]
        if roi.size == 0:
            continue
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Binarização adaptativa menos agressiva
        local_mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 8)
        # Filtro de mediana para suavizar
        local_mask = cv2.medianBlur(local_mask, 3)
        # Máscara do polígono
        poly_local = poly - [x, y]
        # Ajusta o polígono para a nova altura expandida
        poly_local_exp = poly_local.copy()
        poly_local_exp[poly_local_exp[:,1] == (y2 - y), 1] = (y2_exp - y)
        poly_mask = np.zeros_like(local_mask)
        cv2.fillPoly(poly_mask, [poly_local_exp], 255)
        # Aplica a máscara do polígono sobre a binarização
        local_mask = cv2.bitwise_and(local_mask, poly_mask)
        # Operação de abertura para remover ruído
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
        local_mask = cv2.morphologyEx(local_mask, cv2.MORPH_OPEN, kernel_open)
        # Cola na máscara global
        mask[y:y2_exp, x:x2] = cv2.bitwise_or(mask[y:y2_exp, x:x2], local_mask)
    # Suaviza e amplia a máscara final
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 1))
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (7, 1), 0)
    # Remoção de pequenos ruídos
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_clean)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_clean)
    return mask


# Função para inpainting clássico com OpenCV
def classic_inpaint(input_img, mask_img, output_img):
    img = cv2.imread(input_img)
    mask = cv2.imread(mask_img, 0)
    if img is None or mask is None:
        print(f"Erro ao ler {input_img} ou {mask_img}")
        return False
    # Inpainting com o método Telea (rápido e natural para áreas pequenas)
    result = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    cv2.imwrite(output_img, result)
    print(f"Salvo: {output_img}")
    return True

for carta in cartas:
    img_path = carta.get("image")
    if not img_path or not os.path.exists(img_path):
        continue
    img_path_abs = os.path.abspath(img_path)
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    out_path_abs = os.path.join(OUTPUT_DIR, f"{base_name}.webp")
    mask = save_text_mask(img_path_abs, None)
    if mask is False or np.count_nonzero(mask) == 0:
        continue
    # Chama o inpaint diretamente com a máscara em memória
    img = cv2.imread(img_path_abs)
    if img is None:
        continue
    result = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    cv2.imwrite(out_path_abs, result)
    print(f"Imagem final salva: {out_path_abs}")
print("Imagens prontas geradas em imagens_sem_texto.")
