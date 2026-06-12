/**
 * INSTRUCCIONES:
 * 1. En el Sheet ve a Extensiones → Apps Script
 * 2. Borra todo lo que haya y pega este código completo
 * 3. Clic en Guardar (disquete)
 * 4. Ejecutar → configurarTodo
 * 5. Acepta los permisos que pide
 */

// ── Configuración ──────────────────────────────────────────────
const SLUGS_FIJOS = ["deudas", "contratos", "laboral", "propiedades", "migratorio", "civil"];

// ── Setup completo ─────────────────────────────────────────────
function configurarTodo() {
  configurarSheetCategorias();
  configurarSheetArticulos();
  SpreadsheetApp.getUi().alert(
    "✅ Listo.\n\n" +
    "Se crearon dos pestañas:\n" +
    "• Categorías → edita títulos y descripciones\n" +
    "• Artículos → agrega artículos nuevos\n\n" +
    "El desplegable de 'categoria' en Artículos\n" +
    "se actualiza automáticamente desde Categorías."
  );
}

// ── Pestaña Categorías ─────────────────────────────────────────
function configurarSheetCategorias() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName("Categorías");
  if (!sheet) sheet = ss.insertSheet("Categorías", 0);
  sheet.clear();

  // Encabezados
  const headers = ["slug", "titulo", "descripcion"];
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setValues([headers]);
  headerRange.setBackground("#0F1F3D");
  headerRange.setFontColor("#FFFFFF");
  headerRange.setFontWeight("bold");
  sheet.setFrozenRows(1);
  sheet.setColumnWidth(1, 130);
  sheet.setColumnWidth(2, 220);
  sheet.setColumnWidth(3, 480);

  // Slug no editable (solo referencia)
  const slugNote = sheet.getRange("A1");
  slugNote.setNote("No cambies el slug — es el identificador interno. Solo edita título y descripción.");

  // Datos iniciales
  const rows = [
    ["deudas",      "Deudas, cobranzas y juicios ejecutivos", "Preguntas sobre demandas de cobro, embargos, prescripción de deudas y defensa en juicio ejecutivo."],
    ["contratos",   "Contratos y negocios",                   "Orientación sobre contratos, acuerdos y asesoría legal para emprendedores y empresas."],
    ["laboral",     "Derecho laboral",                        "Preguntas sobre despidos, finiquitos, contratos de trabajo y conflictos laborales."],
    ["propiedades", "Propiedades y vivienda",                 "Orientación sobre regularización de propiedades, compraventas, arriendos y antecedentes de inmuebles."],
    ["migratorio",  "Derecho migratorio",                     "Preguntas sobre trámites migratorios, regularización y solicitudes en Chile."],
    ["civil",       "Derecho civil general",                  "Orientación sobre conflictos entre particulares, contratos, obligaciones y responsabilidad civil."],
  ];
  sheet.getRange(2, 1, rows.length, 3).setValues(rows);

  // Columna slug: fondo gris (solo lectura visual)
  sheet.getRange("A2:A1000").setBackground("#F3F3F3").setFontColor("#888888");
  sheet.getRange("C2:C1000").setWrap(true);
}

// ── Pestaña Artículos ──────────────────────────────────────────
function configurarSheetArticulos() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName("Artículos");
  if (!sheet) sheet = ss.insertSheet("Artículos", 1);

  // Encabezados solo si la hoja está vacía
  if (sheet.getLastRow() === 0) {
    const headers = ["categoria", "subcategoria", "titulo", "subtitulo", "contenido", "wa_mensaje", "publicado"];
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setValues([headers]);
    headerRange.setBackground("#0F1F3D");
    headerRange.setFontColor("#FFFFFF");
    headerRange.setFontWeight("bold");
    sheet.setFrozenRows(1);
    sheet.setColumnWidth(1, 130);
    sheet.setColumnWidth(2, 180);
    sheet.setColumnWidth(3, 320);
    sheet.setColumnWidth(4, 260);
    sheet.setColumnWidth(5, 520);
    sheet.setColumnWidth(6, 320);
    sheet.setColumnWidth(7, 110);
  }

  // Actualizar desplegable de categorías desde la pestaña Categorías
  actualizarDesplegableCategorias();

  // Desplegable publicado
  const pubRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["SI", "NO"], true)
    .setAllowInvalid(false)
    .setHelpText("SI = publicado, NO = borrador")
    .build();
  sheet.getRange("G2:G1000").setDataValidation(pubRule);

  sheet.getRange("E2:E1000").setWrap(true);
}

// ── Actualizar desplegable de categorías ───────────────────────
function actualizarDesplegableCategorias() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const catSheet = ss.getSheetByName("Categorías");
  const artSheet = ss.getSheetByName("Artículos");
  if (!catSheet || !artSheet) return;

  // Leer slugs desde la pestaña Categorías
  const lastRow = catSheet.getLastRow();
  if (lastRow < 2) return;
  const slugs = catSheet.getRange(2, 1, lastRow - 1, 1).getValues()
    .map(r => r[0].toString().trim())
    .filter(s => s.length > 0);

  if (slugs.length === 0) return;

  const catRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(slugs, true)
    .setAllowInvalid(false)
    .setHelpText("Elige una categoría. Para agregar nuevas, edita la pestaña Categorías.")
    .build();
  artSheet.getRange("A2:A1000").setDataValidation(catRule);
}

// ── Trigger: se ejecuta cuando editas la pestaña Categorías ───
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() === "Categorías") {
    actualizarDesplegableCategorias();
  }
}
