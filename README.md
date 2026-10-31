# Fotos de la familia

Páginas para que la familia identifique quién aparece en las fotos.

- `index.html`: galería para identificar caras en fotos ya guardadas (fotos cifradas; ver `galeria/herramientas/README.md`).
- `subir.html`: subir una foto nueva y marcar quién aparece (detección de caras en el navegador con face-api).
- `personas.js`: nombres y alias de la base "Personas" de Notion, sin fechas ni notas.
- Al guardar, la foto y las etiquetas van a un escenario de Make que sube la foto a Drive ("05 - Fotografías familiares") y crea la entrada en la base "Fotografías" de Notion.

## Árbol familiar

- `arbol/index.html`: árbol de los Fuentes Siller, protegido con contraseña (los datos van cifrados).
- `arbol/herramientas/`: plantilla y script para volver a generarlo desde Notion (ver su README).
