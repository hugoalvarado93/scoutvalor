"""
Paso 2: diagnostico de cobertura de los datos descargados.

Genera data/reports/cobertura.md con:
  - esquema de todas las tablas de Transfermarkt
  - cobertura por liga: jugadores, valor de mercado, contratos, salario de datos, frescura
  - temporadas disponibles por liga en apariciones y alineaciones
  - resumen de StatsBomb, football-data y API-Football

Uso:
    python scripts/02_reporte_cobertura.py
"""
import json
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
REPORTES = RAIZ / "data" / "reports"
REPORTES.mkdir(parents=True, exist_ok=True)

salida: list[str] = ["# Reporte de cobertura de datos\n"]


def seccion(titulo: str):
    salida.append(f"\n## {titulo}\n")
    print(f"\n== {titulo}")


def tabla(df: pd.DataFrame):
    salida.append(df.to_markdown(index=False) if not df.empty else "_(vacio)_")
    salida.append("")
    print(df.to_string(index=False)[:3000])


def columnas(con, t):
    return set(con.execute(f"DESCRIBE {t}").df()["column_name"])


def transfermarkt():
    ruta = RAW / "transfermarkt" / "transfermarkt-datasets.duckdb"
    if not ruta.exists():
        salida.append("Transfermarkt no descargado.")
        return
    con = duckdb.connect(str(ruta), read_only=True)
    tablas = con.execute("SHOW TABLES").df()["name"].tolist()

    seccion("Transfermarkt: tablas y esquemas")
    for t in tablas:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        esquema = con.execute(f"DESCRIBE {t}").df()[["column_name", "column_type"]]
        salida.append(f"### {t} ({n:,} filas)\n")
        salida.append(", ".join(f"`{c}` {ty}" for c, ty in esquema.values))
        salida.append("")
        print(f"{t}: {n:,} filas, {len(esquema)} columnas")

    cp = columnas(con, "players")
    contrato = "contract_expiration_date" if "contract_expiration_date" in cp else None
    seccion("Transfermarkt: cobertura de jugadores por liga (jugadores activos ultima temporada)")
    sql = f"""
    WITH ult AS (SELECT MAX(last_season) AS s FROM players)
    SELECT p.current_club_domestic_competition_id AS liga,
           c.name AS nombre,
           COUNT(*) AS jugadores,
           ROUND(100.0*AVG(CASE WHEN p.market_value_in_eur IS NOT NULL THEN 1 ELSE 0 END),1) AS pct_valor,
           {f"ROUND(100.0*AVG(CASE WHEN p.{contrato} IS NOT NULL THEN 1 ELSE 0 END),1)" if contrato else "NULL"} AS pct_contrato,
           ROUND(100.0*AVG(CASE WHEN p.sub_position IS NOT NULL THEN 1 ELSE 0 END),1) AS pct_subposicion,
           ROUND(100.0*AVG(CASE WHEN p.date_of_birth IS NOT NULL THEN 1 ELSE 0 END),1) AS pct_nacimiento,
           ROUND(SUM(p.market_value_in_eur)/1e6,0) AS valor_total_meur
    FROM players p
    CROSS JOIN ult
    LEFT JOIN competitions c ON c.competition_id = p.current_club_domestic_competition_id
    WHERE p.last_season = ult.s
    GROUP BY 1,2 ORDER BY jugadores DESC
    """
    tabla(con.execute(sql).df())

    seccion("Transfermarkt: frescura por tabla")
    fres = []
    for t, col in [("games", "date"), ("appearances", "date"), ("player_valuations", "date"), ("transfers", "transfer_date")]:
        if t in tablas and col in columnas(con, t):
            mn, mx = con.execute(f"SELECT MIN({col}), MAX({col}) FROM {t}").fetchone()
            fres.append({"tabla": t, "desde": mn, "hasta": mx})
    tabla(pd.DataFrame(fres))

    seccion("Transfermarkt: partidos y alineaciones por liga y temporada (ultimas 4)")
    sql = """
    SELECT g.competition_id AS liga, g.season,
           COUNT(DISTINCT g.game_id) AS partidos,
           COUNT(DISTINCT l.game_id) AS partidos_con_alineacion
    FROM games g
    LEFT JOIN game_lineups l ON l.game_id = g.game_id
    WHERE TRY_CAST(g.season AS INTEGER) >= (SELECT MAX(TRY_CAST(season AS INTEGER)) - 3 FROM games)
      AND g.competition_type = 'domestic_league'
    GROUP BY 1,2 ORDER BY 1,2
    """
    try:
        df = con.execute(sql).df()
        tabla(df.pivot_table(index="liga", columns="season",
                             values=["partidos", "partidos_con_alineacion"], aggfunc="sum").reset_index())
    except Exception as e:  # noqa: BLE001
        salida.append(f"Error: {e}")

    seccion("Transfermarkt: traspasos con monto por temporada")
    if "transfers" in tablas:
        ct = columnas(con, "transfers")
        if "transfer_fee" in ct and "transfer_season" in ct:
            tabla(con.execute("""
                SELECT transfer_season, COUNT(*) AS traspasos,
                       SUM(CASE WHEN transfer_fee > 0 THEN 1 ELSE 0 END) AS con_monto
                FROM transfers GROUP BY 1 ORDER BY 1 DESC LIMIT 12""").df())

    seccion("Transfermarkt: muestra Liga MX (10 jugadores mas valiosos)")
    cols = "name, current_club_name, sub_position, date_of_birth, country_of_citizenship, market_value_in_eur"
    if contrato:
        cols += f", {contrato}"
    tabla(con.execute(f"""
        SELECT {cols} FROM players
        WHERE current_club_domestic_competition_id = 'MEX1'
          AND last_season = (SELECT MAX(last_season) FROM players)
        ORDER BY market_value_in_eur DESC NULLS LAST LIMIT 10""").df())


