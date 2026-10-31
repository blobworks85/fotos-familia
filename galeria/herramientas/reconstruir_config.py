"""Reconstruye config.json a partir de galeria/m.json y las dos llaves de línea.
Uso: python3 reconstruir_config.py ../m.json LLAVE_M LLAVE_F config.json
Las llaves están en la página privada de Notion «Galería — enlaces y llaves (privado)».
Las fotos ya publicadas no necesitan «archivo» (su .bin ya existe); las nuevas sí.
"""
import base64, json, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def unb64(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

ind = json.load(open(sys.argv[1]))
llaves = {"M": sys.argv[2], "F": sys.argv[3]}
fotos, cfg = {}, {"llaves": llaves}
for l, k in llaves.items():
    e = ind["lineas"][l]
    d = json.loads(AESGCM(unb64(k)).decrypt(unb64(e["iv"]), unb64(e["ct"]), None))
    cfg["codigo"], cfg["webhook"] = d["codigo"], d["webhook"]
    for f in d["fotos"]:
        fotos.setdefault(f["id"], dict(f, archivo=""))
cfg["fotos"] = list(fotos.values())
json.dump(cfg, open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
print(len(cfg["fotos"]), "fotos")
