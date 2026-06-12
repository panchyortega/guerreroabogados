# Guerrero Abogados — Sitio Web

Sitio web de Guerrero Abogados. El sitio principal está en HTML/CSS/JS vanilla. El Centro de Ayuda se gestiona desde Google Sheets — sin tocar código.

**Sitio en producción:** https://panchyortega.github.io/guerreroabogadosweb/
**Google Sheet (Centro de Ayuda):** https://docs.google.com/spreadsheets/d/1qsPSjlMgp7o_qV_vTWHg2vTHLeWnUIzaoo23P_eaDoc/edit

---

## Para quien no cacha de código: actualizar el Centro de Ayuda

Todo el contenido del Centro de Ayuda (artículos, categorías) se edita desde Google Sheets. No hay que tocar ningún archivo del sitio.

### Paso 1 — Pedir acceso al Sheet

Solicitar acceso a la administradora del sitio. El Sheet tiene dos pestañas: **Categorías** y **Artículos**.

### Paso 2 — Editar el Sheet

**Pestaña "Categorías"** — controla las categorías que aparecen en el Centro de Ayuda:

| Columna | Qué es | Se puede cambiar? |
|---------|--------|-------------------|
| `slug` | Identificador interno (ej: `deudas`) | ⛔ Nunca. Si se cambia, los artículos vinculados dejan de funcionar. |
| `titulo` | Nombre que se ve en el sitio | ✅ Sí |
| `descripcion` | Texto bajo el título en las cards | ✅ Sí |

Para agregar una categoría nueva: agrega una fila nueva con un slug en **minúsculas, sin espacios, sin tildes, sin mayúsculas** (ej: `familia`, `penal`, `consumidor`). Luego agrega artículos con ese slug en la pestaña Artículos.

---

**Pestaña "Artículos"** — cada fila es un artículo:

| Columna | Qué es |
|---------|--------|
| `categoria` | Slug de la categoría (desplegable). Debe ser exactamente igual al slug de la pestaña Categorías. |
| `subcategoria` | Agrupador dentro de la categoría. Opcional. Ej: `Juicios ejecutivos` |
| `titulo` | Título del artículo. Ej: `¿Qué es un juicio ejecutivo?` |
| `subtitulo` | Bajada corta bajo el título. Opcional. |
| `contenido` | Cuerpo del artículo (ver formato más abajo). |
| `wa_mensaje` | Mensaje prellenado de WhatsApp al final del artículo. Si se deja vacío usa el de la categoría. |
| `publicado` | `SI` para publicar. `NO` o vacío = borrador (no aparece en el sitio). |

**Formato del contenido:**

El texto del artículo se escribe en la celda de `contenido` así:

```
## Este es un subtítulo

Este es un párrafo normal. Se puede escribir con libertad.

## Otro subtítulo

Otro párrafo.

- Item de lista
- Otro item
- Un item más
```

Reglas simples:
- `##` al inicio → subtítulo
- `-` al inicio → ítem de lista
- Cualquier otra línea → párrafo normal

### Paso 3 — Publicar los cambios

Después de editar el Sheet, los cambios **no aparecen solos**. Hay que ir a GitHub y publicar manualmente:

1. Ir a **github.com/panchyortega/guerreroabogadosweb/actions**
2. En el menú izquierdo, clic en **"Publicar artículos desde Google Sheet"**
3. Clic en el botón **"Run workflow"** (lado derecho)
4. Clic en el botón verde **"Run workflow"**
5. Esperar ~1 minuto
6. El sitio se actualiza solo

Si el workflow sale con ✅ verde, los cambios están publicados. Si sale ❌ rojo, algo salió mal — avisar a quien mantiene el sitio.

---

## ⛔ Qué NO tocar nunca

- **Los archivos HTML dentro de `/ayuda/`** — se sobreescriben automáticamente en cada publicación. Cualquier cambio manual se pierde.
- **`ayuda/search-index.js`** — generado automáticamente. No editar.
- **Los slugs de la pestaña Categorías** — si se cambian, los artículos asociados dejan de funcionar.
- **Los secrets del repo** — `GH_TOKEN` y `SHEET_ID` en GitHub → Settings → Secrets. No tocar.

---

## Para diseñadores: cambios visuales

### Tipografías
- **DM Serif Display** — solo para títulos grandes (H1 de artículos, títulos de sección ≥1.5rem)
- **Inter** — todo lo demás: cuerpo, botones, labels, navegación

