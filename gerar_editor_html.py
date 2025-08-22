# --- NOVO GERADOR: Layout das cartas igual ao gerar_editor_old.py, instruções e recursos novos ---
import os
import json
import re
import unicodedata
from PIL import Image

IMAGES_DIR = "imagens_sem_texto"
IMAGES_ORIG_DIR = "imagens"
HTML_PATH = "index.html"
JSON_PATH = "cartas.json"

with open(JSON_PATH, encoding="utf-8") as f:
    cartas = json.load(f)

def get_aspect(img_path):
    try:
        with Image.open(img_path) as im:
            w, h = im.size
            return 'landscape' if w > h else 'portrait'
    except Exception:
        return 'portrait'

# Coletar keywords de efeitos a partir dos <em class="keyword ...">...</em> presentes nos efeitos das cartas
import html as htmlmod
efeito_keywords = set()
def extrair_keywords(texto):
    # Extrai todas as keywords do HTML do efeito
    return re.findall(r'<em class=["\']keyword(?: [^"\']*)?["\']>(.*?)</em>', texto)

for carta in cartas:
    efeitos = carta.get("effects")
    if efeitos and isinstance(efeitos, list):
        for ef in efeitos:
            html_efeito = None
            if isinstance(ef, dict):
                html_efeito = ef.get("html") or ef.get("text")
            elif isinstance(ef, str):
                html_efeito = ef
            if html_efeito:
                for kw in extrair_keywords(html_efeito):
                    kw = htmlmod.unescape(kw.strip())
                    if kw:
                        efeito_keywords.add(kw)
    else:
        efeito_fallback = carta.get("Efeito", "")
        for kw in extrair_keywords(efeito_fallback):
            kw = htmlmod.unescape(kw.strip())
            if kw:
                efeito_keywords.add(kw)
efeito_prefixos = sorted(efeito_keywords)

