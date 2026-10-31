"""Genera los archivos cifrados de la galería (v2).

Uso:
  python3 build.py config.json personas.js anios.txt ../

config.json (NUNCA se sube al repositorio; vive con Claude/Mike) tiene:
  {"codigo": "...", "webhook": "https://hook...",
   "llaves": {"M": "<base64url 32 bytes>", "F": "<base64url 32 bytes>"},
   "fotos": [{"id": "<id de Notion>", "archivo": "/ruta/local.jpg", "linea": "Fuentes|Melgarejo|Ambas",
              "anio": 1975, "fecha": "", "lugar": "", "ocasion": "", "titulo": "",
              "caras": [{"n":1,"x":..,"y":..,"w":..,"h":..,"p":"<id persona>","nombre":"..","quien":".."}] o null,
              "pendientes": 3,
              "fid": "(se llena solo)", "llave": "(se llena solo)"}]}

Salida (en la carpeta galeria/ del repo):
  f/<fid>.bin  foto reducida (1600 px), sin metadatos, cifrada con su propia llave (AES-GCM)
  m.json       un índice por línea (M = Melgarejo, F = Fuentes), cada uno cifrado con la llave de su enlace.
               El índice de Melgarejo solo trae fotos Melgarejo/Ambas y el de Fuentes solo Fuentes/Ambas,
               así que con un enlace no se puede ni saber qué fotos tiene el otro lado.
anios.txt: "<id> <nacimiento|-> <fallecimiento|-> <generación|->" por línea.
"""
import base64, io, json, os, re, secrets, sys
from PIL import Image, ImageOps
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

LADO = 1600
CONTEMPORANEO = 1940  # a quien nació desde aquí no se le publica el año


def b64(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def unb64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def cifra(llave, datos):
    iv = secrets.token_bytes(12)
    return iv, AESGCM(llave).encrypt(iv, datos, None)


cfg_path, personas_js, anios_txt, salida = sys.argv[1:5]
cfg = json.load(open(cfg_path, encoding="utf-8"))
os.makedirs(os.path.join(salida, "f"), exist_ok=True)

# ---- Personas ----
txt = open(personas_js, encoding="utf-8").read()
lista = json.loads(txt[txt.index("= [") + 2: txt.rindex("]") + 1])
anios = {}
for l in open(anios_txt, encoding="utf-8"):
    p = l.split()
    if len(p) == 4:
        anios[p[0]] = [None if v == "-" else int(v) for v in p[1:]]
personas = []
for pid, nombre, alias, rama in lista:
    n, f, g = anios.get(pid, [None, None, None])
    c = 0
    if (n and n >= CONTEMPORANEO) or (n is None and g is not None and g <= 2):
        n, f, c = None, None, 1
    personas.append([pid, nombre, alias, rama, n, f, g, c])

# ---- Fotos ----
fotos = {"M": [], "F": []}
for foto in cfg["fotos"]:
    if not foto.get("fid"):
        foto["fid"] = secrets.token_hex(10)
        foto["llave"] = b64(secrets.token_bytes(32))
    destino = os.path.join(salida, "f", foto["fid"] + ".bin")
    llave = unb64(foto["llave"])
    if not os.path.exists(destino) or foto.get("regenerar"):
        im = ImageOps.exif_transpose(Image.open(foto["archivo"])).convert("RGB")
        im.thumbnail((LADO, LADO), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=85, optimize=True, progressive=True)  # sin EXIF
        iv, ct = cifra(llave, buf.getvalue())
        open(destino, "wb").write(iv + ct)
        foto["w"], foto["h"] = im.size
        foto.pop("regenerar", None)
    entrada = {k: foto.get(k) for k in ("id", "fid", "llave", "w", "h", "linea", "anio", "fecha", "lugar",
                                         "ocasion", "titulo", "caras", "pendientes")}
    if foto["linea"] in ("Melgarejo", "Ambas"):
        fotos["M"].append(entrada)
    if foto["linea"] in ("Fuentes", "Ambas"):
        fotos["F"].append(entrada)

# Las fotos que ya no están en config se borran del repo
vivas = {f["fid"] + ".bin" for f in cfg["fotos"]}
for arch in os.listdir(os.path.join(salida, "f")):
    if arch.endswith(".bin") and arch not in vivas:
        os.remove(os.path.join(salida, "f", arch))

indice = {"v": 2, "lineas": {}}
for linea, llave in cfg["llaves"].items():
    datos = {"linea": linea, "codigo": cfg["codigo"], "webhook": cfg["webhook"],
             "fotos": fotos[linea], "personas": personas}
    iv, ct = cifra(unb64(llave), json.dumps(datos, ensure_ascii=False, separators=(",", ":")).encode())
    indice["lineas"][linea] = {"iv": b64(iv), "ct": b64(ct)}
json.dump(indice, open(os.path.join(salida, "m.json"), "w"), separators=(",", ":"))
json.dump(cfg, open(cfg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("fotos M:", len(fotos["M"]), "F:", len(fotos["F"]), "personas:", len(personas))
