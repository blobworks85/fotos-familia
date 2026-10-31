# Galería para identificar caras (v2)

- `index.html` (raíz): la galería. Se abre con un enlace que trae la llave en la parte después de `#`
  (`#m=…` Melgarejo, `#f=…` Fuentes, ambas = vista completa de Mike). Esa parte nunca sale del navegador.
- `galeria/m.json`: un índice cifrado por línea. Con la llave de Melgarejo solo se abren fotos Melgarejo/Ambas;
  con la de Fuentes, solo Fuentes/Ambas.
- `galeria/f/*.bin`: cada foto reducida a 1600 px, sin metadatos, cifrada con su propia llave (AES-GCM).
- `subir.html`: la página anterior para subir una foto nueva (pestaña «Subir una foto»).
- Lo que identifica alguien se manda a Make (escenario «Galería v2 — guardar aportación») y queda como fila en la
  base de Notion «Aportaciones de la galería». Claude las integra a Fotografías y Personas.

## Regenerar

Pídeselo a Claude en el proyecto «Investigación Familiar». `build.py` necesita un `config.json` con las llaves,
el código del webhook y la lista de fotos (ver el encabezado de `build.py`). **Nunca subir `config.json`.**
Las llaves de línea están en la página privada de Notion «Galería — enlaces y llaves»; con ellas se puede
reconstruir `config.json` descifrando `m.json`.