# --- HTML ---
html = """<!DOCTYPE html>
<html lang=\"pt-br\">
<head>
    <meta charset=\"UTF-8\">
    <title>Editor de Cartas Saint Seiya</title>
    <style>
        .carta.epop_e .edit-nome {
            color: #b4a79e;
        }
        body { font-family: Arial, sans-serif; background: #222; color: #eee; }
        .main-container { margin: 0 auto 24px auto; }
        .header-box { text-align: center; font-size: 1.18em; color: #ffe066; background: #222; padding: 16px 28px; border-radius: 14px; box-shadow: 0 0 14px #000; margin: 32px auto 24px auto; }
        .toolbar-box { text-align: center; margin-bottom: 24px; }
        .export-btn { background: linear-gradient(90deg,#ffe066 0%,#ffb347 100%); color: #222; font-weight: bold; font-size: 1.25em; border: 2.5px solid #ffb347; border-radius: 10px; padding: 12px 32px; margin: 0 18px 8px 0; box-shadow: 0 2px 12px #0008; letter-spacing: 1px; transition: filter .2s; cursor:pointer; }
        .import-btn { background: linear-gradient(90deg,#66e0ff 0%,#3ad29f 100%); color: #222; font-weight: bold; font-size: 1.25em; border: 2.5px solid #3ad29f; border-radius: 10px; padding: 12px 32px; margin: 0 0 8px 0; box-shadow: 0 2px 12px #0008; letter-spacing: 1px; transition: filter .2s; cursor:pointer; }
        .editar-pos-btn { background: #ffb347; color: #222; font-weight: bold; font-size: 1.1em; border: 2px solid #ffe066; border-radius: 8px; padding: 8px 22px; margin: 0 0 18px 0; box-shadow: 0 2px 12px #0008; letter-spacing: 1px; cursor:pointer; transition: filter .2s; }
        .editar-pos-info { display: block; color: #ffe066; font-size: 1.05em; margin-top: 8px; }
        #editar-pos-container { text-align: center; margin: 32px auto 18px auto; max-width: 900px; }
        .classes-lista { background: #181818; padding: 12px 18px; border-radius: 10px; margin: 0 auto 24px auto; }
        .classes-lista .row-container { display: flex; flex-wrap: wrap; gap: 20px 16px; justify-content: center; position: relative; }
        .classes-lista label { font-weight: bold; color: #ffe066; }
        .classes-lista input { width: 220px; margin: 0 12px 8px 0; border-radius: 4px; border: 1px solid #888; padding: 4px 8px; font-size: 1.15em; }
        .classes-lista .classe-row { margin-bottom: 6px; font-weight: 700; flex: 1 1 22%; max-width: 22%; min-width: 220px; background: #222; border-radius: 10px; padding: 18px 16px 10px 16px; box-shadow: 0 2px 12px #0006; display: flex; flex-direction: column; align-items: flex-start; box-sizing: border-box; }
        .efeitos-lista .efeito-btns { margin-top: 12px; }
        .efeitos-lista button { background: #4caf50; color: #fff; border: none; border-radius: 4px; padding: 6px 12px; cursor: pointer; margin-right: 8px; }
        .efeitos-lista input[type=file] { color: #fff; }
        .efeitos-lista .row-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px 16px;
            justify-content: center;
            position: relative;
        }
        .efeito-row {
            margin-bottom: 12px;
            font-weight: 700;
            flex: 0 0 31%;
            max-width: 340px;
            min-width: 300px;
            background: #222;
            border-radius: 10px;
            padding: 18px 16px 14px 16px;
            box-shadow: 0 2px 12px #0006;
            display: flex;
            flex-direction: row;
            align-items: center;
            box-sizing: border-box;
            position: relative;
        }
        .efeito-row input.efeito-trad {
            flex: 1 1 auto;
            min-width: 0;
            max-width: 120px;
            margin-right: 10px;
        }
        .efeito-row button.efeito-aplicar-btn {
            flex: 0 0 auto;
            margin-left: 0;
        }
    /* Botões de ação de posição do efeito são criados dinamicamente via JS */
    .efeito-pos-action-btns { display: flex; gap: 4px; margin-left: 6px; }
    .efeito-pos-action-btns button { background: #444; color: #fff; border-radius: 4px; border: none; padding: 0 8px; height: 22px; font-size: 1em; cursor: pointer; display: flex; align-items: center; justify-content: center; }
    .efeito-pos-action-btns .ok { background: linear-gradient(90deg,#2ecc40 0%,#27ae60 100%); }
    .efeito-pos-action-btns .cancel { background: linear-gradient(90deg,#e74c3c 0%,#c0392b 100%); }
    .efeito-pos-action-btns .reset { background: #888; }
    .efeito-pos-arrows { display: flex; flex-direction: row; gap: 2px; margin-left: 6px; }
    .efeito-pos-arrows button { background: #ffe066; color: #222; border: 1px solid #aaa; border-radius: 4px; font-size: 1em; padding: 0 4px; cursor: pointer; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; }
        .efeito-orig { color: #ff6666; font-style: normal; font-weight: bold; text-shadow: 1px 1px 4px #000; cursor: pointer; position: relative; }
        .efeito-carta-tooltip { display: none; position: fixed; z-index: 1000; background: #222; border: 2px solid #ffe066; border-radius: 10px; padding: 10px 10px 6px 10px; box-shadow: 0 8px 32px #000a; min-width: 320px; text-align: center; max-width: 420px; overflow: visible; }
        .efeito-carta-tooltip img { max-width: 320px; max-height: 460px; box-shadow: 0 0 16px #000; border-radius: 10px; border: 2px solid #ffe066; background: #222; }
        .carta { display: inline-block; margin: 24px; background: #333; padding: 12px; border-radius: 12px; vertical-align: top; box-shadow: 0 0 16px #000a; }
        .carta-imgbox { position: relative; margin-bottom: 0; }
        .carta.portrait .carta-imgbox { width: 350px; height: 500px; }
    .carta.landscape .carta-imgbox { width: 500px; height: 350px; }
    .carta-img { width: 100%; height: 100%; border-radius: 12px; box-shadow: 0 0 16px #000a; object-fit: cover; border: none; }
        .edit-nome {
            position: absolute;
            top: 2px;
            left: 0;
            right: 0;
            width: 90%;
            margin: 0 auto;
            color: #fff;
            border-radius: 8px;
            padding: 6px 8px 2px 8px;
            font-size: 1.4em;
            font-family: 'Arial', Arial, sans-serif;
            font-weight: bold;
            text-align: center;
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            outline: none;
        }
        .edit-classe { z-index: 20; position: absolute; top: 40px; left: 20px; width: 80%; background: rgba(0, 0, 0, 0.2); font-size: 0.8em; font-family: 'Georgia', serif; border: none; border-radius: 6px; padding: 2px 8px; outline: none; text-align: center; box-shadow: 0 1px 6px #0006; color: #fff; }
    .edit-classe { font-style: italic; }
    .edit-classe-landscape { width: 37% !important; }
        .efeitos-stack {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            font-family: 'Georgia', serif;
            font-size: 0.8em;
            color: #111;
            width: 85%;
            margin: 0 auto;
            position: absolute;
            bottom: 24px;
            left: 0;
            right: 0;
        }
        .carta.landscape .efeitos-stack,
        .carta.portrait .efeitos-stack,
        .carta.landscape.epop_e .efeitos-stack {
            width: 85%;
            margin: 0 auto;
            left: 0;
            right: 0;
        }
        .effect {
            font-family: 'NeoSansW01', sans-serif;
            border-radius: 8px;
            padding: 4px 10px;
            margin-bottom: 4px;
            display: inline-block;
        }
        /* Se a keyword findepartie estiver presente, deixa o texto da effect branco exceto a keyword */
        .effect:has(em.keyword.findepartie),
        .effect:has(em.keyword.findepartie),
        .effect:has(em.keyword.fin_de_partie),
        .effect:has(em.keyword.findepopee),
        .effect:has(em.keyword.fin_de_popee) {
            color: #fff !important;
            background: #060a0d !important;
        }
        .effect:has(em.keyword.findepartie) em.keyword.findepartie,
        .effect:has(em.keyword.fin_de_partie) em.keyword.fin_de_partie,
        .effect:has(em.keyword.findepopee) em.keyword.findepopee,
        .effect:has(em.keyword.fin_de_popee) em.keyword.fin_de_popee {
            color: #629732 !important;
            background: none !important;
        }
        .effect.play {
            background: #deccbb;
            color: #302d29;
        }
        .effect.ground {
            background: #1d1501;
            color: #fff;
        }
        .effect.passive {
            background: #eee6f9;
            color: #302d29;
        }
    /* Keywords especiais - cartas e lista */

    em.keyword {
        font-weight: bold;
    }
    .efeito-box em.keyword.arrivee,
    .efeitos-lista .efeito-row em.keyword.arrivee,
    .efeito-box em.keyword.miseenjeu,
    .efeitos-lista .efeito-row em.keyword.miseenjeu,
    .efeito-box em.keyword.talent,
    .efeitos-lista .efeito-row em.keyword.talent,
    .efeito-box em.keyword.apparition,
    .efeitos-lista .efeito-row em.keyword.apparition { color: #007dc6; }
    .efeito-box em.keyword.blesser,
    .efeitos-lista .efeito-row em.keyword.blesser,
    .efeito-box em.keyword.defausser,
    .efeitos-lista .efeito-row em.keyword.defausser,
    .efeito-box em.keyword.vaincu,
    .efeitos-lista .efeito-row em.keyword.vaincu,
    .efeito-box em.keyword.detruire,
    .efeitos-lista .efeito-row em.keyword.detruire,
    .efeito-box em.keyword.geler,
    .efeitos-lista .efeito-row em.keyword.geler,
    .efeito-box em.keyword.aneanti,
    .efeitos-lista .efeito-row em.keyword.aneanti,
    .efeito-box em.keyword.capacite,
    .efeitos-lista .efeito-row em.keyword.capacite { color: red; }
    .efeito-box em.keyword.marque,
    .efeitos-lista .efeito-row em.keyword.marque { color: purple; }
    .efeito-box em.keyword.sortie,
    .efeitos-lista .efeito-row em.keyword.sortie,
    .efeito-box em.keyword.findepopee,
    .efeitos-lista .efeito-row em.keyword.finedpopee,
    .efeito-box em.keyword.findepopee,
    .efeitos-lista .efeito-row em.keyword.findepopee { color: orange; }
    .efeito-box em.keyword.findepartie,
    .efeitos-lista .efeito-row em.keyword.findepartie,
    .efeito-box em.keyword.findepartie,
    .efeitos-lista .efeito-row em.keyword.findepartie { color: #629732; }

            color: #ff6666;
            font-style: normal;
            font-weight: bold;
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
        }
        .efeito-orig {
            color: #ff6666;
            font-style: normal;
            font-weight: bold;
        }
        .efeito-box .efeito-vaincu { color: #ffb84d; font-weight: bold; }
        .efeito-box .efeito-defausser { color: #ff4d4d; font-weight: bold; }
        .efeito-box .efeito-cosmos { color: #66b3ff; font-weight: bold; }
        .efeito-box .efeito-victoire { color: #ffe066; font-weight: bold; }
        .efeito-box .efeito-arrivee { color: #b3e6ff; font-weight: bold; }
        .efeito-box .custo { font-size: 1.1em; font-weight: bold; color: #ffe066; text-shadow: 1px 1px 4px #000; }
        .simbolo-btn { background: #222; color: #ffe066; border: 1px solid #ffe066; border-radius: 4px; padding: 2px 8px; font-size: 0.95em; margin-left: 6px; cursor: pointer; }
        /* --- Botões de referência e restaurar em coluna à direita --- */
        .carta-ref-restaurar-col { position: absolute; top: 8px; right: 8px; z-index: 20; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
        .carta-ref-icone { display: inline-block; width: 28px; height: 28px; background: #ffe066; border-radius: 50%; box-shadow: 0 0 6px #000; cursor: pointer; text-align: center; line-height: 28px; font-size: 1.2em; font-weight: bold; }
        .restaurar-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: #222; border-radius: 50%; color: #ffe066; border: 2px solid #ffe066; font-size: 1.2em; cursor: pointer; box-shadow: 0 0 6px #0006; margin-top: 0; }
        .restaurar-toolbar {
            display: none;
            position: absolute;
            top: 72px;
            right: -6px;
            z-index: 120;
            flex-direction: column;
            gap: 7px;
            background: #222;
            border-radius: 10px;
            box-shadow: 0 2px 12px #000a;
            padding: 8px 6px 6px 6px;
            align-items: flex-end;
        }
        .restaurar-toolbar button {
            font-size: 1em;
            font-weight: bold;
            border-radius: 7px;
            padding: 4px 12px;
            margin: 0 0 3px 0;
            box-shadow: 0 2px 8px #0006;
            cursor: pointer;
            transition: filter .2s;
            color: #fff;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .restaurar-toolbar .restaurar-ok {
            background: linear-gradient(90deg,#2ecc40 0%,#27ae60 100%);
        }
        .restaurar-toolbar .restaurar-cancel {
            background: linear-gradient(90deg,#e74c3c 0%,#c0392b 100%);
        }
        .restaurar-toolbar button:last-child {
            margin-bottom: 0;
        }
        .restaurar-preview { display: none; position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; z-index: 31; pointer-events: auto; background: rgba(0,0,0,0.0); }
        .restaurar-canvas { display: none; position: absolute; left: 0; top: 0; width: 100%; height: 100%; z-index: 99; pointer-events: auto; }
        /* Ícones cosmos e forca: width 22px; demais: width conforme HTML do JSON */
        .effect img[alt="Cosmos"], .effect img[alt="Force"] {
            width: 22px !important;
            height: 22px !important;
            vertical-align: middle;
        }
        /* Os demais ícones não terão width forçado, usarão o width do HTML do JSON */
        .effect img:not([alt="Cosmos"]):not([alt="Force"]) {
            vertical-align: middle;
        }

        /* Ícone de raio amarelo puro SVG para .icon-flash */
        .icon-flash {
            display: inline-block;
            width: 1em;
            height: 1.2em;
            vertical-align: middle;
            background: none;
            position: relative;
        }
        .icon-flash svg {
            width: 100%;
            height: 100%;
            display: block;
        }
        .restaurar-toolbar .restaurar-trash {
            background: linear-gradient(90deg,#b71c1c 0%,#f44336 100%);
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header-box">
            <b>Editor de Cartas Saint Seiya</b><br>
            Edite o <b>nome</b>, <b>classe</b> e <b>efeitos</b> de cada carta diretamente na lista abaixo.<br>
            Para traduzir rapidamente, utilize as caixas de tradução de <b>classes</b> e <b>efeitos globais</b> — ao alterar um termo, todas as cartas com aquele termo serão atualizadas automaticamente.<br>
            <span style="color:#b0e0ff;">Para restaurar partes da imagem original (ex: remover falhas da versão sem texto), clique no botão <span style="background:#ffe066;color:#222;padding:2px 8px;border-radius:5px;font-weight:bold;">✏️</span> na carta desejada, desenhe um retângulo sobre a área a restaurar e confirme com <b>✔</b> ou cancele com <b>✖</b>. A restauração é visual e não altera o arquivo original.</span><br>
            <span style="color:#ffe066;font-size:0.98em;">Use <b>Exportar JSON</b> para salvar seu progresso e <b>Importar JSON</b> para continuar depois.</span>
        </div>
        <div class="toolbar-box">
            <button type="button" onclick="exportarJson()" class="export-btn">⬇ Exportar JSON</button>
            <button type="button" onclick="document.getElementById('importar-arquivo').click()" class="import-btn">⬆ Importar JSON</button>
            <input type="file" id="importar-arquivo" style="display:none" accept="application/json" onchange="importarJson(event)">
        </div>
        <div class="classes-lista">
            <h2>Tradução de Classes Comuns</h2>
            <form id="classes-form">
"""
# Lista de classes para tradução
classes_unicas = sorted(set(c["Classe"] for c in cartas if c.get("Classe")))
# Mapeia cada classe para uma carta de exemplo
classe_para_carta = {}
for classe in classes_unicas:
    for carta in cartas:
        if carta.get("Classe") == classe:
            classe_para_carta[classe] = carta
            break