Importadas desde Google Fonts, declaradas en el `<head>` de cada HTML.

### Archivos de estilos
- `styles.css` — estilos del sitio principal (home, servicios, contacto, FAQ, footer)
- `ayuda/ayuda.css` — estilos del Centro de Ayuda (hero, cards de categorías, artículos, buscador)

Son archivos separados. Un cambio en `styles.css` no afecta el Centro de Ayuda y viceversa.

### Variables de color
Al inicio de `styles.css` y `ayuda/ayuda.css`:

```css
:root {
  --navy:        #0F1F3D;  /* Azul marino — fondos oscuros, títulos */
  --navy-mid:    #1A3560;  /* Azul medio — sección contacto */
  --blue:        #2E5FAC;  /* Azul activo — links, íconos, acentos */
  --blue-light:  #8EA8C3;  /* Azul grisáceo — textos secundarios */
  --off-white:   #F5F3EE;  /* Beige cálido — fondos de secciones claras */
  --warm-grey:   #E8E5DF;  /* Gris cálido — bordes */
  --text-dark:   #1C1C1C;  /* Texto principal */
  --text-muted:  #6B7280;  /* Texto secundario */
  --green-wa:    #25D366;  /* Verde WhatsApp */
}
```

### Número de WhatsApp
Busca y reemplaza `56983937954` en `index.html` (aparece varias veces). En los archivos de `/ayuda/` está hardcodeado en `scripts/build_articles.py` — variable `WA_NUMBER` al inicio del archivo.

---

## Para desarrolladores

### Stack
- HTML/CSS/JS vanilla — sin frameworks, sin build step para el sitio principal
- GitHub Pages — deploy automático en cada push a `main`
- Python 3.11 — script de build del Centro de Ayuda (`scripts/build_articles.py`)
- GitHub Actions — corre el script manualmente o en cada push

### Cómo funciona el build del Centro de Ayuda

1. El workflow (`build-articles.yml`) corre `build_articles.py`
2. El script descarga las dos pestañas del Sheet como CSV (URLs hardcodeadas en el script)
3. Lee la pestaña **Categorías** → construye el diccionario `active_categories`
4. Lee la pestaña **Artículos** → filtra los que tienen `publicado = SI`
5. Para cada categoría: genera `ayuda/{slug}/index.html` con la lista de artículos
6. Para cada artículo: convierte el contenido Markdown a HTML y genera `ayuda/{slug}/{titulo-slugificado}.html`
7. Borra los HTMLs que ya no están en el Sheet
8. Reconstruye `ayuda/index.html` con las cards de categorías actualizadas
9. Reconstruye `ayuda/search-index.js` con todos los artículos indexados
10. Hace commit y push de los cambios al repo
11. GitHub Pages detecta el push y publica el sitio

### Agregar un campo nuevo al Sheet

1. Agregar la columna en el Sheet (pestaña Artículos)
2. En `build_articles.py`, leer el campo con `art.get("nombre_columna", "")` en la función `build_article()`
3. Usarlo en el template HTML dentro de la misma función

### URLs del Sheet (CSV publicado)

```python
SHEET_URL_ARTICLES   = "https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?gid=0&single=true&output=csv"
SHEET_URL_CATEGORIES = "https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?gid=1831731050&single=true&output=csv"
```

Si se crea un Sheet nuevo, hay que publicarlo en **Archivo → Compartir → Publicar en la web → CSV** y actualizar estas URLs en el script.

### Correr localmente

```bash
# Sitio principal
python3 -m http.server 3000
# Abre http://localhost:3000

# Probar el script de build (requiere que el Sheet esté publicado)
pip install requests
python3 scripts/build_articles.py
```

### Deploy

```bash
git add .
git commit -m "descripción del cambio"
git push
```

GitHub Pages publica automáticamente en 1-2 minutos.

---

## Mantenimiento del token GitHub

El workflow usa un Personal Access Token guardado como secret `GH_TOKEN`. **Expira en junio 2027.**

Cuando expire, el workflow fallará con un error de autenticación. Para renovarlo:

1. Ir a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generar nuevo token con scopes: `repo` + `workflow`, expiración 1 año
3. Ir al repo → Settings → Secrets and variables → Actions → `GH_TOKEN` → Update
4. Pegar el nuevo token

El `SHEET_ID` también está guardado como secret pero no expira.
