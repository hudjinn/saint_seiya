# --- NOVO GERADOR: Layout das cartas igual ao gerar_editor_old.py, instruções e recursos novos ---
import os
import json
import re
from PIL import Image

IMAGES_DIR = "imagens_sem_texto"
IMAGES_ORIG_DIR = "imagens"
HTML_PATH = "editor.html"
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

# Coletar prefixos de efeitos globais (como no old)
efeito_prefixos = set()
for carta in cartas:
    efeito = carta.get("Efeito", "")
    efeito_limpo = re.sub(r'<[^>]+>', '', efeito)
    m = re.match(r'([A-Za-zÀ-ÿ\'’éàèêîôûçÉÀÈÊÎÔÛÇ ]+?)(?:\s*[-:–]|$)', efeito_limpo.strip())
    if m:
        prefixo = m.group(1).strip()
        if 2 < len(prefixo) < 30 and prefixo.lower() not in carta["Nome"].lower():
            efeito_prefixos.add(prefixo)
efeito_prefixos = sorted(efeito_prefixos)

# --- HTML ---
html = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Editor de Cartas Saint Seiya</title>
    <style>
        /* Ícones de efeito pequenos centralizados na base */
        .efeito-html img.stat, .efeito-html img[alt="Force"], .efeito-html img[alt="Cosmos"], .efeito-html img[alt="PV"], .efeito-html img[alt="Cura"], .efeito-html img[alt="Almas"], .efeito-html img[alt="Sceau"], .efeito-html img[alt="Compteur"] {
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-bottom: 0;
            margin-top: 8px;
            vertical-align: bottom;
        }
        body { font-family: Arial, sans-serif; background: #222; color: #eee; }
        .editar-pos-btn {
            background: #ffb347;
            color: #222;
            font-weight: bold;
            font-size: 1.1em;
            border: 2px solid #ffe066;
            border-radius: 8px;
            padding: 8px 22px;
            margin: 0 0 18px 0;
            box-shadow: 0 2px 12px #0008;
            letter-spacing: 1px;
            cursor:pointer;
            transition: filter .2s;
        }
        .efeito-move-btns {
            display: none;
            position: absolute;
            z-index: 100;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
        .efeito-move-btns.active {
            display: block;
        }
        .efeito-move-btn {
            position: absolute;
            background: #ffe066cc;
            color: #222;
            border: 1.5px solid #ffb347;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            font-size: 1.1em;
            font-weight: bold;
            text-align: center;
            line-height: 22px;
            cursor: pointer;
            pointer-events: auto;
            box-shadow: 0 2px 8px #0006;
            user-select: none;
        }
        .efeito-move-btn.up { top: -14px; left: 50%; transform: translateX(-50%); }
        .efeito-move-btn.down { bottom: -14px; left: 50%; transform: translateX(-50%); }
        .efeito-move-btn.left { left: -14px; top: 50%; transform: translateY(-50%); }
        .efeito-move-btn.right { right: -14px; top: 50%; transform: translateY(-50%); }
    .efeitos-lista { background: #181818; padding: 18px 24px; border-radius: 10px; margin: 24px auto 32px auto; }
    .efeitos-lista .row-container { display: flex; flex-wrap: wrap; gap: 24px 16px; justify-content: center; position: relative; }
    .efeitos-lista label { display: inline-block; min-width: 120px; font-weight: bold; }
    .efeitos-lista input { width: 220px; margin: 0 16px 8px 0; border-radius: 4px; border: 1px solid #888; padding: 4px 8px; font-size: 1.15em; }
    .efeitos-lista .efeito-row { margin-bottom: 8px; font-weight: 700; flex: 1 1 22%; max-width: 22%; min-width: 220px; background: #222; border-radius: 10px; padding: 18px 16px 10px 16px; box-shadow: 0 2px 12px #0006; display: flex; flex-direction: column; align-items: flex-start; box-sizing: border-box; }
    .efeitos-lista .efeito-orig { color: #ffe066; font-size: 1.18em; font-family: 'Georgia', serif; font-weight: bold; cursor: pointer; position: relative; }
    /* Removido: agora o tooltip dos efeitos será controlado por JS */
        .efeito-carta-tooltip {
            display: none;
            position: fixed;
            z-index: 1000;
            background: #222; border: 2px solid #ffe066; border-radius: 10px; padding: 10px 10px 6px 10px;
            box-shadow: 0 8px 32px #000a;
            min-width: 320px;
            text-align: center;
            pointer-events: auto;
            max-width: 420px;
            overflow: visible;
            left: 0; top: 0;
        }
        .efeitos-lista .efeito-btns { margin-top: 12px; }
        .efeitos-lista button { background: #4caf50; color: #fff; border: none; border-radius: 4px; padding: 6px 12px; cursor: pointer; margin-right: 8px; }
        .efeitos-lista input[type=file] { color: #fff; }
    .classes-lista { background: #181818; padding: 12px 18px; border-radius: 10px; margin: 0 auto 24px auto;}
    .classes-lista .row-container { display: flex; flex-wrap: wrap; gap: 20px 16px; justify-content: center; position: relative; }
    .classes-lista label { font-weight: bold; color: #ffe066; }
    .classes-lista input { width: 220px; margin: 0 12px 8px 0; border-radius: 4px; border: 1px solid #888; padding: 4px 8px; font-size: 1.15em; }
    .classes-lista .classe-row { margin-bottom: 6px; font-weight: 700; flex: 1 1 22%; max-width: 22%; min-width: 220px; background: #222; border-radius: 10px; padding: 18px 16px 10px 16px; box-shadow: 0 2px 12px #0006; display: flex; flex-direction: column; align-items: flex-start; box-sizing: border-box; }
        .carta { display: inline-block; margin: 24px; background: #333; padding: 12px; border-radius: 12px; vertical-align: top; box-shadow: 0 0 16px #000a; }
        .carta-imgbox { position: relative; margin-bottom: 0; }
        .carta.portrait .carta-imgbox { width: 350px; height: 500px; }
        .carta.landscape .carta-imgbox { width: 500px; height: 350px; }
    .carta.portrait .carta-img { width: 350px; height: 500px; border-radius: 12px; border: 2.5px solid #ffe066; box-shadow: 0 0 16px #000a; }
    .carta.landscape .carta-img { width: 500px; height: 350px; border-radius: 12px; border: 2.5px solid #ffe066; box-shadow: 0 0 16px #000a; }
        .edit-nome {
            position: absolute; top: 0px; left: 0; right: 0; width: 90%; margin: 0 auto;
            background: rgba(0,0,0,0.60); color: #fff; border-radius: 8px; border: 2px solid #111;
            padding: 6px 8px 2px 8px; font-size: 1.1em; font-family: 'Arial', Arial, sans-serif; font-weight: bold; text-align: center;
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            outline: none; letter-spacing: 1px;
        }
        .edit-classe {
            position: absolute; top: 41px; left: 0; right: 0; width: 80%; margin: 0 auto;
            background: rgba(0,0,0,0.32); color: #e0e0e0; border-radius: 4px; border: 1.5px solid #aaa;
            padding: 2px 6px; font-size: 0.95em; font-family: 'Georgia', serif; text-align: center;
            text-shadow: 1px 1px 4px #000, 0 0 2px #fff; outline: none; font-style: italic;
        }
        .efeito-box {
            position: absolute;
            left: 0; right: 0;
            bottom: 10px;
            z-index: 11;
            min-height: 32px;
            margin: 0 auto 6px auto;
            background: rgba(0,0,0,0.60); color: #fff; border-radius: 6px; border: 2px solid #888;
            padding: 8px 12px 8px 12px; font-size: 1.01em; text-align: center;
            text-shadow: 1px 1px 6px #000, 0 0 2px #000; outline: none; line-height: 1.18em;
            font-family: 'Times New Roman', 'Georgia', serif;
            box-sizing: border-box;
            width: 94%;
        }
        .efeitos-stack {
            position: absolute;
            left: 0; right: 0; bottom: 0;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .efeito-box em, .efeito-orig {
            color: #ff6666; font-style: normal; font-weight: bold; text-shadow: 1px 1px 4px #000;
        }
        .efeito-box .efeito-vaincu { color: #ffb84d; font-weight: bold; }
        .efeito-box .efeito-defausser { color: #ff4d4d; font-weight: bold; }
        .efeito-box .efeito-cosmos { color: #66b3ff; font-weight: bold; }
        .efeito-box .efeito-victoire { color: #ffe066; font-weight: bold; }
        .efeito-box .efeito-arrivee { color: #b3e6ff; font-weight: bold; }
        .efeito-box .custo { font-size: 1.1em; font-weight: bold; color: #ffe066; text-shadow: 1px 1px 4px #000; }
        .simbolo-btn { background: #222; color: #ffe066; border: 1px solid #ffe066; border-radius: 4px; padding: 2px 8px; font-size: 0.95em; margin-left: 6px; cursor: pointer; }
    </style>
</head>
<body>
    <div style="margin:0 auto 24px auto;">
        <div style="text-align:center;font-size:1.18em;color:#ffe066;background:#222;padding:16px 28px;border-radius:14px;box-shadow:0 0 14px #000;margin:32px auto 24px auto;">
            <b>Editor de Cartas Saint Seiya</b><br>
            Edite o <b>nome</b>, <b>classe</b> e <b>efeitos</b> de cada carta diretamente na lista abaixo.<br>
            Para traduzir rapidamente, utilize as caixas de tradução de <b>classes</b> e <b>efeitos globais</b> — ao alterar um termo, todas as cartas com aquele termo serão atualizadas automaticamente.<br>
            <span style="color:#b0e0ff;">Para restaurar partes da imagem original (ex: remover falhas da versão sem texto), clique no botão <span style="background:#ffe066;color:#222;padding:2px 8px;border-radius:5px;font-weight:bold;">✏️</span> na carta desejada, desenhe um retângulo sobre a área a restaurar e confirme com <b>✔</b> ou cancele com <b>✖</b>. A restauração é visual e não altera o arquivo original.</span><br>
            <span style="color:#ffe066;font-size:0.98em;">Use <b>Exportar JSON</b> para salvar seu progresso e <b>Importar JSON</b> para continuar depois.</span>
        </div>
        <div style="text-align:center;margin-bottom:24px;">
            <button type="button" onclick="exportarJson()" style="background: linear-gradient(90deg,#ffe066 0%,#ffb347 100%); color: #222; font-weight: bold; font-size: 1.25em; border: 2.5px solid #ffb347; border-radius: 10px; padding: 12px 32px; margin: 0 18px 8px 0; box-shadow: 0 2px 12px #0008; letter-spacing: 1px; transition: filter .2s; cursor:pointer;">⬇ Exportar JSON</button>
            <button type="button" onclick="document.getElementById('importar-arquivo').click()" style="background: linear-gradient(90deg,#66e0ff 0%,#3ad29f 100%); color: #222; font-weight: bold; font-size: 1.25em; border: 2.5px solid #3ad29f; border-radius: 10px; padding: 12px 32px; margin: 0 0 8px 0; box-shadow: 0 2px 12px #0008; letter-spacing: 1px; transition: filter .2s; cursor:pointer;">⬆ Importar JSON</button>
            <input type="file" id="importar-arquivo" style="display:none" accept="application/json" onchange="importarJson(event)">
        </div>
        <div class="classes-lista">
            <h2>Tradução de Classes Comuns</h2>
            <form id="classes-form">
'''
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
        html += f'''<div class="classe-row">
            <span class="classe-orig classe-hover">{classe}
                <span class="classe-carta-tooltip" style="display:none;position:absolute;left:0;top:28px;z-index:1000;background:#222;border:2px solid #ffe066;border-radius:10px;padding:10px 10px 6px 10px;box-shadow:0 8px 32px #000a;min-width:320px;text-align:center;max-width:420px;overflow:visible;">
                    <img src="{img_exemplo}" alt="{nome_exemplo}" style="max-width:320px;max-height:460px;box-shadow:0 0 16px #000;border-radius:10px;border:2px solid #ffe066;background:#222;"><br>
                    <span style="color:#ffe066;font-size:1.1em;font-weight:bold;">{nome_exemplo}</span>
                </span>
            </span>
            <input type="text" class="classe-trad" data-orig="{classe}" value="{classe}">
        </div>\n'''
    else:
        html += f'''<div class="classe-row">
            <span class="classe-orig">{classe}</span>
            <input type="text" class="classe-trad" data-orig="{classe}" value="{classe}">
        </div>\n'''
html += '</div>'
html += '''
    <!-- Botões removidos daqui -->
        </form>
    </div>
    <div class="efeitos-lista">
        <h2>Tradução de Efeitos Globais</h2>
        <form id="efeitos-form">
'''
# Lista de efeitos para tradução
html += '<div class="row-container">'
efeito_para_carta = {}
for kw in efeito_prefixos:
    carta_exemplo = None
    for carta in cartas:
        efeito = None
        efeitos = carta.get("effects")
        if efeitos and isinstance(efeitos, list) and efeitos:
            # Se for lista de dicts, pega o campo 'text' do primeiro
            if isinstance(efeitos[0], dict) and 'text' in efeitos[0]:
                efeito = efeitos[0]['text']
            else:
                efeito = efeitos[0]
        else:
            efeito = carta.get("Efeito", "")
        if not isinstance(efeito, str):
            continue
        efeito_limpo = re.sub(r'<[^>]+>', '', efeito)
        m = re.match(r"([A-Za-zÀ-ÿ'’éàèêîôûçÉÀÈÊÎÔÛÇ ]+?)(?:\s*[-:–]|$)", efeito_limpo.strip())
        if m and m.group(1).strip() == kw:
            carta_exemplo = carta
            break
    if carta_exemplo:
        img_exemplo = os.path.join(IMAGES_ORIG_DIR, os.path.basename(carta_exemplo["image"]))
        nome_exemplo = carta_exemplo["Nome"]
        html += f'''<div class="efeito-row">
            <span class="efeito-orig efeito-hover">{kw}
                <span class="efeito-carta-tooltip"><img src="{img_exemplo}" alt="{nome_exemplo}" style="max-width:320px;max-height:460px;box-shadow:0 0 16px #000;border-radius:10px;border:2px solid #ffe066;background:#222;"><br><span style="color:#ffe066;font-size:1.1em;font-weight:bold;">{nome_exemplo}</span></span>
            </span>
            <input type="text" class="efeito-trad" data-orig="{kw}" value="{kw}">
        </div>\n'''
    else:
        html += f'''<div class="efeito-row">
            <span class="efeito-orig">{kw}</span>
            <input type="text" class="efeito-trad" data-orig="{kw}" value="{kw}">
        </div>\n'''
html += '</div>'
html += '''
    <!-- Botões removidos daqui -->
        </form>
    </div>
        <div id="editar-pos-container" style="text-align:center;margin:32px auto 18px auto;max-width:900px;">
        <button type="button" class="editar-pos-btn" id="editar-pos-btn">Editar Posição dos Efeitos</button>
        <span id="editar-pos-info" style="display:block;color:#ffe066;font-size:1.05em;margin-top:8px;">Clique para ativar/desativar o modo de edição de posição dos efeitos. Use as setas que aparecem sobre cada efeito para mover.</span>
    </div>
    <div id="cartas">
'''

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
            if isinstance(ef, dict):
                if ef.get("html"):
                    efeitos_html.append(ef["html"])
                elif ef.get("text"):
                    efeitos_html.append(ef["text"])
            elif isinstance(ef, str):
                efeitos_html.append(ef)
    else:
        efeito_fallback = carta.get("Efeito", "")
        efeitos_html = split_efeitos_html(efeito_fallback)
    aspect = get_aspect(img)
    html += f'''<div class="carta {aspect}">
    
        <div class="carta-imgbox" style="position:relative;width:{'350px;height:500px;' if aspect=='portrait' else '500px;height:350px;'}">
            <img src="{img}" alt="{nome}" class="carta-img" style="display:block;position:relative;z-index:10;">
            <div contenteditable="true" class="edit-nome" style="z-index:20;">{nome}</div>
            <div contenteditable="true" class="edit-classe" data-orig="{classe}" style="z-index:20;">{classe}</div>
            <img src="{img_orig}" class="restaurar-preview" style="display:none;position:absolute;left:0;top:0;width:100%;height:100%;z-index:31;pointer-events:none;">
            <canvas class="restaurar-canvas" style="display:none;position:absolute;left:0;top:0;width:100%;height:100%;z-index:99;pointer-events:auto;"></canvas>
            <span class="carta-ref-hover" style="position:absolute;top:8px;right:8px;z-index:20;">
                <span class="carta-ref-icone" style="display:inline-block;width:28px;height:28px;background:#ffe066;border-radius:50%;box-shadow:0 0 6px #000;cursor:pointer;text-align:center;line-height:28px;font-size:1.2em;font-weight:bold;">🔍</span>
                <span class="carta-ref-tooltip" style="display:none;position:absolute;right:32px;top:-8px;z-index:30;background:#222;border:2px solid #ffe066;border-radius:10px;padding:10px 10px 6px 10px;box-shadow:0 8px 32px #000a;min-width:320px;text-align:center;">
                    <img src="{img_orig}" alt="{nome}" style="max-width:320px;max-height:460px;box-shadow:0 0 16px #000;border-radius:10px;border:2px solid #ffe066;background:#222;\"><br>
                    <span style="color:#ffe066;font-size:1.1em;font-weight:bold;">{nome}</span>
                </span>
            </span>
            <span class="restaurar-btn" title="Restaurar pedaço da imagem" style="position:absolute;top:8px;left:8px;z-index:21;cursor:pointer;font-size:1.3em;background:#222;border-radius:50%;padding:2px 6px;color:#ffe066;border:2px solid #ffe066;">✏️</span>
            <div class="restaurar-toolbar" style="display:none;position:absolute;top:44px;left:8px;z-index:120;">
                <button class="restaurar-ok" title="Salvar restauração" style="font-size:1.2em;background:#4caf50;color:#fff;border:none;border-radius:4px;padding:2px 8px;margin-right:4px;">✔</button>
                <button class="restaurar-cancel" title="Cancelar" style="font-size:1.2em;background:#b33;color:#fff;border:none;border-radius:4px;padding:2px 8px;">✖</button>
            </div>
            <div class="efeitos-stack">
''' + ''.join([
    f'<div contenteditable="true" class="efeito-box" style="position:absolute;left:0;right:0;bottom:{10+idx*44}px;z-index:11;min-height:32px;margin:0 auto 6px auto;background:rgba(0,0,0,0.60);color:#fff;border-radius:6px;border:2px solid #888;padding:8px 12px 8px 12px;font-size:1.01em;text-align:center;text-shadow:1px 1px 6px #000,0 0 2px #000;outline:none;line-height:1.18em;font-family:\'Times New Roman\',\'Georgia\',serif;box-sizing:border-box;width:94%;' 
    f'" data-pos-x="0" data-pos-y="0">{ef_html}'
    f'<div class="efeito-move-btns" style="pointer-events:none;">'
    f'<button class="efeito-move-btn up" title="Mover para cima" style="pointer-events:auto;">↑</button>'
    f'<button class="efeito-move-btn down" title="Mover para baixo" style="pointer-events:auto;">↓</button>'
    f'<button class="efeito-move-btn left" title="Mover para a esquerda" style="pointer-events:auto;">←</button>'
    f'<button class="efeito-move-btn right" title="Mover para a direita" style="pointer-events:auto;">→</button>'
    f'</div></div>'
    for idx, ef_html in enumerate(efeitos_html)
]) + '''
            </div>
        </div>
    </div>
    '''
html += '''
    </div>
    <p style="margin-top:40px;">Edite o nome, classe e os efeitos sobre a carta. Para salvar, exporte o JSON ou importe para continuar a tradução depois.</p>
    <script>
    // --- Edição de posição dos efeitos ---
    (function(){
        var editandoPos = false;
        var btnEditarPos = document.getElementById('editar-pos-btn');
        btnEditarPos.addEventListener('click', function() {
            editandoPos = !editandoPos;
            document.querySelectorAll('.efeito-move-btns').forEach(function(btns){
                if(editandoPos) btns.classList.add('active');
                else btns.classList.remove('active');
            });
            btnEditarPos.style.background = editandoPos ? '#ffe066' : '#ffb347';
            btnEditarPos.style.color = editandoPos ? '#222' : '#222';
            btnEditarPos.innerText = editandoPos ? 'Sair do Modo Edição de Posição' : 'Editar Posição dos Efeitos';
        });
        document.querySelectorAll('.efeito-box').forEach(function(box){
            var btns = box.querySelector('.efeito-move-btns');
            var up = btns.querySelector('.up');
            var down = btns.querySelector('.down');
            var left = btns.querySelector('.left');
            var right = btns.querySelector('.right');
            function move(dx,dy){
                var x = parseInt(box.getAttribute('data-pos-x')||'0',10)+dx;
                var y = parseInt(box.getAttribute('data-pos-y')||'0',10)+dy;
                box.setAttribute('data-pos-x',x);
                box.setAttribute('data-pos-y',y);
                box.style.transform = `translate(${x}px,${y}px)`;
            }
            up.addEventListener('click',function(e){e.stopPropagation();move(0,-1);});
            down.addEventListener('click',function(e){e.stopPropagation();move(0,1);});
            left.addEventListener('click',function(e){e.stopPropagation();move(-1,0);});
            right.addEventListener('click',function(e){e.stopPropagation();move(1,0);});
        });
    })();
    // Tradução automática de classes
    document.querySelectorAll('.classe-trad').forEach(function(input) {
        input.addEventListener('input', function() {
            var orig = this.getAttribute('data-orig');
            var trad = this.value;
            document.querySelectorAll('.edit-classe').forEach(function(div) {
                if (div.getAttribute('data-orig') === orig) {
                    div.innerText = trad;
                }
            });
        });
    });
    // Atualiza todos os efeitos ao editar a tradução global
    document.querySelectorAll('.efeito-trad').forEach(function(input) {
        input.addEventListener('input', function() {
            var orig = this.getAttribute('data-orig');
            var trad = this.value;
            document.querySelectorAll('.efeito-box').forEach(function(div) {
                div.innerHTML = div.innerHTML.replace(new RegExp(orig, 'g'), trad);
            });
        });
    });
    // Exportar JSON
    function exportarJson() {
        var cartas = [];
        document.querySelectorAll('.carta').forEach(function(cartaDiv) {
            var nome = cartaDiv.querySelector('.edit-nome').innerText;
            var classe = cartaDiv.querySelector('.edit-classe').innerText;
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
    document.querySelectorAll('.carta').forEach(function(cartaDiv) {
        var btn = cartaDiv.querySelector('.restaurar-btn');
        var canvas = cartaDiv.querySelector('.restaurar-canvas');
        var imgSemTexto = cartaDiv.querySelector('.carta-img');
        var imgOriginal = cartaDiv.querySelector('.restaurar-preview');
        var toolbar = cartaDiv.querySelector('.restaurar-toolbar');
        var drawing = false, startX = 0, startY = 0, endX = 0, endY = 0, rect = null;
        var restauracoes = [];
        if (cartaDiv.dataset.restauracoes) {
            restauracoes = JSON.parse(cartaDiv.dataset.restauracoes);
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
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            syncCanvasSize();
            canvas.style.display = 'block';
            imgOriginal.style.display = 'block';
            toolbar.style.display = 'flex';
            drawAllRestauracoes();
        });
        canvas.addEventListener('mousedown', function(e) {
            if (canvas.style.display !== 'block') return;
            drawing = true;
            var rectC = canvas.getBoundingClientRect();
            // Considera scroll e border
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
        toolbar.querySelector('.restaurar-ok').addEventListener('click', function(e) {
            if (rect && rect.w > 0 && rect.h > 0) {
                // Aplica o pedaço restaurado na imagem sem texto
                // Cria um canvas temporário do tamanho da imagem sem texto
                var tempCanvas = document.createElement('canvas');
                tempCanvas.width = imgSemTexto.naturalWidth;
                tempCanvas.height = imgSemTexto.naturalHeight;
                var tempCtx = tempCanvas.getContext('2d');
                // Desenha a imagem sem texto inteira
                tempCtx.drawImage(imgSemTexto, 0, 0);
                // Copia o pedaço da imagem original para a área selecionada
                tempCtx.drawImage(imgOriginal, rect.x, rect.y, rect.w, rect.h, rect.x, rect.y, rect.w, rect.h);
                // Atualiza o src da imagem sem texto
                imgSemTexto.src = tempCanvas.toDataURL('image/webp');
                // Atualiza as restaurações salvas
                restauracoes.push(rect);
                cartaDiv.dataset.restauracoes = JSON.stringify(restauracoes);
                drawAllRestauracoes();
            }
            rect = null;
            canvas.style.display = 'none';
            imgOriginal.style.display = 'none';
            toolbar.style.display = 'none';
        });
        toolbar.querySelector('.restaurar-cancel').addEventListener('click', function(e) {
            rect = null;
            canvas.style.display = 'none';
            imgOriginal.style.display = 'none';
            toolbar.style.display = 'none';
            drawAllRestauracoes();
        });
        window.addEventListener('resize', function() {
            if (canvas.style.display === 'block') {
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
            if (tooltip.style.display === 'block') {
                tooltip.style.display = 'none';
            } else {
                tooltip.style.display = 'block';
            }
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
    </script>
</body>
</html>
'''

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)