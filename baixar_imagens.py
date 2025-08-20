import os
import json
import requests

IMAGES_DIR = "imagens"
JSON_PATH = "cartas.json"

# Cria a pasta se não existir
os.makedirs(IMAGES_DIR, exist_ok=True)

with open(JSON_PATH, encoding="utf-8") as f:
    cartas = json.load(f)

for carta in cartas:
    url = carta.get("image")
    if not url:
        continue
    nome_arquivo = url.split("/")[-1]
    caminho_arquivo = os.path.join(IMAGES_DIR, nome_arquivo)
    # Baixa a imagem se não existir
    if not os.path.exists(caminho_arquivo):
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(caminho_arquivo, "wb") as imgf:
                imgf.write(resp.content)
    # Atualiza o campo image para o caminho local
    carta["image"] = os.path.join(IMAGES_DIR, nome_arquivo)

# Salva o JSON atualizado
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(cartas, f, ensure_ascii=False, indent=2)

print(f"Imagens baixadas e JSON atualizado.")
