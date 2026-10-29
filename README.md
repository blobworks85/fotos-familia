# Fotos de la familia

Página para que la familia suba fotos y marque quién aparece en cada una.

- `index.html`: la página (detección de caras en el navegador con face-api).
- `personas.js`: nombres y alias de la base "Personas" de Notion, sin fechas ni notas.
- Al guardar, la foto y las etiquetas van a un escenario de Make que sube la foto a Drive ("05 - Fotografías familiares") y crea la entrada en la base "Fotografías" de Notion.

## Árbol familiar

- `arbol/index.html`: árbol de los Fuentes Siller, protegido con contraseña (los datos van cifrados).
- `arbol/herramientas/`: plantilla y script para volver a generarlo desde Notion (ver su README).
