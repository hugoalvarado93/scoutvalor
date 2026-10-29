"""Resume lo descargado de API-Football en data/reports/api_football.md (sin datos personales)."""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[1]
PQ = RAIZ / "data" / "api_football" / "parquet"
out = ["# Resumen API-Football\n"]

ligas = PQ / "ligas.parquet"
if ligas.exists():
    df = pd.read_parquet(ligas)
    out.append("## Ligas verificadas\n")
    res = (df[df.temporada >= 2022]
           .assign(t=lambda d: d.temporada.astype(str) + d.actual.map({True: "*", False: ""}).fillna(""))
           .groupby(["tm_liga", "api_liga", "nombre", "pais", "pais_ok"])
           .agg(temporadas=("t", lambda s: " ".join(sorted(s))),
                stats_jugador=("cov_stats_jugador", "sum"))
           .reset_index())
    out.append(res.to_markdown(index=False))
    out.append("\n`*` = temporada actual\n")

out.append("## Tablas descargadas\n")
filas = []
for f in sorted(PQ.glob("*.parquet")):
    df = pd.read_parquet(f)
    filas.append({"tabla": f.stem, "filas": len(df), "columnas": len(df.columns)})
out.append(pd.DataFrame(filas).to_markdown(index=False) if filas else "_(nada aun)_")

jt = PQ / "jugadores_temporada.parquet"
if jt.exists():
    df = pd.read_parquet(jt)
    out.append("\n## Jugadores por liga y temporada\n")
    out.append(df.pivot_table(index="api_liga", columns="temporada", values="api_jugador",
                              aggfunc="nunique").reset_index().to_markdown(index=False))
    out.append("\n## Completitud de estadisticas (% no nulo, jugadores con minutos)\n")
    m = df[df.minutos.fillna(0) > 0]
    cols = ["calificacion", "tiros", "pases", "pases_clave", "precision_pase", "entradas",
            "intercepciones", "duelos", "regates_intentos", "faltas_recibidas"]
    out.append((m[cols].notna().mean() * 100).round(1).rename("pct").reset_index()
               .rename(columns={"index": "estadistica"}).to_markdown(index=False))

dest = RAIZ / "data" / "reports" / "api_football.md"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text("\n".join(out), encoding="utf-8")
print("\n".join(out)[:3000])
