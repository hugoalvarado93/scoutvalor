"""
Genera muestras reducidas para desarrollo local (rama `muestras`).

Contenido (parquet comprimido):
  tm_*            Transfermarkt completo para jugadores/clubes/ligas; historial filtrado a ligas muestra
  af_*            API-Football (si existe) filtrado a ligas muestra

Ligas muestra: MEX1, ARG1, GB1, PO1 (cubren Latinoamerica, Europa top y una liga vendedora).
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[1]
TM = RAIZ / "data" / "raw" / "transfermarkt" / "transfermarkt-datasets.duckdb"
AF = RAIZ / "data" / "api_football" / "parquet"
OUT = RAIZ / "muestras"
OUT.mkdir(exist_ok=True)

LIGAS_TM = ("MEX1", "ARG1", "GB1", "PO1")
LIGAS_AF = (262, 128, 39, 94)


def escribir(nombre: str, df: pd.DataFrame):
    p = OUT / f"{nombre}.parquet"
    df.to_parquet(p, index=False, compression="zstd")
    print(f"{nombre}: {len(df):,} filas, {p.stat().st_size/1e6:.1f} MB")


con = duckdb.connect(str(TM), read_only=True)
lig = ",".join(f"'{x}'" for x in LIGAS_TM)
# tablas pequenas completas: necesarias para vincular contra cualquier liga
for t in ("competitions", "countries", "clubs", "national_teams", "players"):
    escribir(f"tm_{t}", con.execute(f"SELECT * FROM {t}").df())
# historial filtrado
escribir("tm_games", con.execute(f"SELECT * FROM games WHERE competition_id IN ({lig})").df())
escribir("tm_appearances", con.execute(f"SELECT * FROM appearances WHERE competition_id IN ({lig})").df())
escribir("tm_game_lineups", con.execute(f"""
    SELECT l.* FROM game_lineups l JOIN games g ON g.game_id = CAST(l.game_id AS VARCHAR)
    WHERE g.competition_id IN ({lig}) AND g.date >= DATE '2024-07-01'""").df())
escribir("tm_player_valuations", con.execute(f"""
    SELECT v.* FROM player_valuations v JOIN players p USING (player_id)
    WHERE p.current_club_domestic_competition_id IN ({lig})""").df())
escribir("tm_transfers", con.execute("SELECT * FROM transfers WHERE transfer_date >= DATE '2018-01-01'").df())

if AF.exists():
    for f in AF.glob("*.parquet"):
        df = pd.read_parquet(f)
        if "api_liga" in df.columns and f.stem != "ligas":
            df = df[df.api_liga.isin(LIGAS_AF)]
        if f.stem in ("plantillas_actuales", "traspasos") and "api_equipo" in df.columns:
            eq = pd.read_parquet(AF / "equipos.parquet")
            df = df[df.api_equipo.isin(eq[eq.api_liga.isin(LIGAS_AF)].api_equipo)] if f.stem == "plantillas_actuales" else df
        escribir(f"af_{f.stem}", df)

tot = sum(p.stat().st_size for p in OUT.glob("*.parquet")) / 1e6
print(f"Total: {tot:.1f} MB")
