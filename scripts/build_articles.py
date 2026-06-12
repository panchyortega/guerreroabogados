#!/usr/bin/env python3
"""
build_articles.py
Lee el Google Sheet de Guerrero Abogados y genera las páginas HTML
del Centro de Ayuda automáticamente.

Columnas del Sheet (fila 1 = encabezados):
  A: categoria       — slug de la categoría (ej: deudas, laboral, contratos...)
  B: subcategoria    — texto libre (ej: "Juicios ejecutivos", "Contratos laborales")
  C: titulo          — título del artículo (ej: ¿Qué es un juicio ejecutivo?)
  D: subtitulo       — bajada corta debajo del título
  E: contenido       — cuerpo en Markdown (párrafos, ## subtítulos, listas)
  F: wa_mensaje      — mensaje prellenado de WhatsApp (sin encode)
  G: publicado       — SI para publicar, NO o vacío para borrador
"""

import os, re, json, sys, unicodedata
import requests
import markdown as md_lib

# ── Configuración ──────────────────────────────────────────────────────────────
SHEET_ID   = os.environ.get("SHEET_ID", "1qsPSjlMgp7o_qV_vTWHg2vTHLeWnUIzaoo23P_eaDoc")
SHEET_URL_ARTICLES   = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoBgppXXeZFPo1IuAqaKISWPzoC0Cfis2q13e5_nKlY8ns9hL1ZAMXDVzlx1ynKHdRK9dQEmSivWsJ/pub?gid=0&single=true&output=csv"
SHEET_URL_CATEGORIES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoBgppXXeZFPo1IuAqaKISWPzoC0Cfis2q13e5_nKlY8ns9hL1ZAMXDVzlx1ynKHdRK9dQEmSivWsJ/pub?gid=1831731050&single=true&output=csv"
AYUDA_DIR  = os.path.join(os.path.dirname(__file__), "..", "ayuda")
WA_NUMBER  = "56983937954"
WA_DEFAULT = "Hola%2C%20quisiera%20realizar%20una%20consulta%20legal%20con%20Guerrero%20Abogados."

