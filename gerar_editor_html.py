# --- NOVO GERADOR: Layout das cartas igual ao gerar_editor_old.py, instruções e recursos novos ---
import os
import json
import re
import unicodedata
from PIL import Image

IMAGES_DIR = "imagens"
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
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Belanosima:wght@700&family=UnifrakturMaguntia&display=swap\" rel=\"stylesheet\">
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
        .carta.portrait .carta-imgbox { width: 300px; height: 419px; }
    .carta.landscape .carta-imgbox { width: 419px; height: 300px; }
    .carta-img { width: 100%; height: 100%; border-radius: 12px; box-shadow: 0 0 16px #000a; object-fit: fill; border: none; }
        /* Faixa de fundo do nome por ranking — posição/tamanho controlado por JS */
        .nome-faixa {
            position: absolute;
            z-index: 1;
            border-radius: 4px;
            pointer-events: none;
            background-repeat: no-repeat;
        }
        .nome-faixa.rank0 { background: rgba(80,80,80,0.7); }
        .nome-faixa.rank1 { background-image: url(imagens/bordas/rank1.png); }
        .nome-faixa.rank2 { background-image: url(imagens/bordas/rank2.png); }
        .nome-faixa.rank3 { background-image: url(imagens/bordas/rank3.png); }
        .nome-faixa.rank4 { background-image: url(imagens/bordas/rank4.png); }
        .nome-faixa.rank5 { background-image: url(imagens/bordas/rank5.png); }
        .nome-faixa.rank6 { background-image: url(imagens/bordas/rank6.png); }
        .nome-faixa.rank7 { background-image: url(imagens/bordas/rank7.png); }
        .nome-faixa.rank8 { background-image: url(imagens/bordas/rank8.png); }
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
            font-size: 1.2em;
            font-family: 'Arial', Arial, sans-serif;
            font-weight: bold;
            text-align: center;
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            outline: none;
            z-index: 2;
        }
        .edit-classe { z-index: 20; position: absolute; top: 34px; left: 20px; background-repeat: no-repeat; background-color: transparent; font-size: 0.8em; font-family: 'Georgia', serif; border: none; border-radius: 6px; padding: 2px 8px; outline: none; text-align: center; box-shadow: 0 1px 6px #0006; color: #fff; width: auto; min-width: 40px; max-width: 80%; }
    .edit-classe { font-style: italic; }
    /* Imagem de classe: posição/tamanho calculados dinamicamente por JS (syncClasseWidth) */
    .portrait-imgbox .edit-classe { background-image: url(imagens/bordas/class_vertical.png); left: 50%; transform: translateX(-50%); }
    .landscape-imgbox .edit-classe { background-image: url(imagens/bordas/class_horizontal.png); max-width: 50%; }
    .rank-select { display: block; width: 28px; height: 28px; background: #1a1a1a; color: #ffe066; border: 2px solid #ffe066; border-radius: 6px; font-size: 0.7em; font-weight: bold; cursor: pointer; text-align: center; text-align-last: center; padding: 0; -webkit-appearance: none; appearance: none; outline: none; box-shadow: 0 0 4px #000; }
    .rank-select option { background: #222; color: #eee; }
        .efeitos-stack {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            font-family: 'Georgia', serif;
            font-size: 0.7em;
            color: #111;
            position: absolute;
            margin: 0;
        }
        /* Portrait: bbox (25,368)→(260,398), imagem 300x419 */
        .carta.portrait .efeitos-stack {
            left: 25px;
            width: 235px;
            bottom: 21px;
            right: auto;
        }
        /* Landscape: bbox (20,248)→(380,275), imagem 419x300 */
        .carta.landscape .efeitos-stack {
            left: 20px;
            width: 360px;
            bottom: 25px;
            right: auto;
        }
        .effect {
            font-family: 'NeoSansW01', sans-serif;
            border-radius: 6px;
            padding: 2px 6px;
            margin-bottom: 2px;
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
        .efeitos-drag-handle { cursor: grab; color: #ffe066aa; font-size: 0.85em; line-height: 1; padding: 1px 4px 3px; text-align: center; width: 100%; user-select: none; letter-spacing: 3px; }
        .efeitos-drag-handle:hover { color: #ffe066; }
        .efeitos-drag-handle:active { cursor: grabbing; }
        .width-ctrl-btn { background: #333; color: #ffe066; border: 1px solid #ffe066; border-radius: 4px; padding: 1px 5px; font-size: 0.62em; cursor: pointer; font-weight: bold; line-height: 1.6; }
        .width-ctrl-btn:hover { background: #ffe066; color: #222; }
        .efeito-item { position: relative; width: 100%; display: flex; flex-direction: column; align-items: center; }
        .efeito-item-handle { cursor: grab; color: #ffe066aa; font-size: 0.75em; width: 100%; display: flex; justify-content: flex-end; align-items: center; gap: 3px; user-select: none; padding: 1px 3px 0; }
        .efeito-item-handle:hover { color: #ffe066; }
        .efeito-item-handle:active { cursor: grabbing; }
        .efeito-item-width-btn { background: #2a2a2a; color: #ffe066; border: 1px solid #ffe066; border-radius: 3px; padding: 0 4px; font-size: 0.85em; cursor: pointer; line-height: 1.5; }
        .efeito-item-width-btn:hover { background: #ffe066; color: #222; }
        /* Ícones cosmos e forca: width 22px; demais: width conforme HTML do JSON */
        .effect img[alt="Cosmos"], .effect img[alt="Force"] {
            width: 15px !important;
            height: 15px !important;
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
        <div class="classes-lista collapsible-box">
            <div class="collapsible-header" style="display:flex;align-items:center;justify-content:space-between;cursor:pointer;">
                <h2 style="margin:0;">Tradução de Classes Comuns</h2>
                <button type="button" class="collapsible-toggle" aria-expanded="true" style="background:#444;color:#ffe066;border:none;border-radius:6px;padding:6px 18px;font-size:1em;cursor:pointer;">Ocultar</button>
            </div>
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
    <div class="efeitos-lista collapsible-box classes-lista" style="margin-top:32px;">
        <div class="collapsible-header" style="display:flex;align-items:center;justify-content:space-between;cursor:pointer;">
            <h2 style="margin:0;">Tradução de Efeitos Globais</h2>
            <button type="button" class="collapsible-toggle" aria-expanded="true" style="background:#444;color:#ffe066;border:none;border-radius:6px;padding:6px 18px;font-size:1em;cursor:pointer;">Ocultar</button>
        </div>
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
    # sempre usar imagem original
    img = img_orig.lstrip("/")
    # Extrai classe de ranking do TipoIcone
    tipo_icone = carta.get("TipoIcone", "")
    rank_match = re.search(r'rank(\d+)', tipo_icone)
    rank_class = f"rank{rank_match.group(1)}" if rank_match else "rank0"
    rank_num = int(rank_match.group(1)) if rank_match else 0
    nome = carta["Nome"]
    classe = carta["Classe"]
    efeitos = carta.get("effects")
    efeitos_html = []
    if efeitos and isinstance(efeitos, list) and efeitos:
        # PV type sempre primeiro
        efeitos = sorted(efeitos, key=lambda e: 0 if (isinstance(e, dict) and e.get("type") == "pv") else 1)
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
        <select class="rank-select" title="Rank da carta (clique para alterar)">
            <option value="0"{'  selected' if rank_num==0 else ''}>–</option>
            <option value="1"{'  selected' if rank_num==1 else ''}>Básico</option>
            <option value="2"{'  selected' if rank_num==2 else ''}>Bronze</option>
            <option value="3"{'  selected' if rank_num==3 else ''}>Prata</option>
            <option value="4"{'  selected' if rank_num==4 else ''}>Ouro</option>
            <option value="5"{'  selected' if rank_num==5 else ''}>Divino</option>
            <option value="6"{'  selected' if rank_num==6 else ''}>B/P</option>
            <option value="7">B/O</option>
            <option value="8">P/O</option>
        </select>
        <div style="display:flex;gap:2px;">
          <button class="width-ctrl-btn" data-target="nome" data-delta="-10" title="Estreitar nome">N-</button>
          <button class="width-ctrl-btn" data-target="nome" data-delta="10" title="Alargar nome">N+</button>
        </div>
        <div style="display:flex;gap:2px;">
          <button class="width-ctrl-btn" data-target="efeito" data-delta="-10" title="Estreitar efeitos">E-</button>
          <button class="width-ctrl-btn" data-target="efeito" data-delta="10" title="Alargar efeitos">E+</button>
        </div>
    </div>
    <div class="carta {aspect} {classe_css}" data-img-orig="{img_orig}">
        <div class="{carta_imgbox_class}">
            <img src="{img}" alt="{nome}" class="carta-img">
            <div class="nome-faixa {rank_class}" data-rank="{rank_num}"></div>
            <div contenteditable="true" class="edit-nome">{nome}</div>
            <input type="text" class="{edit_classe_class}" data-orig="{classe}" data-orientation="{'landscape' if aspect=='landscape' else 'portrait'}" value="{classe}">
            <div class="efeitos-stack" data-drag-x="0" data-drag-y="0">
                <div class="efeitos-drag-handle" title="Arrastar para mover · duplo-clique para resetar">· · · · ·</div>
"""
    # Adiciona os efeitos_html com wrapper individual para drag/resize
    for idx, ef_html in enumerate(efeitos_html):
        ef_html_escaped = ef_html.replace('"', '&quot;').replace("'", "&#39;")
        html += (
            f'<div class="efeito-item" data-idx="{idx}" data-pos-x="0" data-pos-y="0">'
            f'<div class="efeito-item-handle" title="Arrastar · duplo-clique para resetar">⠿ '
            f'<button class="efeito-item-width-btn" data-delta="-5" title="Estreitar">E-</button>'
            f'<button class="efeito-item-width-btn" data-delta="5" title="Alargar">E+</button>'
            f'</div>'
            f'<div contenteditable="true" class="efeito-box" data-orig="{ef_html_escaped}">{ef_html}</div>'
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
    // Expande/retrai as seções de classes e efeitos
    document.querySelectorAll('.collapsible-header').forEach(function(header){
        var box = header.parentElement;
        var toggle = header.querySelector('.collapsible-toggle');
        var form = box.querySelector('form');
        var row = box.querySelector('.row-container');
        toggle.addEventListener('click', function(e){
            e.stopPropagation();
            var expanded = toggle.getAttribute('aria-expanded') === 'true';
            if(expanded){
                form.style.display = 'none';
                if(row) row.style.display = 'none';
                toggle.textContent = 'Mostrar';
                toggle.setAttribute('aria-expanded','false');
            }else{
                form.style.display = '';
                if(row) row.style.display = '';
                toggle.textContent = 'Ocultar';
                toggle.setAttribute('aria-expanded','true');
            }
        });
        // Clique no header também expande/retrai
        header.addEventListener('click', function(e){
            if(e.target !== toggle){
                toggle.click();
            }
        });
    });
    // Importa automaticamente cartas_editadas.json se existir (GitHub Pages ou servidor)
    (function() {
        fetch('cartas_editadas.json', {cache: 'no-store'})
            .then(function(resp) {
                if (!resp.ok) return null;
                return resp.json();
            })
            .then(function(data) {
                if (!data) return;
                // Preenche cartas
                var cartas = Array.isArray(data) ? data : data.cartas;
                document.querySelectorAll('.carta').forEach(function(cartaDiv, i) {
                    if (cartas && cartas[i]) {
                        cartaDiv.querySelector('.edit-nome').innerText = cartas[i].Nome || '';
                        formatNome(cartaDiv.querySelector('.edit-nome'));
                        var efItems3 = cartaDiv.querySelectorAll('.efeito-item');
                        if (Array.isArray(cartas[i].Efeitos)) {
                            for (var j = 0; j < efItems3.length; j++) {
                                var ef = cartas[i].Efeitos[j] || {};
                                var eit3 = efItems3[j]; var efDiv3 = eit3.querySelector('.efeito-box');
                                if (efDiv3) efDiv3.innerHTML = ef.texto || '';
                                eit3.setAttribute('data-pos-x', ef.x || 0); eit3.setAttribute('data-pos-y', ef.y || 0);
                                eit3.style.transform = 'translate(' + (ef.x||0) + 'px,' + (ef.y||0) + 'px)';
                                if (ef.w && efDiv3) efDiv3.style.width = ef.w;
                            }
                        } else {
                            var efeitos = (cartas[i].Efeito || '').split(/<br\\s*\\/?>|;|(?<=[.])\\s+(?=[A-ZÀ-Ý])/);
                            for (var j = 0; j < efDivs.length; j++) {
                                efDivs[j].innerHTML = efeitos[j] || '';
                                efDivs[j].setAttribute('data-pos-x', 0);
                                efDivs[j].setAttribute('data-pos-y', 0);
                                efDivs[j].style.transform = '';
                            }
                        }
                        if (cartas[i].restauracoes) {
                            cartaDiv.dataset.restauracoes = JSON.stringify(cartas[i].restauracoes);
                        }
                        if (cartas[i].rank !== undefined) {
                            var rankSel = cartaDiv.closest('.carta-container').querySelector('.rank-select');
                            if (rankSel) {
                                rankSel.value = cartas[i].rank;
                                rankSel.dispatchEvent(new Event('change', {bubbles: true}));
                            }
                        }
                    }
                });
                // Restaurar traduções de classes
                if (data.classes_trad) {
                    document.querySelectorAll('.classe-trad').forEach(function(input) {
                        var orig = input.getAttribute('data-orig');
                        if (data.classes_trad[orig] !== undefined) {
                            input.value = data.classes_trad[orig];
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                }
                // Restaurar traduções de efeitos globais
                if (data.efeitos_trad) {
                    document.querySelectorAll('.efeito-trad').forEach(function(input) {
                        var orig = input.getAttribute('data-orig');
                        if (data.efeitos_trad[orig] !== undefined) {
                            input.value = data.efeitos_trad[orig];
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                }
                if (typeof syncAllClasseWidths === 'function') syncAllClasseWidths();
            })
            .catch(function(e) {
                // arquivo não existe ou erro de fetch, não faz nada
            });
    })();
    // --- Eventos de referência (tooltip) ---
    document.querySelectorAll('.carta-container').forEach(function(container){
        var refIcone = container.querySelector('.carta-ref-icone');
        var refTooltip = container.querySelector('.carta-ref-tooltip');
        if(refIcone && refTooltip) {
            refIcone.addEventListener('mouseenter', function(){ refTooltip.style.display = 'block'; });
            refIcone.addEventListener('mouseleave', function(){ refTooltip.style.display = 'none'; });
        }
    });
    // --- Drag para mover o bloco de efeitos (stack inteiro) ---
    document.querySelectorAll('.efeitos-drag-handle').forEach(function(handle) {
        var stack = handle.closest('.efeitos-stack');
        if (!stack) return;
        var dragX = 0, dragY = 0;
        handle.addEventListener('dblclick', function() {
            dragX = 0; dragY = 0;
            stack.setAttribute('data-drag-x', 0); stack.setAttribute('data-drag-y', 0);
            stack.style.transform = '';
        });
        handle.addEventListener('mousedown', function(e) {
            e.preventDefault();
            var startX = e.clientX - dragX, startY = e.clientY - dragY;
            handle.style.cursor = 'grabbing';
            function onMove(ev) {
                dragX = ev.clientX - startX; dragY = ev.clientY - startY;
                stack.setAttribute('data-drag-x', dragX); stack.setAttribute('data-drag-y', dragY);
                stack.style.transform = 'translate(' + dragX + 'px,' + dragY + 'px)';
            }
            function onUp() {
                handle.style.cursor = ''; document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp);
            }
            document.addEventListener('mousemove', onMove); document.addEventListener('mouseup', onUp);
        });
    });
    // --- Drag individual de cada efeito ---
    document.querySelectorAll('.efeito-item-handle').forEach(function(handle) {
        var item = handle.closest('.efeito-item');
        if (!item) return;
        var dragX = parseFloat(item.getAttribute('data-pos-x')) || 0;
        var dragY = parseFloat(item.getAttribute('data-pos-y')) || 0;
        handle.addEventListener('dblclick', function(e) {
            if (e.target.classList.contains('efeito-item-width-btn')) return;
            dragX = 0; dragY = 0;
            item.setAttribute('data-pos-x', 0); item.setAttribute('data-pos-y', 0);
            item.style.transform = '';
        });
        handle.addEventListener('mousedown', function(e) {
            if (e.target.classList.contains('efeito-item-width-btn')) return;
            e.preventDefault();
            var startX = e.clientX - dragX, startY = e.clientY - dragY;
            function onMove(ev) {
                dragX = ev.clientX - startX; dragY = ev.clientY - startY;
                item.setAttribute('data-pos-x', dragX); item.setAttribute('data-pos-y', dragY);
                item.style.transform = 'translate(' + dragX + 'px,' + dragY + 'px)';
            }
            function onUp() { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); }
            document.addEventListener('mousemove', onMove); document.addEventListener('mouseup', onUp);
        });
        handle.querySelectorAll('.efeito-item-width-btn').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                var box = item.querySelector('.efeito-box');
                box.style.width = Math.max(40, box.offsetWidth + parseInt(this.getAttribute('data-delta'))) + 'px';
            });
        });
    });
    // --- Controles de largura do nome e efeitos ---
    document.querySelectorAll('.width-ctrl-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var container = this.closest('.carta-container');
            var delta = parseInt(this.getAttribute('data-delta'));
            var target = this.getAttribute('data-target');
            if (target === 'nome') {
                var faixa = container.querySelector('.nome-faixa');
                var extra = (parseInt(faixa.dataset.wExtra || '0', 10)) + delta;
                faixa.dataset.wExtra = extra;
                syncNomeFaixa(container.querySelector('.edit-nome'));
            } else if (target === 'efeito') {
                var st = container.querySelector('.efeitos-stack');
                st.style.width = Math.max(40, st.offsetWidth + delta) + 'px';
            }
        });
    });
    // Tradução automática de classes
    // Sincroniza input de tradução -> carta
    document.querySelectorAll('.classe-trad').forEach(function(input) {
        input.addEventListener('input', function() {
            var orig = this.getAttribute('data-orig');
            var trad = this.value;
            document.querySelectorAll('.edit-classe').forEach(function(ic) {
                if (ic.getAttribute('data-orig') === orig) {
                    ic.value = trad;
                    syncClasseWidth(ic);
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
        // Carrega cartas.json original (sincrono, pois só no export)
        var req = new XMLHttpRequest();
        req.open('GET', 'cartas.json', false); // síncrono
        req.send(null);
        var cartasOriginais = [];
        if (req.status === 200) {
            try { cartasOriginais = JSON.parse(req.responseText); } catch(e) { cartasOriginais = []; }
        }
        // Monta mapa por imagem original
        var mapaOrig = {};
        cartasOriginais.forEach(function(carta) {
            if (carta && carta.image) mapaOrig[carta.image] = carta;
        });
        // Função para normalizar texto de efeito: remove tags, pega só texto
        function normalizaEfeitoTexto(efeitoHtml) {
            if (!efeitoHtml) return '';
            var div = document.createElement('div');
            div.innerHTML = efeitoHtml;
            // Remove tradução global: pega o texto original das keywords
            div.querySelectorAll('em.keyword').forEach(function(em){
                em.textContent = em.getAttribute('data-orig') || em.textContent;
            });
            return div.textContent.replace(/\s+/g,' ').trim();
        }
        var cartasEditadas = {};
        document.querySelectorAll('.carta').forEach(function(cartaDiv, idx) {
            var imgOrig = cartaDiv.dataset.imgOrig;
            var cartaOrig = mapaOrig[imgOrig] || {};
            var nome = cartaDiv.querySelector('.edit-nome').innerText;
            var classeInput = cartaDiv.querySelector('.edit-classe');
            var classe = classeInput.value;
            var nomeOrig = cartaOrig.Nome || '';
            var classeOrig = cartaOrig.Classe || '';
            var alterado = false;
            var motivos = [];
            if (nome !== nomeOrig) { alterado = true; motivos.push('nome:' + nomeOrig + ' => ' + nome); }
            // Não compara classe para decidir se exporta
            // Efeitos: compara texto e posição, ignorando só tradução global
            var efeitos = [];
            var efeitosOrig = (cartaOrig.Efeitos || cartaOrig.effects || []);
            var efItems = cartaDiv.querySelectorAll('.efeito-item');
            for (var j = 0; j < efItems.length; j++) {
                var eit = efItems[j];
                var efDiv = eit.querySelector('.efeito-box');
                var texto = efDiv ? efDiv.innerHTML : '';
                var x = parseInt(eit.getAttribute('data-pos-x')||'0',10);
                var y = parseInt(eit.getAttribute('data-pos-y')||'0',10);
                var w = efDiv ? (efDiv.style.width || '') : '';
                var textoOrig = '';
                var xOrig = 0, yOrig = 0, wOrig = '';
                if (efeitosOrig[j]) {
                    textoOrig = efeitosOrig[j].texto || efeitosOrig[j].html || efeitosOrig[j] || '';
                    xOrig = efeitosOrig[j].x == null ? 0 : efeitosOrig[j].x;
                    yOrig = efeitosOrig[j].y == null ? 0 : efeitosOrig[j].y;
                    wOrig = efeitosOrig[j].w || '';
                }
                // Para ignorar tradução global, compara o texto puro ANTES da tradução
                function textoSemTraduKeyword(html) {
                    if (!html) return '';
                    var div = document.createElement('div');
                    div.innerHTML = html;
                    div.querySelectorAll('em.keyword').forEach(function(em){
                        em.textContent = em.getAttribute('data-orig') || em.textContent;
                    });
                    return div.textContent.replace(/\s+/g,' ').trim();
                }
                var textoComp = textoSemTraduKeyword(texto);
                var textoOrigComp = textoSemTraduKeyword(textoOrig);
                if (textoComp !== textoOrigComp) {
                    alterado = true; motivos.push('efeito'+j+':"'+textoOrigComp+'" => "'+textoComp+'"');
                }
                if ((x||0) !== (xOrig||0) || (y||0) !== (yOrig||0)) {
                    alterado = true; motivos.push('efeito'+j+'_pos:('+xOrig+','+yOrig+') => ('+x+','+y+')');
                }
                if (w !== wOrig) { alterado = true; motivos.push('efeito'+j+'_w:' + wOrig + ' => ' + w); }
                efeitos.push({texto: texto, x: x, y: y, w: w});
                if (textoComp !== textoOrigComp || (x||0)!==(xOrig||0) || (y||0)!==(yOrig||0) || w !== wOrig) {
                    console.log('[DEBUG] Efeito carta', imgOrig, 'idx', j, {
                        textoComp, textoOrigComp, x, xOrig, y, yOrig, w, wOrig
                    });
                }
            }
            var stack = cartaDiv.querySelector('.efeitos-stack');
            var stackX = stack ? parseInt(stack.getAttribute('data-drag-x')||'0',10) : 0;
            var stackY = stack ? parseInt(stack.getAttribute('data-drag-y')||'0',10) : 0;
            if (stackX !== 0 || stackY !== 0) { alterado = true; motivos.push('stackPos:(' + stackX + ',' + stackY + ')'); }
            var faixaEl = cartaDiv.querySelector('.nome-faixa');
            var nomeWExtra = faixaEl ? (parseInt(faixaEl.dataset.wExtra || '0', 10)) : 0;
            if (nomeWExtra !== 0) { alterado = true; motivos.push('nomeWExtra:' + nomeWExtra); }
            // Verificar se rank mudou
            var rankSelect = cartaDiv.closest('.carta-container').querySelector('.rank-select');
            var rank = rankSelect ? parseInt(rankSelect.value) : 0;
            var rankOrig = 0;
            var tipoIconeOrig = cartaOrig.TipoIcone || '';
            var rankOrigMatch = tipoIconeOrig.match(/rank(\\d+)/);
            if (rankOrigMatch) rankOrig = parseInt(rankOrigMatch[1]);
            if (rank !== rankOrig) { alterado = true; motivos.push('rank:' + rankOrig + ' => ' + rank); }
            if (alterado) {
                cartasEditadas[imgOrig] = {
                    Nome: nome,
                    Classe: classe,
                    Efeitos: efeitos,
                    stackX: stackX,
                    stackY: stackY,
                    nomeWExtra: nomeWExtra,
                    rank: rank
                };
                var nomeLog = nomeOrig || imgOrig;
                console.log('[ALTERADA]', nomeLog, '|', motivos.join(' | '));
            }
        });
        // Exporta apenas traduções alteradas
        var classes_trad = {};
        document.querySelectorAll('.classe-trad').forEach(function(input) {
            var orig = input.getAttribute('data-orig');
            if (input.value !== orig) {
                classes_trad[orig] = input.value;
            }
        });
        var efeitos_trad = {};
        document.querySelectorAll('.efeito-trad').forEach(function(input) {
            var orig = input.getAttribute('data-orig');
            if (input.value !== orig) {
                efeitos_trad[orig] = input.value;
            }
        });
        var exportData = {
            cartas: cartasEditadas,
            classes_trad: classes_trad,
            efeitos_trad: efeitos_trad
        };
        var blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'cartas_editadas.json';
        a.click();
    }
    window.exportarJson = exportarJson;
    // Importar JSON
    function importarJson(event) {
        var file = event.target.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function(e) {
            var data = JSON.parse(e.target.result);
            // Novo formato: cartas é um objeto {imgOrig: {dados...}}
            var cartasEditadas = data.cartas || {};
            document.querySelectorAll('.carta').forEach(function(cartaDiv) {
                var imgOrig = cartaDiv.dataset.imgOrig;
                if (cartasEditadas[imgOrig]) {
                    var carta = cartasEditadas[imgOrig];
                    if (carta.Nome !== undefined) { cartaDiv.querySelector('.edit-nome').innerText = carta.Nome; formatNome(cartaDiv.querySelector('.edit-nome')); }
                    if (carta.Classe !== undefined) cartaDiv.querySelector('.edit-classe').value = carta.Classe;
                    var efItems2 = cartaDiv.querySelectorAll('.efeito-item');
                    if (Array.isArray(carta.Efeitos)) {
                        for (var j = 0; j < efItems2.length; j++) {
                            var eit2 = efItems2[j]; var efDiv2 = eit2.querySelector('.efeito-box');
                            var ef2 = carta.Efeitos[j] || {};
                            if (efDiv2 && ef2.texto !== undefined) efDiv2.innerHTML = ef2.texto;
                            if (ef2.x || ef2.y) { var dx2=ef2.x||0, dy2=ef2.y||0; eit2.setAttribute('data-pos-x',dx2); eit2.setAttribute('data-pos-y',dy2); eit2.style.transform='translate('+dx2+'px,'+dy2+'px)'; }
                            if (ef2.w && efDiv2) efDiv2.style.width = ef2.w;
                        }
                    }
                    var stack = cartaDiv.querySelector('.efeitos-stack');
                    if (stack && carta.stackX !== undefined) {
                        var dx = carta.stackX || 0, dy = carta.stackY || 0;
                        stack.setAttribute('data-drag-x', dx);
                        stack.setAttribute('data-drag-y', dy);
                        stack.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
                    }
                    if (carta.nomeWExtra !== undefined) {
                        var faixaEl2 = cartaDiv.querySelector('.nome-faixa');
                        if (faixaEl2) { faixaEl2.dataset.wExtra = carta.nomeWExtra; syncNomeFaixa(cartaDiv.querySelector('.edit-nome')); }
                    }
                    if (carta.rank !== undefined) {
                        var rankSel = cartaDiv.closest('.carta-container').querySelector('.rank-select');
                        if (rankSel) {
                            rankSel.value = carta.rank;
                            rankSel.dispatchEvent(new Event('change', {bubbles: true}));
                        }
                    }
                }
            });
            // Restaurar traduções de classes
            if (data.classes_trad) {
                document.querySelectorAll('.classe-trad').forEach(function(input) {
                    var orig = input.getAttribute('data-orig');
                    if (data.classes_trad[orig] !== undefined) {
                        input.value = data.classes_trad[orig];
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }
            // Restaurar traduções de efeitos globais
            if (data.efeitos_trad) {
                document.querySelectorAll('.efeito-trad').forEach(function(input) {
                    var orig = input.getAttribute('data-orig');
                    if (data.efeitos_trad[orig] !== undefined) {
                        input.value = data.efeitos_trad[orig];
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }
            if (typeof syncAllClasseWidths === 'function') syncAllClasseWidths();
        };
        reader.readAsText(file);
    }
    window.importarJson = importarJson;
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
    // --- Sincroniza .nome-faixa com o bounding box REAL do texto em .edit-nome ---
    function syncNomeFaixa(editNome) {
        var imgbox = editNome.closest('.carta-imgbox');
        if (!imgbox) return;
        var faixa = imgbox.querySelector('.nome-faixa');
        if (!faixa) return;
        var boxRect = imgbox.getBoundingClientRect();
        var nomeRect = editNome.getBoundingClientRect();
        // Mede a largura real do texto (não do div inteiro) usando Range
        var textLeft = nomeRect.left;
        var textWidth = nomeRect.width;
        try {
            var range = document.createRange();
            range.selectNodeContents(editNome);
            var rects = range.getClientRects();
            if (rects.length > 0) {
                var minLeft = Infinity, maxRight = -Infinity;
                for (var i = 0; i < rects.length; i++) {
                    if (rects[i].width > 0) {
                        minLeft = Math.min(minLeft, rects[i].left);
                        maxRight = Math.max(maxRight, rects[i].right);
                    }
                }
                if (minLeft < Infinity) { textLeft = minLeft; textWidth = maxRight - minLeft; }
            }
        } catch(e) {}
        var top  = nomeRect.top  - boxRect.top;
        var left = textLeft - boxRect.left;
        var extra = parseInt(faixa.dataset.wExtra || '0', 10);
        var finalLeft  = left - extra / 2;
        var finalWidth = textWidth + extra;
        faixa.style.top    = top  + 'px';
        faixa.style.left   = finalLeft + 'px';
        faixa.style.width  = finalWidth + 'px';
        faixa.style.height = nomeRect.height + 'px';
        // Alinha a imagem de rank ao card: mostra o slice correspondente à posição da faixa
        faixa.style.backgroundSize     = boxRect.width + 'px ' + boxRect.height + 'px';
        faixa.style.backgroundPosition = (-finalLeft) + 'px ' + (-top) + 'px';
    }
    // Aplica tamanho reduzido ao resto do nome quando >20 chars
    function formatNome(el) {
        var text = el.innerText.trim();
        el.innerHTML = '';
        if (text.length > 20) {
            var spaceIdx = text.indexOf(' ');
            if (spaceIdx > 0) {
                var s1 = document.createElement('span');
                s1.textContent = text.slice(0, spaceIdx);
                var s2 = document.createElement('span');
                s2.style.fontSize = '0.9em';
                s2.textContent = text.slice(spaceIdx);
                el.appendChild(s1);
                el.appendChild(s2);
            } else {
                el.textContent = text;
            }
        } else {
            el.textContent = text;
        }
        syncNomeFaixa(el);
    }
    function flattenNome(el) {
        var text = el.innerText;
        el.innerHTML = '';
        el.textContent = text;
    }
    function syncAllNomeFaixas() {
        document.querySelectorAll('.edit-nome').forEach(formatNome);
    }
    // Aplica após fontes/layout renderizados
    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(syncAllNomeFaixas);
    }
    window.addEventListener('load', syncAllNomeFaixas);
    window.addEventListener('resize', syncAllNomeFaixas);
    // Atualiza ao editar o nome
    document.querySelectorAll('.edit-nome').forEach(function(el) {
        el.addEventListener('focus', function() { flattenNome(this); });
        el.addEventListener('blur', function() { formatNome(this); });
        el.addEventListener('input', function() { syncNomeFaixa(this); });
    });
    // --- Sincroniza largura do edit-classe com o texto (clip dinâmico da imagem de classe) ---
    var _classeMirror = document.createElement('span');
    _classeMirror.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;pointer-events:none;left:-9999px;top:-9999px;';
    document.body.appendChild(_classeMirror);
    var CLASSES_OCULTAS = ['provação', 'saga', 'altar', 'maison', 'capacidade', 'provacão', 'provacao'];
    function syncClasseWidth(input) {
        var val = input.value.trim();
        if (!val || CLASSES_OCULTAS.indexOf(val.toLowerCase()) !== -1) {
            input.style.display = 'none';
            return;
        }
        input.style.display = '';
        var cs = getComputedStyle(input);
        _classeMirror.style.font = cs.font;
        _classeMirror.style.fontSize = cs.fontSize;
        _classeMirror.style.fontFamily = cs.fontFamily;
        _classeMirror.style.fontStyle = cs.fontStyle;
        _classeMirror.style.letterSpacing = cs.letterSpacing;
        _classeMirror.style.padding = cs.paddingLeft + ' ' + cs.paddingRight;
        _classeMirror.textContent = input.value || '\u00a0';
        var textW = _classeMirror.offsetWidth;
        var padding = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight) + 16;
        var newW = Math.max(40, textW + padding);
        input.style.width = newW + 'px';
        // Alinha a imagem de classe ao card dinamicamente (mesmo princípio do syncNomeFaixa)
        var imgbox = input.closest('.carta-imgbox');
        if (imgbox) {
            var boxRect = imgbox.getBoundingClientRect();
            var inputRect = input.getBoundingClientRect();
            var leftOffset = inputRect.left - boxRect.left;
            input.style.backgroundSize = boxRect.width + 'px auto';
            input.style.backgroundPosition = (-leftOffset) + 'px center';
        }
    }
    function syncAllClasseWidths() {
        document.querySelectorAll('.edit-classe').forEach(syncClasseWidth);
    }
    window.addEventListener('load', syncAllClasseWidths);
    window.addEventListener('resize', syncAllClasseWidths);
    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(syncAllClasseWidths);
    }
    // Atualiza largura ao editar a classe (além da sincronização de tradução já existente)
    document.querySelectorAll('.edit-classe').forEach(function(input) {
        input.addEventListener('input', function() { syncClasseWidth(this); });
    });
    // --- Rank-select: altera rank da carta visualmente ---
    function aplicarRank(container, rank) {
        var faixa = container.querySelector('.nome-faixa');
        if (!faixa) return;
        for (var r = 0; r <= 8; r++) faixa.classList.remove('rank' + r);
        faixa.classList.add('rank' + rank);
        faixa.dataset.rank = rank;
    }
    document.querySelectorAll('.rank-select').forEach(function(sel) {
        sel.addEventListener('change', function() {
            aplicarRank(this.closest('.carta-container'), parseInt(this.value));
        });
    });
    </script>
</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)