html += '<div class="row-container">'
for classe in classes_unicas:
    carta_exemplo = classe_para_carta.get(classe)
    if carta_exemplo:
        img_exemplo = os.path.join(IMAGES_ORIG_DIR, os.path.basename(carta_exemplo["image"]))
        nome_exemplo = carta_exemplo["Nome"]
        html += f"""<div class="classe-row">
            <span class="classe-orig classe-hover">{classe}
                <span class="classe-carta-tooltip" style="display:none;position:absolute;left:0;top:28px;z-index:1000;background:#222;border:2px solid #ffe066;border-radius:10px;padding:10px 10px 6px 10px;box-shadow:0 8px 32px #000a;min-width:320px;text-align:center;max-width:420px;overflow:visible;">
                    <img src="{img_exemplo}" alt="{nome_exemplo}" style="max-width:320px;max-height:460px;box-shadow:0 0 16px #000;border-radius:10px;border:2px solid #ffe066;background:#222;"><br>
                    <span style="color:#ffe066;font-size:1.1em;font-weight:bold;">{nome_exemplo}</span>
                </span>
            </span>
            <input type="text" class="classe-trad" data-orig="{classe}" value="{classe}">
        </div>\n"""
    else:
        html += f"""<div class="classe-row">
            <span class="classe-orig">{classe}</span>
            <input type="text" class="classe-trad" data-orig="{classe}" value="{classe}">
        </div>\n"""