CATEGORIES = {
    "deudas":      {"title": "Deudas, cobranzas y juicios ejecutivos", "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>'},
    "contratos":   {"title": "Contratos y negocios",                   "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'},
    "laboral":     {"title": "Derecho laboral",                        "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>'},
    "propiedades": {"title": "Propiedades y vivienda",                 "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'},
    "migratorio":  {"title": "Derecho migratorio",                     "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'},
    "civil":       {"title": "Derecho civil general",                  "icon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 6h18M3 12h18M3 18h18"/></svg>'},
}

WA_DEFAULTS = {
    "deudas":      "Hola%2C%20quisiera%20realizar%20una%20consulta%20sobre%20deudas%2C%20cobranzas%20o%20juicio%20ejecutivo.",
    "contratos":   "Hola%2C%20quisiera%20realizar%20una%20consulta%20sobre%20redacci%C3%B3n%20o%20revisi%C3%B3n%20de%20contratos.",
    "laboral":     "Hola%2C%20quisiera%20realizar%20una%20consulta%20sobre%20derecho%20laboral.",
    "propiedades": "Hola%2C%20quisiera%20realizar%20una%20consulta%20sobre%20regularizaci%C3%B3n%20de%20propiedades%20o%20vivienda.",
    "migratorio":  "Hola%2C%20quisiera%20realizar%20una%20consulta%20sobre%20derecho%20migratorio.",
    "civil":       "Hola%2C%20quisiera%20realizar%20una%20consulta%20sobre%20derecho%20civil.",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def slugify(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    return text[:80]

def wa_encode(msg):
    if not msg:
        return WA_DEFAULT
    return requests.utils.quote(msg.strip(), safe="")

def markdown_to_html(text):
    """Convert markdown to HTML. Supports ## headings, paragraphs, - lists, * lists."""
    return md_lib.markdown(text, extensions=["nl2br"])

def wa_icon():
    return '<svg class="btn__icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.556 4.112 1.529 5.836L.057 23.215a.75.75 0 0 0 .928.928l5.379-1.472A11.952 11.952 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22a9.956 9.956 0 0 1-5.063-1.378l-.363-.214-3.742 1.023 1.023-3.742-.214-.363A9.956 9.956 0 0 1 2 12C2 6.486 6.486 2 12 2s10 4.486 10 10-4.486 10-10 10z"/></svg>'

# ── Header / Footer shared HTML ────────────────────────────────────────────────
def shared_header(active_link, depth=2):
    prefix = "../" * depth
    return f"""  <header class="header" id="header">
    <div class="header__inner container">
      <a href="{prefix}index.html" class="header__logo"><span class="header__logo-main">Guerrero</span><span class="header__logo-sub">Abogados</span></a>
      <nav class="header__nav"><ul class="header__nav-list">
        <li><a href="{prefix}index.html#servicios" class="header__nav-link">Servicios</a></li>
        <li><a href="{prefix}index.html#contacto" class="header__nav-link">Contacto</a></li>
        <li><a href="{prefix}index.html#preguntas" class="header__nav-link">Preguntas frecuentes</a></li>
        <li><a href="{prefix}ayuda/index.html" class="header__nav-link active">Centro de ayuda</a></li>
      </ul></nav>
      <a href="https://wa.me/{WA_NUMBER}?text={WA_DEFAULT}" class="btn btn--whatsapp header__cta" target="_blank" rel="noopener noreferrer">
        {wa_icon()} Contactar por WhatsApp
      </a>
      <button class="header__burger" aria-label="Abrir menú" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
    </div>
    <div class="mobile-menu" id="mobile-menu" aria-hidden="true">
      <nav><ul class="mobile-menu__list">
        <li><a href="{prefix}index.html#servicios" class="mobile-menu__link">Servicios</a></li>
        <li><a href="{prefix}index.html#contacto" class="mobile-menu__link">Contacto</a></li>
        <li><a href="{prefix}index.html#preguntas" class="mobile-menu__link">Preguntas frecuentes</a></li>
        <li><a href="{prefix}ayuda/index.html" class="mobile-menu__link">Centro de ayuda</a></li>
        <li><a href="https://wa.me/{WA_NUMBER}?text={WA_DEFAULT}" class="btn btn--whatsapp mobile-menu__cta" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
      </ul></nav>
    </div>
  </header>"""

def shared_footer(depth=2):
    prefix = "../" * depth
    return f"""  <footer class="footer">
    <div class="container">
      <div class="footer__grid">
        <div class="footer__brand">
          <p class="footer__logo">Guerrero Abogados</p>
          <p class="footer__tagline">Asesoría legal directa y personalizada en Santiago Centro.</p>
          <p class="footer__addr">Santa Lucía 344, Oficina 41 · Santiago Centro · +56 9 8393 7954</p>
        </div>
        <div class="footer__col">
          <h3 class="footer__col-title">Centro de Ayuda</h3>
          <ul class="footer__links">
            <li><a href="{prefix}ayuda/deudas/index.html">Deudas y cobranzas</a></li>
            <li><a href="{prefix}ayuda/contratos/index.html">Contratos y negocios</a></li>
            <li><a href="{prefix}ayuda/laboral/index.html">Derecho laboral</a></li>
            <li><a href="{prefix}ayuda/propiedades/index.html">Propiedades</a></li>
            <li><a href="{prefix}ayuda/migratorio/index.html">Derecho migratorio</a></li>
            <li><a href="{prefix}ayuda/civil/index.html">Derecho civil</a></li>
          </ul>
        </div>
        <div class="footer__col">
          <h3 class="footer__col-title">Contacto</h3>
          <ul class="footer__links">
            <li><a href="https://wa.me/{WA_NUMBER}" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
            <li><a href="mailto:guerreroabogados_@outlook.com">guerreroabogados_@outlook.com</a></li>
            <li><a href="{prefix}index.html">Volver al sitio principal</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__bottom">
        <p>© 2026 Guerrero Abogados. Todos los derechos reservados.</p>
        <p class="footer__legal">La información contenida en este Centro de Ayuda es de carácter general y no constituye asesoría legal específica. Para revisar tu caso, contáctanos directamente.</p>
      </div>
    </div>
  </footer>
  <a href="https://wa.me/{WA_NUMBER}?text={WA_DEFAULT}" class="whatsapp-float" target="_blank" rel="noopener noreferrer" aria-label="Contactar por WhatsApp">
    {wa_icon()}
  </a>
  <script src="{prefix}ayuda/ayuda.js"></script>"""

# ── Article page generator ─────────────────────────────────────────────────────
def build_article(article, cat_slug, cat_title, wa_msg):
    slug = article["slug"]
    title = article["titulo"]
    subtitle = article.get("subtitulo", "")
    body_html = markdown_to_html(article.get("contenido", ""))
    depth = 2  # ayuda/cat/article.html

    breadcrumb = f"""  <nav class="breadcrumb" aria-label="Ruta de navegación">
    <div class="container">
      <ol class="breadcrumb__list">
        <li class="breadcrumb__item"><a href="../../ayuda/index.html">Centro de Ayuda</a><span class="breadcrumb__sep">/</span></li>
        <li class="breadcrumb__item"><a href="index.html">{cat_title}</a><span class="breadcrumb__sep">/</span></li>
        <li class="breadcrumb__item breadcrumb__item--current">{title}</li>
      </ol>
    </div>
  </nav>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | {cat_title} | Guerrero Abogados</title>
  <meta name="description" content="{subtitle or title}. Guerrero Abogados, Santiago Centro." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../../ayuda/ayuda.css" />
</head>
<body>
{shared_header("ayuda", depth)}
{breadcrumb}
  <main>
    <div class="container">
      <div class="article-layout">
        <article class="article-content">
          <header class="article-header">
            <a href="index.html" class="article-header__category">{cat_title}</a>
            <h1 class="article-header__title">{title}</h1>
            {f'<p class="article-header__subtitle">{subtitle}</p>' if subtitle else ''}
          </header>
          <div class="article-body">
            {body_html}
            <div class="note">
              <strong>Nota:</strong> Esta información es de carácter general y no reemplaza una asesoría legal personalizada. Cada caso puede presentar particularidades que conviene revisar directamente con un abogado.
            </div>
          </div>
          <div class="article-cta">
            <h2 class="article-cta__title">¿Tienes más dudas?</h2>
            <p class="article-cta__desc">Escríbenos por WhatsApp y conversemos sobre tu caso.</p>
            <a href="https://wa.me/{WA_NUMBER}?text={wa_msg}" class="btn btn--whatsapp btn--lg" target="_blank" rel="noopener noreferrer">
              {wa_icon()} Escribirnos por WhatsApp
            </a>
          </div>
        </article>
      </div>
    </div>
  </main>
{shared_footer(depth)}
</body>
</html>"""

# ── Category index page generator ─────────────────────────────────────────────
def build_category_index(cat_slug, cat_info, articles_by_subcat, wa_msg):
    cat_title = cat_info["title"]
    desc = cat_info.get("desc", "")
    depth = 1

    # Build article list grouped by subcategory
    total = sum(len(v) for v in articles_by_subcat.values())
    if total == 0:
        articles_html = '<p class="cat-empty">Aún no hay artículos en esta categoría. Vuelve pronto.</p>'
    else:
        articles_html = ""
        for subcat, articles in articles_by_subcat.items():
            if subcat:
                articles_html += f'\n        <h3 class="cat-subcat-title">{subcat}</h3>\n'
            articles_html += '\n        <nav class="article-list">\n'
            for art in articles:
                articles_html += f"""          <a href="{art['slug']}.html" class="article-item">
            <span class="article-item__title">{art['titulo']}</span>
            <svg class="article-item__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>\n"""
            articles_html += "        </nav>\n" 

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{cat_title} | Centro de Ayuda | Guerrero Abogados</title>
  <meta name="description" content="Artículos sobre {cat_title.lower()}. Guerrero Abogados, Santiago Centro." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../ayuda.css" />
</head>
<body>
{shared_header("ayuda", 1)}
  <nav class="breadcrumb" aria-label="Ruta de navegación">
    <div class="container">
      <ol class="breadcrumb__list">
        <li class="breadcrumb__item"><a href="../index.html">Centro de Ayuda</a><span class="breadcrumb__sep">/</span></li>
        <li class="breadcrumb__item breadcrumb__item--current">{cat_title}</li>
      </ol>
    </div>
  </nav>
  <main>
    <div class="container">
      <div class="cat-layout">
        <div class="cat-layout__main">
          <div class="cat-header">
            <h1 class="cat-header__title">{cat_title}</h1>
            <p class="cat-header__desc">{desc}</p>
          </div>
          {articles_html}
        </div>
      </div>
    </div>
  </main>
{shared_footer(1)}
</body>
</html>"""

def update_category_counts(by_cat, active_categories=None):
    """Update article count and descriptions on each cat-card in ayuda/index.html."""
    if active_categories is None:
        active_categories = CATEGORIES
    index_path = os.path.join(AYUDA_DIR, "index.html")
    if not os.path.exists(index_path):
        return
    html = open(index_path).read()
    for cat_slug, cat_info in active_categories.items():
        total = sum(len(v) for v in by_cat.get(cat_slug, {}).values())
        label = f"{total} artículo{'s' if total != 1 else ''}"
        title = cat_info.get("title", "")
        desc = cat_info.get("desc", "")

        # Update count
        html = re.sub(
            rf'(data-cat="{cat_slug}"[^>]*>.*?<span class="cat-card__count">)[^<]*(</span>)',
            rf'\g<1>{label}\g<2>',
            html, flags=re.DOTALL
        )
        # Update title
        if title:
            html = re.sub(
                rf'(data-cat="{cat_slug}"[^>]*>.*?<h3 class="cat-card__title">)[^<]*(</h3>)',
                rf'\g<1>{title}\g<2>',
                html, flags=re.DOTALL
            )
        # Update description
        if desc:
            html = re.sub(
                rf'(data-cat="{cat_slug}"[^>]*>.*?<p class="cat-card__desc">)[^<]*(</p>)',
                rf'\g<1>{desc}\g<2>',
                html, flags=re.DOTALL
            )
    open(index_path, "w").write(html)
    print("  📊 Cards de categorías actualizadas en ayuda/index.html")



def rebuild_ayuda_index(active_categories, by_cat):
    """Rebuild ayuda/index.html from scratch based on current categories."""
    index_path = os.path.join(AYUDA_DIR, "index.html")
    if not os.path.exists(index_path):
        print("  ⚠️  ayuda/index.html no encontrado, no se puede reconstruir")
        return

    html = open(index_path).read()

    # Build new cards grid
    cards_html = ""
    for cat_slug, cat_info in active_categories.items():
        total = sum(len(v) for v in by_cat.get(cat_slug, {}).values())
        label = f"{total} artículo{'s' if total != 1 else ''}"
        title = cat_info.get("title", cat_slug)
        desc = cat_info.get("desc", "")
        wa_msg = WA_DEFAULTS.get(cat_slug, WA_DEFAULT)

        cards_html += f"""
        <a href="{cat_slug}/index.html" class="cat-card reveal" data-cat="{cat_slug}" aria-label="Categoría: {title}">
          <h3 class="cat-card__title">{title}</h3>
          <p class="cat-card__desc">{desc}</p>
          <span class="cat-card__count">{label}</span>
          <span class="cat-card__arrow">Ver artículos <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
        </a>
"""

    # Replace the grid content
    import re as re2
    html = re2.sub(
        r'(<div class=\"help-categories__grid\">).*?(</div>\s*</section>)',
        lambda m: m.group(1) + "\n" + cards_html + "\n      </div>\n  </section>",
        html,
        flags=re2.DOTALL,
        count=1
    )
    open(index_path, "w").write(html)
    print(f"  🗂️  ayuda/index.html reconstruido con {len(active_categories)} categorías")


# ── Main ───────────────────────────────────────────────────────────────────────
def fetch_categories():
    """Fetch categories from the second sheet tab. Falls back to CATEGORIES default."""
    print("📥 Descargando categorías desde Sheet...")
    resp = requests.get(SHEET_URL_CATEGORIES)
    if resp.status_code != 200:
        print("⚠️  No se pudo leer la pestaña Categorías, usando valores por defecto")
        return None

    # Load categories from sheet (or fall back to defaults)
    dynamic_cats = fetch_categories()
    active_categories = dynamic_cats if dynamic_cats else CATEGORIES

    import csv, io
    reader = csv.DictReader(io.StringIO(resp.text))
    cats = {}
    for row in reader:
        row = {k.strip().lower(): v.strip() for k, v in row.items()}
        slug = row.get("slug", "").lower().strip()
        title = row.get("titulo", "").strip()
        desc = row.get("descripcion", "").strip()
        if not slug or not title:
            continue
        cats[slug] = {
            "title": title,
            "desc": desc,
            "icon": CATEGORIES.get(slug, {}).get("icon", ""),
        }
    print(f"✅ {len(cats)} categorías cargadas desde Sheet")
    return cats if cats else None


def main():
    print("📥 Descargando Sheet...")
    resp = requests.get(SHEET_URL_ARTICLES)
    if resp.status_code != 200:
        print(f"❌ Error descargando Sheet: {resp.status_code}")
        sys.exit(1)

    # Load categories from sheet (or fall back to defaults)
    dynamic_cats = fetch_categories()
    active_categories = dynamic_cats if dynamic_cats else CATEGORIES

    import csv, io
    reader = csv.DictReader(io.StringIO(resp.text))

    # Normalize column names (strip spaces, lowercase)
    articles = []
    for row in reader:
        row = {k.strip().lower(): v.strip() for k, v in row.items()}
        if row.get("publicado", "").strip().upper() != "SI":
            continue
        cat = row.get("categoria", "").lower().strip()
        if cat not in CATEGORIES:
            print(f"⚠️  Categoría desconocida '{cat}', saltando fila")
            continue
        title = row.get("titulo", "").strip()
        if not title:
            continue
        row["slug"] = slugify(title)
        articles.append(row)

    print(f"✅ {len(articles)} artículos publicados encontrados")

    # Group by category then subcategory
    by_cat = {}
    for art in articles:
        cat = art["categoria"].lower().strip()
        subcat = art.get("subcategoria", "").strip()
        by_cat.setdefault(cat, {}).setdefault(subcat, []).append(art)

    # Limpiar artículos anteriores
    print("🧹 Limpiando artículos anteriores...")
    for cat_slug in active_categories:
        cat_dir = os.path.join(AYUDA_DIR, cat_slug)
        if not os.path.exists(cat_dir):
            continue
        new_slugs = set(["index.html"])
        if cat_slug in by_cat:
            for subcat_arts in by_cat[cat_slug].values():
                for art in subcat_arts:
                    new_slugs.add(art["slug"] + ".html")
        for fname in os.listdir(cat_dir):
            if fname.endswith(".html") and fname not in new_slugs:
                os.remove(os.path.join(cat_dir, fname))
                print(f"  🗑️  Eliminado: {cat_slug}/{fname}")
        if cat_slug not in by_cat:
            idx = os.path.join(cat_dir, "index.html")
            if os.path.exists(idx):
                os.remove(idx)
                print(f"  🗑️  Eliminado: {cat_slug}/index.html")

    # Generate files — always generate index for ALL categories
    for cat_slug, cat_info in active_categories.items():
        cat_dir = os.path.join(AYUDA_DIR, cat_slug)
        os.makedirs(cat_dir, exist_ok=True)
        wa_msg = WA_DEFAULTS.get(cat_slug, WA_DEFAULT)
        subcats = by_cat.get(cat_slug, {})

        # Write category index (even if empty)
        cat_html = build_category_index(cat_slug, cat_info, subcats, wa_msg)
        with open(os.path.join(cat_dir, "index.html"), "w") as f:
            f.write(cat_html)
        total = sum(len(v) for v in subcats.values())
        print(f"  📁 {cat_slug}/index.html ({total} artículos)")

        # Write each article
        for subcat, arts in subcats.items():
            for art in arts:
                art_html = build_article(art, cat_slug, cat_info["title"], wa_encode(art.get("wa_mensaje", "")))
                path = os.path.join(cat_dir, f"{art['slug']}.html")
                with open(path, "w") as f:
                    f.write(art_html)
                print(f"  📄 {cat_slug}/{art['slug']}.html")

    # Rebuild ayuda/index.html with current categories
    rebuild_ayuda_index(active_categories, by_cat)

    # Rebuild search index
    build_search_index(by_cat)
    print("✅ Build completo")

def build_search_index(by_cat):
    articles = []
    for cat_slug, subcats in by_cat.items():
        cat_title = CATEGORIES[cat_slug]["title"]
        for subcat, arts in subcats.items():
            for art in arts:
                body_html = markdown_to_html(art.get("contenido", ""))
                body_text = re.sub(r"<[^>]+>", " ", body_html)
                body_text = re.sub(r"\s+", " ", body_text).strip()
                articles.append({
                    "title": art["titulo"],
                    "cat": cat_title,
                    "cat_slug": cat_slug,
                    "url": f"{cat_slug}/{art['slug']}.html",
                    "text": (art["titulo"] + " " + body_text).lower()
                })
    import json
    js = "const SEARCH_INDEX = " + json.dumps(articles, ensure_ascii=False, indent=2) + ";\n"
    with open(os.path.join(AYUDA_DIR, "search-index.js"), "w") as f:
        f.write(js)
    print(f"  🔍 search-index.js ({len(articles)} artículos)")

if __name__ == "__main__":
    main()
