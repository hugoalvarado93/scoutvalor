"""
Reune las cifras del pipeline para la pagina de Metodologia (web/public/data/metodologia.json).

Toma: tamano de cada fuente, metricas de vinculacion (20), del modelo de valor (40),
del modelo de fichajes (60) y el resumen del portal (50). Se ejecuta al final del pipeline,
asi la pagina siempre describe la corrida mas reciente.
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[1]
MUESTRAS = os.getenv("MUESTRAS")
PROC = RAIZ / "data" / "procesado"
OUT = Path(os.getenv("SALIDA_PORTAL", RAIZ / "web" / "public" / "data"))


def leer_json(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def tamanos_transfermarkt():
    tablas = ["players", "player_valuations", "transfers", "appearances", "game_lineups", "games", "clubs", "competitions"]
    if MUESTRAS:
        return {t: int(len(pd.read_csv(Path(MUESTRAS) / f"tm_{t}.csv.gz", usecols=[0]))) for t in tablas
                if (Path(MUESTRAS) / f"tm_{t}.csv.gz").exists()}
    import duckdb
    con = duckdb.connect(str(RAIZ / "data/raw/transfermarkt/transfermarkt-datasets.duckdb"), read_only=True)
    return {t: int(con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]) for t in tablas}


def tamanos_api_football():
    out = {}
    for t in ["jugadores_temporada", "plantillas_actuales", "traspasos", "equipos", "ligas"]:
        if MUESTRAS:
            p = Path(MUESTRAS) / f"af_{t}.csv.gz"
            if p.exists():
                out[t] = int(len(pd.read_csv(p, usecols=[0])))
        else:
            p = RAIZ / f"data/api_football/parquet/{t}.parquet"
            if p.exists():
                out[t] = int(len(pd.read_parquet(p)))
    return out


def main():
    modelo_c = leer_json(OUT / "modelo_c.json") or {}
    coef = sorted(zip(modelo_c.get("feats", []), modelo_c.get("coef", [])), key=lambda x: x[1])
    datos = {
        "resumen": leer_json(OUT / "resumen.json"),
        "fuentes": {"transfermarkt": tamanos_transfermarkt(), "api_football": tamanos_api_football()},
        "vinculacion": leer_json(PROC / "metricas_vinculacion.json"),
        "valor": leer_json(PROC / "metricas_valor.json"),
        "fichajes": {k: modelo_c.get(k) for k in ["n", "tasa_base", "auc", "auc_gb", "brier", "brier_gb", "cal", "temporadas"]}
                    | {"coef": [[f, round(c, 3)] for f, c in coef]},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metodologia.json").write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({k: (v if k != "valor" else {kk: vv for kk, vv in (v or {}).items() if kk != "dispersion"})
                      for k, v in datos.items()}, ensure_ascii=False)[:2500])


if __name__ == "__main__":
    main()