html += '</div>'
html += """
    <!-- Botões removidos daqui -->
        </form>
    </div>
    <div class="efeitos-lista">
        <h2>Tradução de Efeitos Globais</h2>
        <form id="efeitos-form">
"""
# Lista de efeitos para tradução
html += '<div class="row-container">'
efeito_para_carta = {}
def normaliza_kw(s):
    # Remove acentos, minúsculas, tira espaços e underscores
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.lower().replace(' ', '').replace('_', '')

for kw in efeito_prefixos:
    carta_exemplo = None
    kw_norm = normaliza_kw(kw)
    for carta in cartas:
        efeitos = carta.get("effects")
        textos = []
        if efeitos and isinstance(efeitos, list):
            for ef in efeitos:
                html_efeito = None
                if isinstance(ef, dict):
                    html_efeito = ef.get("html") or ef.get("text")
                elif isinstance(ef, str):
                    html_efeito = ef
                if html_efeito:
                    textos.append(html_efeito)
        else:
            efeito_fallback = carta.get("Efeito", "")
            if efeito_fallback:
                textos.append(efeito_fallback)
        for texto in textos:
            for found_kw in extrair_keywords(texto):
                if normaliza_kw(found_kw) == kw_norm:
                    carta_exemplo = carta
                    break
            if carta_exemplo:
                break
        if carta_exemplo:
            break
    if carta_exemplo:
        img_exemplo = os.path.join(IMAGES_ORIG_DIR, os.path.basename(carta_exemplo["image"]))
        nome_exemplo = carta_exemplo["Nome"]
        # Determina a cor de fundo e texto da keyword (igual ao CSS das cartas)
        def cor_keyword(kw):
            def norm(s):
                import unicodedata
                s = unicodedata.normalize('NFKD', s)
                s = ''.join(c for c in s if not unicodedata.combining(c))
                return s.lower().replace(' ', '').replace('_', '')
            kw_norm = norm(kw)
            # Tons mais neutros e suaves, sem text-shadow
            if kw_norm in ["arrivee", "miseenjeu", "talent", "apparition"]:
                return "background:#1d1501;color:#007dc6;"
            if kw_norm in ["blesser", "defausser", "vaincu", "detruire", "geler", "aneanti", "capacite"]:
                return "background:#ffe3e3;color:#b71c1c;"
            if kw_norm in ["marque"]:
                return "background:#ede3ff;color:#7c3aed;"
            if kw_norm in ["sortie", "findepopee"]:
                return "background:#fff2db;color:orange;"
            if kw_norm in ["findepartie"]:
                return "background:#e3ffe3;color:#388e3c;"
            return "background:#f4f4f4;color:#222;"

        html += f"""<div class=\"efeito-row\">
            <span class=\"efeito-orig efeito-hover\"><em class=\"keyword {kw.lower().replace(' ', '_')}\" style=\"display:inline-block;padding:2px 10px;margin-right:14px;border-radius:7px;font-style:normal;font-weight:bold;text-shadow:none;{cor_keyword(kw)}\">{kw}</em>
                <span class=\"efeito-carta-tooltip\"><img src=\"{img_exemplo}\" alt=\"{nome_exemplo}\" style=\"max-width:320px;max-height:460px;box-shadow:0 0 16px #000;border-radius:10px;border:2px solid #ffe066;background:#222;\"><br><span style=\"color:#ffe066;font-size:1.1em;font-weight:bold;\">{nome_exemplo}</span></span>
            </span>
            <input type=\"text\" class=\"efeito-trad\" data-orig=\"{kw}\" value=\"{kw}\">
            <button type=\"button\" class=\"efeito-aplicar-btn\" data-orig=\"{kw}\">Aplicar</button>
        </div>\n"""
    else:
        html += f"""<div class=\"efeito-row\">
            <span class=\"efeito-orig\"><em class=\"keyword {kw.lower().replace(' ', '_')}\" style=\"display:inline-block;padding:2px 10px;margin-right:14px;border-radius:7px;font-style:normal;font-weight:bold;text-shadow:none;{cor_keyword(kw)}\">{kw}</em></span>
            <input type=\"text\" class=\"efeito-trad\" data-orig=\"{kw}\" value=\"{kw}\">
            <button type=\"button\" class=\"efeito-aplicar-btn\" data-orig=\"{kw}\">Aplicar</button>
        </div>\n"""
html += '</div>'
html += """
    <!-- Botões removidos daqui -->
        </form>
    </div>
        <!-- Edição de posição agora é individual por efeito -->
    <div id="cartas">
"""

def split_efeitos_html(efeitos):
    if not efeitos:
        return []
    if isinstance(efeitos, str):
        efeitos = [efeitos]
    return [e.strip() for e in efeitos if e.strip()]