def statsbomb():
    ruta = RAW / "statsbomb" / "competitions.json"
    if not ruta.exists():
        return
    seccion("StatsBomb Open Data: competiciones gratuitas")
    df = pd.DataFrame(json.loads(ruta.read_text(encoding="utf-8")))
    tabla(df[["competition_name", "season_name", "competition_gender", "country_name"]]
          .sort_values(["competition_gender", "competition_name", "season_name"]))


def football_data():
    base = RAW / "football_data"
    if not base.exists():
        return
    seccion("football-data.co.uk: archivos y columnas de momios")
    filas = []
    for f in sorted(base.rglob("*.csv")):
        try:
            df = pd.read_csv(f, encoding="latin-1", on_bad_lines="skip")
            momios = [c for c in df.columns if c.startswith(("B365", "PS", "Max", "Avg"))]
            filas.append({"archivo": f"{f.parent.name}/{f.name}", "filas": len(df),
                          "temporadas": df["Season"].nunique() if "Season" in df else 1,
                          "cols_momios": len(momios)})
        except Exception as e:  # noqa: BLE001
            filas.append({"archivo": f.name, "filas": f"error: {e}"})
    tabla(pd.DataFrame(filas))


def api_football():
    base = RAW / "api_football" / "diagnostico"
    if not base.exists():
        return
    seccion("API-Football: diagnostico")
    for f in sorted(base.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        resumen = {"archivo": f.name, "resultados": d.get("results"), "errores": d.get("errors")}
        if f.stem == "status":
            # Solo plan y limites: nunca publicar datos personales de la cuenta
            cuenta = d.get("response") or {}
            if isinstance(cuenta, dict):
                resumen["plan"] = (cuenta.get("subscription") or {}).get("plan")
                resumen["limite_diario"] = (cuenta.get("requests") or {}).get("limit_day")
        if f.stem in ("liga_mx", "premier") and d.get("response"):
            temporadas = d["response"][0].get("seasons", [])
            resumen["temporadas"] = [
                {"anio": s["year"], "actual": s.get("current"),
                 "jugadores": s.get("coverage", {}).get("players"),
                 "stats_jugador": s.get("coverage", {}).get("fixtures", {}).get("statistics_players")}
                for s in temporadas[-4:]]
        salida.append("```json\n" + json.dumps(resumen, ensure_ascii=False, indent=2, default=str)[:4000] + "\n```")
        print(json.dumps(resumen, ensure_ascii=False, default=str)[:600])


if __name__ == "__main__":
    transfermarkt()
    statsbomb()
    football_data()
    api_football()
    destino = REPORTES / "cobertura.md"
    destino.write_text("\n".join(salida), encoding="utf-8")
    print(f"\nReporte escrito en {destino}")
