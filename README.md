# Guerrero Abogados — Sitio Web

Sitio web estático para Guerrero Abogados, construido con HTML, CSS y JavaScript vanilla. Sin dependencias, sin build step, listo para publicar en GitHub Pages.

---

## Estructura de archivos

```
guerreroabogados/
├── index.html    # Página principal (una sola página con anclas)
├── styles.css    # Todos los estilos
├── main.js       # Interacciones (menú, FAQ, scroll reveal, parallax)
└── README.md     # Este archivo
```

---

## Correr localmente

No requiere ningún servidor ni instalación. Solo abre `index.html` en el navegador.

**Opción 1 — Doble clic:**
Abre `index.html` directamente desde el explorador de archivos.

**Opción 2 — Con Live Server (VS Code):**
1. Instala la extensión "Live Server" en VS Code.
2. Abre la carpeta del proyecto.
3. Click derecho sobre `index.html` → "Open with Live Server".

**Opción 3 — Con Python:**
```bash
cd guerreroabogados
python3 -m http.server 3000
# Abre http://localhost:3000
```

---

## Publicar en GitHub Pages

### Primer deploy

1. **Sube los archivos al repo:**
   ```bash
   git init
   git add .
   git commit -m "feat: sitio web inicial Guerrero Abogados"
   git branch -M main
   git remote add origin https://github.com/panchyortega/guerreroabogados.git
   git push -u origin main
   ```

2. **Activa GitHub Pages:**
   - Ve al repo en GitHub → Settings → Pages
   - En "Source" selecciona: **Deploy from a branch**
   - Branch: `main` / Folder: `/ (root)`
   - Haz clic en **Save**

3. **El sitio estará disponible en:**
   ```
   https://panchyortega.github.io/guerreroabogados/
   ```
   (puede tardar 1–2 minutos en aparecer la primera vez)

### Actualizar el sitio

```bash
git add .
git commit -m "fix: descripción del cambio"
git push
```
GitHub Pages se actualiza automáticamente en unos minutos.

---

## Ediciones frecuentes

### Cambiar número de WhatsApp
Busca `56983937954` en `index.html` y reemplaza por el nuevo número (sin espacios, sin guiones, sin +).

### Cambiar textos
Edita directamente en `index.html`. Los textos están en su lugar semántico (H1, H2, párrafos, listas).

### Cambiar colores
En `styles.css`, modifica las variables al inicio del archivo:
```css
:root {
  --navy:       #0F1F3D;
  --blue:       #2E5FAC;
  --off-white:  #F5F3EE;
  /* ... */
}
```

### Agregar/quitar servicios
Cada servicio es un `<article class="service-card">` en la sección `#servicios`. Copia uno existente y modifica el contenido.

---

## SEO implementado

- Meta title y description
- Open Graph básico
- HTML semántico (H1 único, H2 por sección, H3 por servicio)
- JSON-LD para LegalService y FAQPage
- Alt texts en imágenes/SVG
- Anclas descriptivas
- Chips de búsqueda para SEO local

---

## Notas

- No usa frameworks ni dependencias externas (solo Google Fonts).
- Es fully responsive (mobile, tablet, desktop).
- Cumple accesibilidad básica: contraste, focus, aria, reduced-motion.
- Los links de WhatsApp usan el formato `https://wa.me/56983937954?text=MENSAJE` con texto pre-codificado.