for carta in cartas:
    img_orig = carta["image"]
    # Se for ícone (rank, cosmos, force, etc.), sempre usar imagens/
    icones = [
        "rank1.webp", "rank2.webp", "rank3.webp", "rank4.webp", "rank5.webp",
        "cosmos.webp", "force.webp", "flamme.webp", "ame.webp", "sceau.webp", "compteur.webp", "heal.webp"
    ]
    nome_arquivo = os.path.basename(img_orig)
    if nome_arquivo in icones:
        img = f"imagens/{nome_arquivo}".lstrip("/")
    elif img_orig.startswith("imagens/"):
        img = img_orig.replace("imagens/", "imagens_sem_texto/").lstrip("/")
    else:
        img = img_orig.lstrip("/")
    nome = carta["Nome"]
    classe = carta["Classe"]
    efeitos = carta.get("effects")
    efeitos_html = []
    if efeitos and isinstance(efeitos, list) and efeitos:
        for ef in efeitos:
            html_efeito = None
            if isinstance(ef, dict):
                if ef.get("html"):
                    html_efeito = ef["html"]
                elif ef.get("text"):
                    html_efeito = ef["text"]
            elif isinstance(ef, str):
                html_efeito = ef
            if html_efeito:
                html_efeito = html_efeito.replace('src="/imagens/', 'src="imagens/').replace("src='/imagens/", "src='imagens/")
                # Substitui <span class="icon-flash"></span> por SVG do raio amarelo
                html_efeito = html_efeito.replace(
                    '<span alt="Energie" class="icon-flash"></span>',
                    '<span class="icon-flash"><svg viewBox="0 0 24 28"><polygon points="13,2 3,16 11,16 9,26 21,10 13,10" fill="#ffe066" stroke="#ffed00" stroke-width="2" filter="drop-shadow(1px 1px 0 #000)"/></svg></span>'
                )
                for prefixo in efeito_prefixos:
                    if html_efeito.strip().startswith(prefixo):
                        # Adiciona a keyword como classe extra (ex: <em class="keyword vaincu">Vaincu</em>)
                        class_keyword = f"keyword {prefixo.lower().replace(' ', '_')}"
                        if not html_efeito.strip().startswith(f'<em class="{class_keyword}">{prefixo}</em>'):
                            html_efeito = html_efeito.replace(prefixo, f'<em class="{class_keyword}">{prefixo}</em>', 1)
                        break
                efeitos_html.append(html_efeito)
    else:
        efeito_fallback = carta.get("Efeito", "")
        efeitos_html = split_efeitos_html(efeito_fallback)
    aspect = get_aspect(img)
    # Define classes extras para portrait/landscape
    carta_imgbox_class = f"carta-imgbox {'portrait-imgbox' if aspect=='portrait' else 'landscape-imgbox'}"
    edit_classe_class = f"edit-classe {'edit-classe-landscape' if aspect=='landscape' else 'edit-classe-portrait'}"
    # Classe normalizada para uso em CSS (ex: cavaleiro_de_ouro)
    classe_css = re.sub(r'[^a-z0-9]+', '_', classe.lower()).strip('_') if classe else ''
    html += f"""
<div class='carta-container' style='position:relative; display:inline-block;'>
    <div class='carta-toolbar' style='position:absolute; top:23px; right:-6px; left:auto; z-index:30; display:flex; flex-direction:column; gap:8px;'>
        <span class="carta-ref-icone" title="Ver original" style="background:#ffe066; position:relative;">🔍
            <span class="carta-ref-tooltip" style="display:none; position:absolute; left:-340px; top:0;">
                <img src="{img_orig}" alt="{nome}" class="carta-ref-tooltip-img"><br>
                <span class="carta-ref-tooltip-nome">{nome}</span>
            </span>
        </span>
        <span class="restaurar-btn" title="Restaurar pedaço da imagem">✏️</span>
        <div class="restaurar-toolbar">
            <button class="restaurar-ok" title="Salvar restauração">✔</button>
            <button class="restaurar-cancel" title="Cancelar">✖</button>
            <button class="restaurar-trash" title="Descartar todas as restaurações">🗑️</button>
        </div>
    </div>
    <div class="carta {aspect} {classe_css}">
        <div class="{carta_imgbox_class}">
            <img src="{img}" alt="{nome}" class="carta-img">
            <div contenteditable="true" class="edit-nome">{nome}</div>
            <input type="text" class="{edit_classe_class}" data-orig="{classe}" value="{classe}">
            <img src="{img_orig}" class="restaurar-preview">
            <canvas class="restaurar-canvas"></canvas>
            <div class="efeitos-stack">
"""
    # Adiciona os efeitos_html como divs, um por vez
    for idx, ef_html in enumerate(efeitos_html):
        ef_html_escaped = ef_html.replace('"', '&quot;').replace("'", "&#39;")
        html += (
            f'<div class="efeito-box-wrapper" style="position:relative;display:flex;align-items:flex-start;margin-top:18px;margin-bottom:8px;">'
            f'<div class="efeito-pos-toolbar" style="position:absolute;top:-18px;right:-13px;z-index:10;display:flex;flex-direction:row;align-items:center;gap:4px;">'
            f'<button class="efeito-pos-editar-btn" title="Editar posição" style="width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;background:#ffe066;color:#222;border-radius:50%;border:1.5px solid #ffe066;box-shadow:0 0 2px #0002;cursor:pointer;font-size:1em;padding:0;transition:box-shadow .2s;outline:1px solid #bbb;outline-offset:-1px;">✥</button>'
            f'</div>'
            f'<div style="display:flex;flex-direction:column;align-items:center;width:100%;">'
            f'<div contenteditable="true" class="efeito-box" data-orig="{ef_html_escaped}" data-pos-x="0" data-pos-y="0" style="--efeito-bottom:{10+idx*44}px;">'
            f'{ef_html}'
            f'</div>'
            f'</div>'
            f'</div>'
        )
    html += """
            </div>
        </div>
    </div>
</div>
"""
html += """
    </div>
    <p style=\"margin-top:40px;\">Edite o nome, classe e os efeitos sobre a carta. Para salvar, exporte o JSON ou importe para continuar a tradução depois.</p>
    <script>
    // Importa automaticamente cartas_editadas.json se existir (GitHub Pages ou servidor)
    (async function() {
        try {
            const resp = await fetch('cartas_editadas.json', {cache: 'no-store'});
            if (resp.ok) {
                const data = await resp.json();
                document.querySelectorAll('.carta').forEach(function(cartaDiv, i) {
                    if (data[i]) {
                        cartaDiv.querySelector('.edit-nome').innerText = data[i].Nome || '';
                        cartaDiv.querySelector('.edit-classe').value = data[i].Classe || '';
                        var efDivs = cartaDiv.querySelectorAll('.efeito-box');
                        if (Array.isArray(data[i].Efeitos)) {
                            for (var j = 0; j < efDivs.length; j++) {
                                var ef = data[i].Efeitos[j] || {};
                                efDivs[j].innerHTML = ef.texto || '';
                                efDivs[j].setAttribute('data-pos-x', ef.x || 0);
                                efDivs[j].setAttribute('data-pos-y', ef.y || 0);
                                efDivs[j].style.transform = `translate(${ef.x||0}px,${ef.y||0}px)`;
                            }
                        } else {
                            var efeitos = (data[i].Efeito || '').split(/<br\\s*\\/?>|;|(?<=[.])\\s+(?=[A-ZÀ-Ý])/);
                            for (var j = 0; j < efDivs.length; j++) {
                                efDivs[j].innerHTML = efeitos[j] || '';
                                efDivs[j].setAttribute('data-pos-x', 0);
                                efDivs[j].setAttribute('data-pos-y', 0);
                                efDivs[j].style.transform = '';
                            }
                        }
                        if (data[i].restauracoes) {
                            cartaDiv.dataset.restauracoes = JSON.stringify(data[i].restauracoes);
                        }
                    }
                });
            }
        } catch (e) {
            // arquivo não existe ou erro de fetch, não faz nada
        }
    })();
    // --- Edição de posição dos efeitos ---
    (function(){
        // Edição dinâmica dos botões de posição do efeito
        document.querySelectorAll('.efeito-box-wrapper').forEach(function(wrapper){
            var editarBtn = wrapper.querySelector('.efeito-pos-editar-btn');
            var box = wrapper.querySelector('.efeito-box');
            var toolbar = wrapper.querySelector('.efeito-pos-toolbar');
            var posBefore = {x:0, y:0};
            function closeAll(){
                document.querySelectorAll('.efeito-pos-action-btns').forEach(function(b){b.remove();});
                document.querySelectorAll('.efeito-pos-arrows').forEach(function(b){b.remove();});
                document.querySelectorAll('.efeito-pos-editar-btn').forEach(function(b){b.classList.remove('ativo');});
            }
            function move(dx,dy){
                var x = parseInt(box.getAttribute('data-pos-x')||'0',10)+dx;
                var y = parseInt(box.getAttribute('data-pos-y')||'0',10)+dy;
                box.setAttribute('data-pos-x',x);
                box.setAttribute('data-pos-y',y);
                box.style.transform = `translate(${x}px,${y}px)`;
            }
            editarBtn.addEventListener('click',function(e){
                e.stopPropagation();
                closeAll();
                editarBtn.classList.add('ativo');
                // Cria os botões de ação e setas
                var actionBtns = document.createElement('span');
                actionBtns.className = 'efeito-pos-action-btns';
                actionBtns.innerHTML = `
                    <button class="reset" title="Resetar posição">🗑️</button>
                    <button class="ok" title="Confirmar">✔</button>
                    <button class="cancel" title="Cancelar">✖</button>
                `;
                var arrows = document.createElement('span');
                arrows.className = 'efeito-pos-arrows';
                arrows.innerHTML = `
                    <button class="up" title="Mover para cima">↑</button>
                    <button class="down" title="Mover para baixo">↓</button>
                    <button class="left" title="Mover para a esquerda">←</button>
                    <button class="right" title="Mover para a direita">→</button>
                `;
                toolbar.appendChild(actionBtns);
                toolbar.appendChild(arrows);
                posBefore.x = parseInt(box.getAttribute('data-pos-x')||'0',10);
                posBefore.y = parseInt(box.getAttribute('data-pos-y')||'0',10);
                // Eventos dos botões
                actionBtns.querySelector('.reset').onclick = function(ev){
                    ev.stopPropagation();
                    box.setAttribute('data-pos-x',0);
                    box.setAttribute('data-pos-y',0);
                    box.style.transform = '';
                };
                actionBtns.querySelector('.ok').onclick = function(ev){
                    ev.stopPropagation();
                    closeAll();
                };
                actionBtns.querySelector('.cancel').onclick = function(ev){
                    ev.stopPropagation();
                    box.setAttribute('data-pos-x',posBefore.x);
                    box.setAttribute('data-pos-y',posBefore.y);
                    box.style.transform = `translate(${posBefore.x}px,${posBefore.y}px)`;
                    closeAll();
                };
                // Eventos das setas
                arrows.querySelector('.up').onclick = function(ev){ ev.stopPropagation(); move(0,-1); };
                arrows.querySelector('.down').onclick = function(ev){ ev.stopPropagation(); move(0,1); };
                arrows.querySelector('.left').onclick = function(ev){ ev.stopPropagation(); move(-1,0); };
                arrows.querySelector('.right').onclick = function(ev){ ev.stopPropagation(); move(1,0); };
            });
            // Setas de movimentação com teclado
            box.addEventListener('keydown', function(e){
                if(!editarBtn.classList.contains('ativo')) return;
                if(e.key==='ArrowUp'){ move(0,-1); e.preventDefault(); }
                if(e.key==='ArrowDown'){ move(0,1); e.preventDefault(); }
                if(e.key==='ArrowLeft'){ move(-1,0); e.preventDefault(); }
                if(e.key==='ArrowRight'){ move(1,0); e.preventDefault(); }
            });
        });
        // Fecha ao clicar fora
        document.addEventListener('click', function(e){
            document.querySelectorAll('.efeito-pos-action-btns').forEach(function(b){b.remove();});
            document.querySelectorAll('.efeito-pos-editar-btn').forEach(function(b){b.classList.remove('ativo');});
        });


        // Corrige eventos dos botões de cada carta
        document.querySelectorAll('.carta-container').forEach(function(container){
            var refIcone = container.querySelector('.carta-ref-icone');
            var refTooltip = container.querySelector('.carta-ref-tooltip');
            if(refIcone && refTooltip) {
                refIcone.addEventListener('mouseenter', function(e){
                    refTooltip.style.display = 'block';
                });
                refIcone.addEventListener('mouseleave', function(e){
                    refTooltip.style.display = 'none';
                });
            }
            var restaurarBtn = container.querySelector('.restaurar-btn');
            var canvas = container.querySelector('.restaurar-canvas');
            var imgSemTexto = container.querySelector('.carta-img');
            var imgOriginal = container.querySelector('.restaurar-preview');
            var toolbar = container.querySelector('.restaurar-toolbar');
            var drawing = false, startX = 0, startY = 0, endX = 0, endY = 0, rect = null;
            var restauracoes = [];
            if (container.dataset.restauracoes) {
                restauracoes = JSON.parse(container.dataset.restauracoes);
            }
            function syncCanvasSize() {
                canvas.width = imgSemTexto.naturalWidth;
                canvas.height = imgSemTexto.naturalHeight;
                canvas.style.width = imgSemTexto.offsetWidth + 'px';
                canvas.style.height = imgSemTexto.offsetHeight + 'px';
                imgOriginal.style.width = imgSemTexto.offsetWidth + 'px';
                imgOriginal.style.height = imgSemTexto.offsetHeight + 'px';
            }
            function drawAllRestauracoes() {
                var ctx = canvas.getContext('2d');
                ctx.clearRect(0,0,canvas.width,canvas.height);
                restauracoes.forEach(function(r) {
                    ctx.drawImage(imgOriginal, r.x, r.y, r.w, r.h, r.x, r.y, r.w, r.h);
                });
            }
            if(restaurarBtn) {
                restaurarBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    syncCanvasSize();
                    imgOriginal.style.display = 'block';
                    imgOriginal.style.zIndex = 32;
                    canvas.style.display = 'block';
                    toolbar.style.display = 'flex';
                    drawAllRestauracoes();
                });
            }
            // Botão de lixeira para descartar todas as restaurações
            var trashBtn = toolbar.querySelector('.restaurar-trash');
            if(trashBtn) {
                trashBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    restauracoes = [];
                    container.dataset.restauracoes = JSON.stringify(restauracoes);
                    drawAllRestauracoes();
                });
            }
        });
    })();
    // Tradução automática de classes
    // Sincroniza input de tradução -> carta
    document.querySelectorAll('.classe-trad').forEach(function(input) {
        input.addEventListener('input', function() {
            var orig = this.getAttribute('data-orig');
            var trad = this.value;
            document.querySelectorAll('.edit-classe').forEach(function(ic) {
                if (ic.getAttribute('data-orig') === orig) {
                    ic.value = trad;
                }
            });
        });
    });
    // Sincroniza edição direta na carta -> input de tradução
    document.querySelectorAll('.edit-classe').forEach(function(ic) {
        ic.addEventListener('input', function() {
            var orig = this.getAttribute('data-orig');
            var novo = this.value;
            document.querySelectorAll('.classe-trad').forEach(function(input) {
                if (input.getAttribute('data-orig') === orig) {
                    input.value = novo;
                }
            });
        });
    });
    // Atualiza todos os efeitos ao editar a tradução global (só prefixo, igual classes)
    document.querySelectorAll('.efeito-aplicar-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var orig = this.getAttribute('data-orig');
            var input = document.querySelector('.efeito-trad[data-orig="' + orig.replace(/'/g, "\\'") + '"]');
            var trad = input ? input.value : orig;
            document.querySelectorAll('.efeito-box em.keyword').forEach(function(em) {
                if (em.textContent.trim() === orig.trim()) {
                    em.textContent = trad;
                }
            });
        });
    });
    // Exportar JSON
    function exportarJson() {
        var cartas = [];
        document.querySelectorAll('.carta').forEach(function(cartaDiv) {
            var nome = cartaDiv.querySelector('.edit-nome').innerText;
            var classe = cartaDiv.querySelector('.edit-classe').value;
            var efeitos = [];
            cartaDiv.querySelectorAll('.efeito-box').forEach(function(efDiv) {
                efeitos.push({
                    texto: efDiv.innerHTML,
                    x: parseInt(efDiv.getAttribute('data-pos-x')||'0',10),
                    y: parseInt(efDiv.getAttribute('data-pos-y')||'0',10)
                });
            });
            var restauracoes = cartaDiv.dataset.restauracoes ? JSON.parse(cartaDiv.dataset.restauracoes) : [];
            cartas.push({Nome: nome, Classe: classe, Efeitos: efeitos, restauracoes: restauracoes});
        });
        var blob = new Blob([JSON.stringify(cartas, null, 2)], {type: 'application/json'});
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'cartas_editadas.json';
        a.click();
    }
    // Importar JSON
    function importarJson(event) {
        var file = event.target.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function(e) {
            var data = JSON.parse(e.target.result);
            document.querySelectorAll('.carta').forEach(function(cartaDiv, i) {
                if (data[i]) {
                    cartaDiv.querySelector('.edit-nome').innerText = data[i].Nome || '';
                    cartaDiv.querySelector('.edit-classe').innerText = data[i].Classe || '';
                    var efDivs = cartaDiv.querySelectorAll('.efeito-box');
                    // Suporte ao novo formato: Efeitos como array de objetos {texto, x, y}
                    if (Array.isArray(data[i].Efeitos)) {
                        for (var j = 0; j < efDivs.length; j++) {
                            var ef = data[i].Efeitos[j] || {};
                            efDivs[j].innerHTML = ef.texto || '';
                            efDivs[j].setAttribute('data-pos-x', ef.x || 0);
                            efDivs[j].setAttribute('data-pos-y', ef.y || 0);
                            efDivs[j].style.transform = `translate(${ef.x||0}px,${ef.y||0}px)`;
                        }
                    } else {
                        // Suporte ao formato antigo (string)
                        var efeitos = (data[i].Efeito || '').split(/<br\s*\/?>|;|(?<=[.])\s+(?=[A-ZÀ-Ý])/);
                        for (var j = 0; j < efDivs.length; j++) {
                            efDivs[j].innerHTML = efeitos[j] || '';
                            efDivs[j].setAttribute('data-pos-x', 0);
                            efDivs[j].setAttribute('data-pos-y', 0);
                            efDivs[j].style.transform = '';
                        }
                    }
                    if (data[i].restauracoes) {
                        cartaDiv.dataset.restauracoes = JSON.stringify(data[i].restauracoes);
                    }
                }
            });
        };
        reader.readAsText(file);
    }
    // Função de restauração visual (canvas)
    document.querySelectorAll('.carta-container').forEach(function(container) {
        var btn = container.querySelector('.restaurar-btn');
        var canvas = container.querySelector('.restaurar-canvas');
        var imgSemTexto = container.querySelector('.carta-img');
        var imgOriginal = container.querySelector('.restaurar-preview');
        var toolbar = container.querySelector('.restaurar-toolbar');
        var drawing = false, startX = 0, startY = 0, endX = 0, endY = 0, rect = null;
        var restauracoes = [];
        if (container.dataset.restauracoes) {
            restauracoes = JSON.parse(container.dataset.restauracoes);
        }
        // Garante que o canvas fique perfeitamente alinhado à imagem
        function syncCanvasSize() {
            canvas.width = imgSemTexto.naturalWidth;
            canvas.height = imgSemTexto.naturalHeight;
            canvas.style.width = imgSemTexto.offsetWidth + 'px';
            canvas.style.height = imgSemTexto.offsetHeight + 'px';
            imgOriginal.style.width = imgSemTexto.offsetWidth + 'px';
            imgOriginal.style.height = imgSemTexto.offsetHeight + 'px';
        }
        function drawAllRestauracoes() {
            var ctx = canvas.getContext('2d');
            ctx.clearRect(0,0,canvas.width,canvas.height);
            restauracoes.forEach(function(r) {
                ctx.drawImage(imgOriginal, r.x, r.y, r.w, r.h, r.x, r.y, r.w, r.h);
            });
        }
        if(btn) {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                syncCanvasSize();
                canvas.style.display = 'block';
                imgOriginal.style.display = 'block';
                toolbar.style.display = 'flex';
                drawAllRestauracoes();
            });
        }
        if(canvas) {
            canvas.addEventListener('mousedown', function(e) {
                if (canvas.style.display !== 'block') return;
                drawing = true;
                var rectC = canvas.getBoundingClientRect();
                var scaleX = canvas.width / rectC.width;
                var scaleY = canvas.height / rectC.height;
                startX = (e.clientX - rectC.left) * scaleX;
                startY = (e.clientY - rectC.top) * scaleY;
                endX = startX; endY = startY;
            });
            canvas.addEventListener('mousemove', function(e) {
                if (!drawing) return;
                var rectC = canvas.getBoundingClientRect();
                var scaleX = canvas.width / rectC.width;
                var scaleY = canvas.height / rectC.height;
                endX = (e.clientX - rectC.left) * scaleX;
                endY = (e.clientY - rectC.top) * scaleY;
                var ctx = canvas.getContext('2d');
                drawAllRestauracoes();
                ctx.save();
                ctx.strokeStyle = '#ffe066';
                ctx.lineWidth = 3;
                ctx.setLineDash([8,4]);
                ctx.strokeRect(startX, startY, endX-startX, endY-startY);
                ctx.restore();
                ctx.save();
                ctx.globalAlpha = 0.7;
                ctx.drawImage(imgOriginal, startX, startY, endX-startX, endY-startY, startX, startY, endX-startX, endY-startY);
                ctx.restore();
            });
            canvas.addEventListener('mouseup', function(e) {
                if (!drawing) return;
                drawing = false;
                rect = {
                    x: Math.round(Math.min(startX, endX)),
                    y: Math.round(Math.min(startY, endY)),
                    w: Math.round(Math.abs(endX-startX)),
                    h: Math.round(Math.abs(endY-startY))
                };
            });
        }
        if(toolbar) {
            var okBtn = toolbar.querySelector('.restaurar-ok');
            var cancelBtn = toolbar.querySelector('.restaurar-cancel');
            if(okBtn) okBtn.addEventListener('click', function(e) {
                if (rect && rect.w > 0 && rect.h > 0) {
                    var tempCanvas = document.createElement('canvas');
                    tempCanvas.width = imgSemTexto.naturalWidth;
                    tempCanvas.height = imgSemTexto.naturalHeight;
                    var tempCtx = tempCanvas.getContext('2d');
                    tempCtx.drawImage(imgSemTexto, 0, 0);
                    tempCtx.drawImage(imgOriginal, rect.x, rect.y, rect.w, rect.h, rect.x, rect.y, rect.w, rect.h);
                    imgSemTexto.src = tempCanvas.toDataURL('image/webp');
                    restauracoes.push(rect);
                    container.dataset.restauracoes = JSON.stringify(restauracoes);
                    drawAllRestauracoes();
                }
                rect = null;
                canvas.style.display = 'none';
                imgOriginal.style.display = 'none';
                toolbar.style.display = 'none';
            });
            if(cancelBtn) cancelBtn.addEventListener('click', function(e) {
                rect = null;
                canvas.style.display = 'none';
                imgOriginal.style.display = 'none';
                toolbar.style.display = 'none';
                drawAllRestauracoes();
            });
        }
        window.addEventListener('resize', function() {
            if (canvas && canvas.style.display === 'block') {
                syncCanvasSize();
                drawAllRestauracoes();
            }
        });
    });
    document.querySelectorAll('.carta-ref-hover').forEach(function(ref) {
        var icone = ref.querySelector('.carta-ref-icone');
        var tooltip = ref.querySelector('.carta-ref-tooltip');
        icone.addEventListener('click', function(e) {
            e.stopPropagation();
            document.querySelectorAll('.carta-ref-tooltip').forEach(function(t){ t.style.display = 'none'; });
                var isOpen = tooltip.style.display === 'block';
                if (!isOpen) {
                    tooltip.style.display = 'block';
                }
        });
            // Permite fechar ao clicar no próprio tooltip
            tooltip.addEventListener('click', function(e) {
                e.stopPropagation();
                tooltip.style.display = 'none';
            });
    });
    document.addEventListener('click', function(e) {
        document.querySelectorAll('.carta-ref-tooltip').forEach(function(t){ t.style.display = 'none'; });
    });
    // Tooltip para classes (segue o mouse)
    document.querySelectorAll('.classe-orig.classe-hover').forEach(function(el) {
    // Tooltip para efeitos globais (segue o mouse)
    document.querySelectorAll('.efeito-orig.efeito-hover').forEach(function(el) {
        var tooltip = el.querySelector('.efeito-carta-tooltip');
        el.addEventListener('mouseenter', function(e){
            tooltip.style.display = 'block';
        });
        el.addEventListener('mousemove', function(e){
            if (!tooltip) return;
            var padding = 16;
            var tw = tooltip.offsetWidth || 340;
            var th = tooltip.offsetHeight || 400;
            var x = e.clientX + padding;
            var y = e.clientY + padding;
            // Ajusta para não sair da tela
            if (x + tw > window.innerWidth) x = window.innerWidth - tw - padding;
            if (y + th > window.innerHeight) y = window.innerHeight - th - padding;
            tooltip.style.left = x + 'px';
            tooltip.style.top = y + 'px';
        });
        el.addEventListener('mouseleave', function(){ tooltip.style.display = 'none'; });
    });
        var tooltip = el.querySelector('.classe-carta-tooltip');
        el.addEventListener('mouseenter', function(e){
            tooltip.style.display = 'block';
        });
        el.addEventListener('mousemove', function(e){
            if (!tooltip) return;
            var padding = 16;
            var tw = tooltip.offsetWidth || 340;
            var th = tooltip.offsetHeight || 400;
            var x = e.clientX + padding;
            var y = e.clientY + padding;
            // Ajusta para não sair da tela
            if (x + tw > window.innerWidth) x = window.innerWidth - tw - padding;
            if (y + th > window.innerHeight) y = window.innerHeight - th - padding;
            tooltip.style.left = x + 'px';
            tooltip.style.top = y + 'px';
        });
        el.addEventListener('mouseleave', function(){ tooltip.style.display = 'none'; });
    });
    // --- Observador de mudanças nos efeitos globais ---
    // Garante que qualquer alteração manual (ex: colar texto) nos inputs de efeitos globais seja refletida nas cartas
    const efeitoInputs = document.querySelectorAll('.efeito-trad');
    efeitoInputs.forEach(function(input) {
        // Usar MutationObserver para detectar mudanças no valor do input
        const observer = new MutationObserver(function() {
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
        observer.observe(input, { attributes: true, attributeFilter: ['value'] });
        // Também observar mudanças diretas de texto (ex: colar via menu)
        input.addEventListener('change', function() {
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
        // E garantir atualização ao perder o foco
        input.addEventListener('blur', function() {
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    });
    // Atualiza também se o usuário editar manualmente o <em class="keyword"> na carta
    document.querySelectorAll('.efeito-box').forEach(function(div) {
        div.addEventListener('input', function(e) {
            // Para cada efeito global, se o texto do <em class="keyword"> mudou, atualiza o input correspondente
            var ems = div.querySelectorAll('em.keyword');
            ems.forEach(function(em) {
                var texto = em.textContent.trim();
                document.querySelectorAll('.efeito-trad').forEach(function(input) {
                    var orig = input.getAttribute('data-orig');
                    if (orig.trim() === texto) {
                        input.value = texto;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            });
        });
    });
    </script>
</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)