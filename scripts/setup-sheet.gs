/**
 * INSTRUCCIONES:
 * 1. En el Sheet ve a Extensiones → Apps Script
 * 2. Borra todo lo que haya y pega este código
 * 3. Clic en Guardar (disquete)
 * 4. Clic en Ejecutar ▶ (selecciona "configurarSheet")
 * 5. Acepta los permisos que pide
 */

function configurarSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.setName("Artículos");

  // ── Encabezados ──────────────────────────────────────────────
  const headers = [
    "categoria", "subcategoria", "titulo",
    "subtitulo", "contenido", "wa_mensaje", "publicado"
  ];
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setValues([headers]);
  headerRange.setBackground("#0F1F3D");
  headerRange.setFontColor("#FFFFFF");
  headerRange.setFontWeight("bold");
  headerRange.setFontSize(11);
  sheet.setFrozenRows(1);

  // ── Anchos de columna ────────────────────────────────────────
  sheet.setColumnWidth(1, 130);  // categoria
  sheet.setColumnWidth(2, 180);  // subcategoria
  sheet.setColumnWidth(3, 320);  // titulo
  sheet.setColumnWidth(4, 260);  // subtitulo
  sheet.setColumnWidth(5, 520);  // contenido
  sheet.setColumnWidth(6, 320);  // wa_mensaje
  sheet.setColumnWidth(7, 110);  // publicado

  // ── Desplegable: categoría (columna A) ───────────────────────
  const catValues = [
    "deudas",
    "contratos",
    "laboral",
    "propiedades",
    "migratorio",
    "civil"
  ];
  const catRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(catValues, true)
    .setAllowInvalid(false)
    .setHelpText("Elige una categoría de la lista")
    .build();
  sheet.getRange("A2:A1000").setDataValidation(catRule);

  // ── Desplegable: publicado (columna G) ───────────────────────
  const pubRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["SI", "NO"], true)
    .setAllowInvalid(false)
    .setHelpText("SI = publicado, NO = borrador")
    .build();
  sheet.getRange("G2:G1000").setDataValidation(pubRule);

  // ── Fila de ejemplo ──────────────────────────────────────────
  const ejemplo = [
    "deudas",
    "Juicios ejecutivos",
    "¿Qué es un juicio ejecutivo?",
    "El juicio ejecutivo es un procedimiento judicial de cobro.",
    "## ¿En qué consiste?\n\nEl juicio ejecutivo es un procedimiento que permite cobrar una deuda documentada ante un tribunal.\n\n## ¿Cuándo aplica?\n\nSe usa cuando existe un título ejecutivo, como un pagaré, letra de cambio o cheque protestado.\n\n## Pasos generales\n\n- El acreedor presenta la demanda ante el tribunal\n- El tribunal notifica al deudor\n- El deudor tiene un plazo para oponer excepciones\n- Si no hay excepciones o son rechazadas, se puede embargar",
    "Hola, quisiera realizar una consulta sobre deudas, cobranzas o juicio ejecutivo.",
    "SI"
  ];
  sheet.getRange(2, 1, 1, ejemplo.length).setValues([ejemplo]);

  // ── Formato de la columna contenido: wrap de texto ───────────
  sheet.getRange("E2:E1000").setWrap(true);
  sheet.setRowHeight(2, 160);

  SpreadsheetApp.getUi().alert(
    "✅ Sheet configurado correctamente.\n\n" +
    "• Columna A: desplegable con categorías\n" +
    "• Columna G: desplegable SI / NO\n" +
    "• Fila 2: artículo de ejemplo\n\n" +
    "Agrega nuevos artículos desde la fila 3."
  );
}
