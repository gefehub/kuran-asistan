"""Génère les fiches Coran (PDF) depuis fiches.json.
Police arabe : Amiri — la fatha est placée AU-DESSUS de la chadda (jamais en dessous).
Usage : python3 render.py fiches.json outdir [id ...]
"""
import json, sys, os, html, re
from playwright.sync_api import sync_playwright

CSS = r"""
@page{size:720px auto;margin:0}
*{box-sizing:border-box}
html,body{margin:0;background:#f3efe6;color:#25221d;font-family:"DejaVu Sans",system-ui,sans-serif;font-size:13.3px;line-height:1.5}
.page{width:720px;padding:22px 30px 26px}
header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:4px solid #1f5e4f;padding-bottom:10px;margin-bottom:16px}
h1{margin:0;font-size:30px;line-height:1.1;color:#1f5e4f;font-weight:700}
.sub{color:#8a8070;font-size:12.5px}
.ar{font-family:"Amiri",serif;direction:rtl;color:#1f5e4f;font-feature-settings:"ss01" 0}
.ayet{background:#fffdf8;border:1.5px solid #e2d8c4;border-radius:14px;padding:16px 22px;text-align:right;font-size:32px;line-height:2.2}
.meal{margin:12px 2px 0;font-size:13px}
.meal b{font-weight:700}
.label{margin:20px 2px 10px;color:#a8552e;font-weight:700;font-size:11.5px;letter-spacing:2.4px;text-transform:uppercase}
.parca{background:#fffdf8;border:1.5px solid #e2d8c4;border-radius:14px;padding:12px 16px 14px;margin-bottom:12px}
.top{display:flex;justify-content:space-between;align-items:center}
.num{width:22px;height:22px;border-radius:50%;background:#1f5e4f;color:#fff;font-weight:700;font-size:11.5px;display:flex;align-items:center;justify-content:center}
.pa{font-size:27px;line-height:1.9}
.tr{margin:0 0 0 38px;font-size:13px}
.tr span{color:#a8552e}
.words{display:flex;flex-direction:row-reverse;flex-wrap:wrap;gap:7px;border-top:1.5px dashed #e2d8c4;margin-top:8px;padding-top:10px}
.w{background:#fffdf8;border:1.5px solid #e2d8c4;border-radius:9px;padding:3px 10px 5px;text-align:center;min-width:64px}
.w .ar{font-size:21px;line-height:1.85;display:block}
.w b{display:block;font-size:11.5px;line-height:1.3}
.w i{display:block;font-style:normal;color:#a8552e;font-size:10px;line-height:1.3}
.vk{font-size:.55em;position:relative;top:-1.15em;margin:0 2px 0 0;line-height:0}
.genel{background:#1f5e4f;color:#fff;border-radius:12px;padding:12px 16px;font-size:13px}
"""

# Texte source : encodage Unicode des mushafs turcs (Diyanet / Açık Kuran).
# Affichage : ۪ (U+06EA) = esre du mushaf turc -> kasra ; signes de vakf Secavendi en petites lettres.
VAKF = {"\u06DC": "ط", "\u06D8": "م", "\u06DA": "ج", "\u06D9": "لا", "\u06D6": "ص", "\u06E2": "م"}
def tr_marks(s):
    s = s.replace("\u06EA", "\u0650")
    return re.sub("[" + "".join(VAKF) + "]", lambda m: '<span class="vk">' + VAKF[m.group(0)] + '</span>', s)

def fiche_html(f):
    # les signes de pause (ۖ ۗ ۚ …) collés au mot précédent pour qu'ils restent au-dessus de lui
    e = lambda s: tr_marks(html.escape(re.sub(r'\s+([\u06D6-\u06DC\u06E2])', r'\1', s)))
    parts = []
    for i, p in enumerate(f["parcalar"], 1):
        words = "".join(
            f'<div class="w"><span class="ar">{e(a)}</span><b>{e(t)}</b>' + (f'<i>{e(k)}</i>' if k else "") + "</div>"
            for a, t, k in p["kelimeler"])
        parts.append(f'<div class="parca"><div class="top"><div class="num">{i}</div><div class="ar pa">{e(p["ar"])}</div></div>'
                     f'<p class="tr"><span>→</span> {e(p["tr"])}</p><div class="words">{words}</div></div>')
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="page">
<header><h1>{e(f['sure'])} {f['ayet']}</h1><div class="sub">Tekrar kartı · {('Sayfa ' + str(f['sayfa']) + ' · ') if f.get('sayfa') else ''}{e(f['titre'])}</div></header>
<div class="ayet ar">{e(f['ayet_ar'])}</div>
<p class="meal"><b>{e(f['meal_label'])}</b> {e(f['meal'])}</p>
<div class="label">Parça parça</div>
{''.join(parts)}
<div class="label">Genel anlamı</div>
<div class="genel">{e(f['genel'])}</div>
</div></body></html>"""

def main():
    data = json.load(open(sys.argv[1])); out = sys.argv[2]; only = set(sys.argv[3:])
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 720, "height": 900})
        for f in data:
            if only and f["id"] not in only: continue
            h = fiche_html(f)
            open(os.path.join(out, f["id"] + ".html"), "w").write(h)
            pg.set_content(h); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
            height = pg.evaluate("Math.ceil(document.querySelector('.page').getBoundingClientRect().height)")
            pg.pdf(path=os.path.join(out, f["id"] + ".pdf"), width="720px", height=f"{height+1}px", print_background=True,
                   margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            print(f["id"], height)
        b.close()

if __name__ == "__main__":
    main()
