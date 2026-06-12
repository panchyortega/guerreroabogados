# Guerrero Abogados — Sitio Web

Sitio web estático para Guerrero Abogados, construido con HTML, CSS y JavaScript vanilla. El Centro de Ayuda se gestiona desde Google Sheets.

---

## Estructura de archivos

```
guerreroabogadosweb/
├── index.html              # Página principal
├── styles.css              # Estilos del sitio principal
├── main.js                 # JS del sitio principal
├── ayuda/                  # Centro de Ayuda (generado automáticamente)
│   ├── index.html          # Página principal del Centro de Ayuda
│   ├── ayuda.css           # Estilos del Centro de Ayuda
│   ├── ayuda.js            # JS del Centro de Ayuda
│   ├── search-index.js     # Índice de búsqueda (generado automáticamente)
│   ├── deudas/             # Categoría: Deudas
│   ├── contratos/          # Categoría: Contratos
│   ├── laboral/            # Categoría: Derecho laboral
│   ├── propiedades/        # Categoría: Propiedades
│   ├── migratorio/         # Categoría: Derecho migratorio
│   ├── civil/              # Categoría: Derecho civil
│   └── [otras categorías]/ # Categorías creadas desde el Sheet
├── scripts/
│   ├── build_articles.py   # Script que lee el Sheet y genera el HTML
│   └── setup-sheet.gs      # Script de configuración del Google Sheet
└── .github/
    └── workflows/
        └── build-articles.yml  # GitHub Action para publicar artículos
```

---

## Sitio en producción

**https://panchyortega.github.io/guerreroabogadosweb/**

---

## Cómo actualizar el Centro de Ayuda

El contenido del Centro de Ayuda se gestiona desde Google Sheets. No es necesario tocar código.

### Google Sheet
**https://docs.google.com/spreadsheets/d/1qsPSjlMgp7o_qV_vTWHg2vTHLeWnUIzaoo23P_eaDoc/edit**

> Para acceder a editar el Sheet, solicitar acceso a la administradora del sitio.

---

### Pestaña "Categorías"

Controla las categorías que aparecen en el Centro de Ayuda.

| Columna | Descripción |
|---------|-------------|
| `slug` | Identificador interno. **No cambiar nunca.** Es lo que vincula los artículos a la categoría. |
| `titulo` | Nombre que se muestra en el sitio. Se puede editar libremente. |
| `descripcion` | Descripción breve que aparece bajo el título en las cards. |

**Para agregar una categoría nueva:** agrega una fila con un slug en minúsculas sin espacios (ej: `familia`), un título y una descripción.

---

### Pestaña "Artículos"

Cada fila es un artículo del Centro de Ayuda.

| Columna | Descripción |
|---------|-------------|
| `categoria` | Slug de la categoría (desplegable). Debe coincidir con un slug de la pestaña Categorías. |
| `subcategoria` | Subtítulo agrupador dentro de la categoría. Opcional. Ej: `"Juicios ejecutivos"` |
| `titulo` | Título del artículo. Ej: `¿Qué es un juicio ejecutivo?` |
| `subtitulo` | Bajada corta bajo el título. Opcional. |
| `contenido` | Cuerpo del artículo en Markdown (ver formato abajo). |
| `wa_mensaje` | Mensaje prellenado de WhatsApp. Si se deja vacío usa el de la categoría. |
| `publicado` | `SI` para publicar, `NO` o vacío para borrador. |

---

### Formato del contenido (Markdown)

El contenido se escribe en la celda E con este formato simple:

```
## Primer subtítulo

Un párrafo normal de texto.

## Segundo subtítulo

Otro párrafo.

- Item de lista
- Otro item
- Un item más
```

- `##` al inicio de una línea → subtítulo
- `-` al inicio de una línea → ítem de lista
- Líneas normales → párrafos

---

### Publicar los cambios

Después de editar el Sheet, hay que publicar manualmente:

1. Ir a **github.com/panchyortega/guerreroabogadosweb/actions**
2. Clic en **"Publicar artículos desde Google Sheet"** (menú izquierdo)
3. Clic en **"Run workflow"** → **"Run workflow"** (botón verde)
4. Esperar ~30 segundos
5. El sitio se actualiza en 1-2 minutos

---

## Correr localmente

No requiere instalación. Abre `index.html` directamente en el browser.

O con Python:
```bash
python3 -m http.server 3000
# Abre http://localhost:3000
```

---

## Cambios de código

### Colores
En `styles.css`, variables al inicio del archivo:
```css
:root {
  --navy:      #0F1F3D;
  --blue:      #2E5FAC;
  --off-white: #F5F3EE;
}
```

### Número de WhatsApp
Busca `56983937954` en `index.html` y reemplaza.

### Publicar cambios de código
```bash
git add .
git commit -m "descripción del cambio"
git push
```
GitHub Pages se actualiza en 1-2 minutos.

---

## Token de acceso GitHub

El workflow usa un token guardado como secret en el repo (`GH_TOKEN`). Expira en junio 2027. Cuando expire:

1. Generar nuevo token en GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Scopes: `repo` + `workflow`
3. Expiración: 1 año
4. Ir al repo → Settings → Secrets and variables → Actions → `GH_TOKEN` → Update
