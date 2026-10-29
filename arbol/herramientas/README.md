# Árbol de la familia Fuentes Siller

`arbol/index.html` es el árbol que ve la familia. Funciona así:

- Empieza con Ricardo Fuentes Castilla y Delia Siller Pérez, y cada quien abre a los padres de la persona que quiera.
- Todos los datos van **cifrados** dentro de la página (AES-GCM con una clave derivada de la contraseña familiar). Sin la contraseña no se pueden leer, ni siquiera viendo el código.
- Los datos salen de Notion (Personal / Historia familiar): base **Personas** y base **Hallazgos**.

## Qué se muestra

- **Personas:** solo los dos abuelos y sus ancestros (relación Padres). Se muestran nombre, alias, años, fecha y lugar de nacimiento y fallecimiento (sin causa), ocupación, estado y fuentes. Las Notas no se muestran.
- **Hallazgos:** solo los que tienen Confianza «Confirmado» o «Probable» y no son de tipo «Contradicción». Se muestra el título y el campo **Texto para la familia**. El campo Detalle no se muestra.
- **Niveles hacia abajo** (hijos, nietos): todavía no. Se liberan con el último argumento de `build.py` cuando estén al día en Notion.

## Cómo actualizarlo

Pídeselo a Claude en el proyecto «Investigación Familiar». El proceso es:

1. Extraer de Notion un `datos.json` con esta forma:
   ```
   {"raices": ["<id Ricardo>", "<id Gudelia>"],
    "personas": {"<id>": {nombre, alias, sexo, estado, filiacion_por_confirmar, nacimiento, lugar_nacimiento,
                          anio_nacimiento, fallecimiento, lugar_fallecimiento, anio_fallecimiento, ocupacion,
                          padres: [ids], pareja: [ids], num_fotos, fuentes: [{titulo}], url}},
    "hallazgos": [{id, titulo, detalle, tipo, confianza, personas: [ids], fuente: [{titulo}], texto_familia}]}
   ```
   Raíces: Ricardo Fuentes Castilla `3e8ca309601981c99cbdf8d13ce07b73` y Gudelia Siller Pérez `3e8ca309601981d1ad15f38ba041bbf7`.
2. Ejecutar `python3 build.py datos.json plantilla.html ../index.html CONTRASEÑA` (requiere `pip install cryptography`).
3. Subir solo `arbol/index.html`. **Nunca subir `datos.json`**: contiene los datos sin cifrar.
