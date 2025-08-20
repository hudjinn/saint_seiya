import os
import json
import requests

IMAGES_DIR = "imagens"
JSON_PATH = "cartas_fr.json"

os.makedirs(IMAGES_DIR, exist_ok=True)

with open(JSON_PATH, encoding="utf-8") as f:
    cartas = json.load(f)

# Baixar imagens das cartas
def baixar_imagem(url):
    if not url:
        return None
    # Se já é um caminho local, apenas retorna
    if not url.startswith("http"):
        return url
    nome_arquivo = url.split("/")[-1]
    caminho_arquivo = os.path.join(IMAGES_DIR, nome_arquivo)
    if not os.path.exists(caminho_arquivo):
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(caminho_arquivo, "wb") as imgf:
                imgf.write(resp.content)
    return os.path.join(IMAGES_DIR, nome_arquivo)

# Baixar e atualizar imagens das cartas e ícones dos efeitos
for carta in cartas:
    carta["image"] = baixar_imagem(carta.get("image"))
    for effect in carta.get("effects", []):
        local_icons = []
        for icon_url in effect.get("icons", []):
            local_icon = baixar_imagem(icon_url)
            local_icons.append(local_icon)
        effect["icons"] = local_icons

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(cartas, f, ensure_ascii=False, indent=2)

print("Imagens e ícones baixados e JSON atualizado.")
