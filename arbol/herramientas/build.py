"""Construye el árbol Fuentes Siller cifrado a partir de datos.json (extraído de Notion).
Uso: python3 build.py datos.json plantilla.html ../index.html CONTRASEÑA [niveles_abajo]
datos.json NO se sube al repositorio: contiene los datos sin cifrar.
"""
import base64, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

src, tpl, out, pw = sys.argv[1:5]
niveles_abajo = int(sys.argv[5]) if len(sys.argv) > 5 else 0
D = json.load(open(src, encoding="utf-8"))

MOSTRAR_CONFIANZA = {"Confirmado", "Probable"}
OCULTAR_TIPO = {"Contradicción"}
ALIAS_EXTRA = {}  # los alias viven en la propiedad Alias de Notion
# Hallazgos que son notas de proceso de la investigación, no historias para la familia
EXCLUIR_HALLAZGO = ("Se abre la rama materna", "Correspondencia con Euroroots", "Registrado en Notion",
                    "Los cuatro bisabuelos de la mamá", "Pista:")
# El detalle de los hallazgos está escrito como nota de investigación; por ahora solo se muestra el título
MOSTRAR_DETALLE = False
RENOMBRAR_FUENTE = [
    ("FamilySearch: registros de las líneas", "Actas parroquiales y del registro civil (Siller, Pérez Mata, Fuentes y Castilla)"),
    ("Correo de Euroroots", "Investigación genealógica de Euroroots (linaje Fuentes-Dávila-de la Garza-Treviño)"),
    ("Árbol de FamilySearch de ", "Árbol genealógico en línea de la familia"),
    ("Documentos y fotos subidas por ", "Documentos y fotos familiares"),
    ("Testimonio de ", "Testimonio familiar: los diez hijos de Ricardo y Delia"),
]


def fuente_familiar(t):
    for pre, nuevo in RENOMBRAR_FUENTE:
        if t.startswith(pre):
            return nuevo
    return t


def s(v):
    return "" if v is None else str(v).strip()


def corta(v, seps=",;("):
    v = s(v)
    idx = [v.find(c) for c in seps if v.find(c) > 0]
    return (v[: min(idx)] if idx else v).strip(" ,.")


def lugar(v):
    v = s(v)
    return v.split("(")[0].strip(" ,.") if v else ""


def anio(num, texto):
    if num not in (None, ""):
        try:
            return str(int(float(num)))
        except ValueError:
            pass
    m = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", s(texto))
    if not m:
        return ""
    pre = s(texto).lower()
    aprox = any(w in pre for w in ("c.", "ca.", "hacia", "circa", "aprox"))
    return ("c. " if aprox else "") + m.group(1)


personas = {}
for pid, p in D["personas"].items():
    nombre = s(p.get("nombre"))
    ocup = re.split(r"\(|, según", s(p.get("ocupacion")))[0].strip(" ,.")
    fuentes = []
    for f in p.get("fuentes") or []:
        t = s(f.get("titulo") if isinstance(f, dict) else f)
        t = fuente_familiar(t)
        if t and not re.fullmatch(r"[0-9a-f-]{32,36}", t) and t not in fuentes:
            fuentes.append(t)
    personas[pid] = {
        "n": nombre,
        "alias": s(p.get("alias")) or ALIAS_EXTRA.get(nombre, ""),
        "sexo": s(p.get("sexo")),
        "estado": s(p.get("estado")) or "Sin datos",
        "filiacion": bool(p.get("filiacion_por_confirmar")),
        "an": anio(p.get("anio_nacimiento"), p.get("nacimiento")),
        "af": anio(p.get("anio_fallecimiento"), p.get("fallecimiento")),
        "nac": corta(p.get("nacimiento")),
        "lnac": lugar(p.get("lugar_nacimiento")),
        "fall": corta(p.get("fallecimiento")),
        "lfall": lugar(p.get("lugar_fallecimiento")),
        "ocup": ocup,
        "padres": [x for x in (p.get("padres") or []) if x],
        "pareja": [x for x in (p.get("pareja") or []) if x],
        "fotos": int(p.get("num_fotos") or 0),
        "src": fuentes[:8],
        "url": s(p.get("url")),
        "h": [],
    }

for h in D.get("hallazgos", []):
    if s(h.get("confianza")) not in MOSTRAR_CONFIANZA or s(h.get("tipo")) in OCULTAR_TIPO:
        continue
    if s(h.get("titulo")).startswith(EXCLUIR_HALLAZGO):
        continue
    fuente = h.get("fuente") or []
    if isinstance(fuente, list):
        fuente = ", ".join(fuente_familiar(s(x.get("titulo") if isinstance(x, dict) else x)) for x in fuente
                           if not re.fullmatch(r"[0-9a-f-]{32,36}", s(x.get("titulo") if isinstance(x, dict) else x)))
    item = {"t": s(h.get("tipo")) or "Dato", "h": s(h.get("titulo")), "d": s(h.get("texto_familia")) or (s(h.get("detalle")) if MOSTRAR_DETALLE else ""),
            "c": s(h.get("confianza")), "f": s(fuente)}
    for pid in h.get("personas") or []:
        if pid in personas:
            personas[pid]["h"].append(item)

etiquetas = ["Ricardo y Delia", "Sus padres", "Sus abuelos", "Sus bisabuelos", "Sus tatarabuelos"] + \
            [f"Sus {i}.º abuelos" for i in range(5, 15)]
data = {
    "titulo": "Familia Fuentes Siller",
    "raices": D["raices"],
    "personas": personas,
    "etiquetas": etiquetas,
    "niveles_abajo": niveles_abajo,
    "nota_abajo": "Sus diez hijos y el resto de la familia se agregarán más adelante.",
}

salt, iv, it = os.urandom(16), os.urandom(12), 310000
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, json.dumps(data, ensure_ascii=False).encode(), None)
payload = {k: base64.b64encode(v).decode() for k, v in (("salt", salt), ("iv", iv), ("ct", ct))}
payload["iter"] = it
html = open(tpl, encoding="utf-8").read().replace("__PAYLOAD__", json.dumps(payload))
open(out, "w", encoding="utf-8").write(html)
print(f"{len(personas)} personas, {sum(len(p['h']) for p in personas.values())} historias visibles -> {out}")
