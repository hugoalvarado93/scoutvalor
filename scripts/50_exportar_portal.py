"""
Exporta los datos del portal como JSON estatico (web/public/data/).

Archivos:
  resumen.json      cifras generales y fecha de corte
  ligas.json        ligas con id de API-Football (logo) y numero de jugadores
  clubes.json       club Transfermarkt -> nombre, codigo de 3 letras, id API-Football (escudo)
  jugadores.json    tabla compacta (columnas -> arreglos) de jugadores activos para radar y buscador
  paises.json       jugadores por nacionalidad y por pais de liga
  movimientos.json  mayores subidas y bajadas de valor en la ultima actualizacion
  j/<n>.json        detalle por jugador (historial de valor, traspasos, temporadas), 256 fragmentos
"""
import json
import os
import re
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[1]
MUESTRAS = os.getenv("MUESTRAS")
PROC = RAIZ / "data" / "procesado"
OUT = Path(os.getenv("SALIDA_PORTAL", RAIZ / "web" / "public" / "data"))
HOY = pd.Timestamp(os.getenv("FECHA_CORTE", date.today().isoformat()))
FRAG = 256

POS = {"Goalkeeper": "POR", "Centre-Back": "DFC", "Left-Back": "LI", "Right-Back": "LD",
       "Defensive Midfield": "MCD", "Central Midfield": "MC", "Attacking Midfield": "MCO",
       "Left Midfield": "MI", "Right Midfield": "MD", "Left Winger": "EI", "Right Winger": "ED",
       "Second Striker": "SD", "Centre-Forward": "DC"}


CONMEBOL = {"Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Paraguay", "Peru", "Uruguay", "Venezuela"}
CONF_TM = {"europa": "UEFA", "afrika": "CAF", "asien": "AFC", "ozeanien": "OFC", "amerika": "CONCACAF"}
NOMBRES_LIGA = {
    "GB1": "Premier League", "ES1": "LaLiga", "IT1": "Serie A", "L1": "Bundesliga", "FR1": "Ligue 1",
    "NL1": "Eredivisie", "PO1": "Primeira Liga", "BE1": "Jupiler Pro League", "TR1": "Süper Lig",
    "GR1": "Super League Grecia", "SC1": "Scottish Premiership", "RU1": "Liga Premier de Rusia",
    "UKR1": "Liga Premier de Ucrania", "DK1": "Superliga de Dinamarca", "A1": "Bundesliga de Austria",
    "C1": "Super League de Suiza", "PL1": "Ekstraklasa", "SE1": "Allsvenskan", "NO1": "Eliteserien",
    "TS1": "Chance Liga", "KR1": "HNL", "SER1": "Superliga de Serbia", "RO1": "Superliga de Rumania",
    "BRA1": "Brasileirão", "ARG1": "Liga Profesional", "MLS1": "MLS", "MEX1": "Liga MX",
    "COL1": "Liga BetPlay", "SA1": "Saudi Pro League", "JAP1": "J1 League", "RSK1": "K League 1",
    "AUS1": "A-League",
}


def confederacion(pais, conf_tm):
    if pais in CONMEBOL:
        return "CONMEBOL"
    return CONF_TM.get(conf_tm)


def tm(nombre):
    if MUESTRAS:
        return pd.read_csv(Path(MUESTRAS) / f"tm_{nombre}.csv.gz")
    import duckdb
    con = duckdb.connect(str(RAIZ / "data/raw/transfermarkt/transfermarkt-datasets.duckdb"), read_only=True)
    return con.execute(f"SELECT * FROM {nombre}").df()


def af(nombre):
    if MUESTRAS:
        p = Path(MUESTRAS) / f"af_{nombre}.csv.gz"
        return pd.read_csv(p) if p.exists() else pd.DataFrame()
    p = RAIZ / f"data/api_football/parquet/{nombre}.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def proc(nombre):
    for p in (PROC / f"{nombre}.parquet", PROC / f"{nombre}.csv.gz"):
        if p.exists():
            return pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
    return pd.DataFrame()


def escribir(nombre, obj):
    p = OUT / nombre
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=_def), encoding="utf-8")
    return p.stat().st_size


def _def(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (pd.Timestamp, date)):
        return o.isoformat()[:10]
    return str(o)


def limpio(v):
    if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NaT:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def codigo_club(nombre: str) -> str:
    n = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().upper()
    n = re.sub(r"\b(FC|CF|CD|CLUB|SC|AC|AFC|SD|CA|CS|FK|SK|UD|RC|SSC|AS|DE|DEPORTIVO|ATLETICO|SPORT|THE)\b", " ", n)
    palabras = [w for w in re.split(r"[^A-Z0-9]+", n) if w]
    if not palabras:
        return "?"
    if len(palabras) == 1:
        return palabras[0][:3]
    return "".join(w[0] for w in palabras[:3]).ljust(3, palabras[0][1] if len(palabras[0]) > 1 else "X")[:3]


def main():
    players = tm("players")
    clubs = tm("clubs")
    comps = tm("competitions")
    countries = tm("countries")
    vals = tm("player_valuations")
    transfers = tm("transfers")
    af_j = af("jugadores_temporada")
    af_ligas = af("ligas")
    af_eq = af("equipos")
    vinc = proc("vinculos")
    valor = proc("valor")

    ult = players.last_season.max()
    act = players[players.last_season == ult].copy()
    act["current_club_id"] = pd.to_numeric(act.current_club_id, errors="coerce")
    act["edad"] = ((HOY - pd.to_datetime(act.date_of_birth, errors="coerce")).dt.days / 365.25).round(1)

    # ---- confederacion por nacionalidad
    conf = {p: confederacion(p, c) for p, c in zip(countries.country_name, countries.confederation)}

    # ---- ligas
    liga_af = {}
    if not af_ligas.empty:
        l = af_ligas.drop_duplicates("tm_liga")
        liga_af = dict(zip(l.tm_liga, l.api_liga))
    cnt = act.current_club_domestic_competition_id.value_counts()
    ligas = []
    for _, c in comps[comps.type == "domestic_league"].iterrows():
        cid = c.competition_id
        ligas.append({"id": cid, "nombre": NOMBRES_LIGA.get(cid, c["name"].replace("-", " ").title()), "pais": c.country_name,
                      "conf": confederacion(c.country_name, c.confederation), "af": limpio(liga_af.get(cid)),
                      "jugadores": int(cnt.get(cid, 0))})
    ligas.sort(key=lambda x: -x["jugadores"])

    # ---- clubes: escudo via el equipo de API-Football mas comun entre sus jugadores vinculados
    clubs["club_id"] = pd.to_numeric(clubs.club_id, errors="coerce")
    club_af = {}
    if len(vinc) and not af_j.empty:
        ultimo_eq = af_j.sort_values("temporada").groupby("api_jugador").api_equipo.last()
        m = vinc.merge(ultimo_eq.rename("api_equipo"), left_on="api_jugador", right_index=True)
        m = m.merge(act[["player_id", "current_club_id"]], on="player_id")
        club_af = m.groupby("current_club_id").api_equipo.agg(lambda s: s.value_counts().index[0]).to_dict()
    clubes = {}
    for _, c in clubs.iterrows():
        if pd.isna(c.club_id):
            continue
        nombre = c["name"]
        clubes[int(c.club_id)] = {"n": nombre, "c": codigo_club(nombre), "l": c.domestic_competition_id,
                                  "af": int(club_af[c.club_id]) if c.club_id in club_af else None}

    # ---- jugadores (formato columnar)
    act = act.merge(vinc[["player_id", "api_jugador"]], on="player_id", how="left") if len(vinc) else act.assign(api_jugador=np.nan)
    if len(valor):
        act = act.merge(valor.drop(columns=[c for c in ["edad", "api_jugador"] if c in valor.columns]), on="player_id", how="left")
    else:
        for c in ["valor_estimado", "brecha", "elegible_radar", "minutos", "goles", "asistencias", "calificacion"]:
            act[c] = np.nan
    contrato = pd.to_datetime(act.contract_expiration_date, errors="coerce")
    cols = {
        "id": act.player_id, "n": act["name"], "cl": act.current_club_id, "lg": act.current_club_domestic_competition_id,
        "p": act.sub_position.map(POS), "pg": act.position, "e": act.edad, "nac": act.country_of_citizenship,
        "cf": act.country_of_citizenship.map(conf), "ct": contrato.dt.strftime("%Y-%m"),
        "v": act.market_value_in_eur, "vmax": act.highest_market_value_in_eur, "ve": act.valor_estimado,
        "b": (act.brecha * 100).round(0), "r": act.elegible_radar, "pie": act.foot, "h": act.height_in_cm,
        "af": act.api_jugador, "min": act.minutos, "g": act.goles, "a": act.asistencias,
        "cal": act.calificacion.round(2) if "calificacion" in act else np.nan,
    }
    jug = {k: [limpio(x) for x in (s.tolist() if hasattr(s, "tolist") else s)] for k, s in cols.items()}
    jug["r"] = [bool(x) if x is not None else False for x in jug["r"]]
    for k in ("cl", "af", "v", "vmax", "ve", "b", "h", "min", "g", "a"):
        jug[k] = [int(x) if x is not None else None for x in jug[k]]

    # ---- paises
    por_nac = act.country_of_citizenship.value_counts()
    liga_pais = dict(zip(comps.competition_id, comps.country_name))
    por_liga = act.current_club_domestic_competition_id.map(liga_pais).value_counts()
    paises = [{"pais": p, "conf": conf.get(p), "nac": int(por_nac.get(p, 0)), "liga": int(por_liga.get(p, 0))}
              for p in sorted(set(por_nac.index) | set(por_liga.index))]

    # ---- movimientos de valor (ultima actualizacion de cada jugador activo)
    vals["date"] = pd.to_datetime(vals.date, errors="coerce")
    vals = vals.sort_values("date")
    dos = vals[vals.player_id.isin(act.player_id)].groupby("player_id").tail(2)
    g = dos.groupby("player_id").agg(v0=("market_value_in_eur", "first"), v1=("market_value_in_eur", "last"),
                                      f=("date", "last"), n=("date", "size"))
    g = g[(g.n == 2) & (g.f >= vals.date.max() - pd.Timedelta(days=45)) & (g.v0 > 0)]
    g["delta"] = g.v1 - g.v0
    g["pct"] = (g.v1 / g.v0 - 1) * 100
    g = g.join(act.set_index("player_id")[["name", "current_club_id", "sub_position", "edad"]])

    def mov(df):
        return [{"id": int(i), "n": r["name"], "cl": limpio(r.current_club_id), "p": POS.get(r.sub_position),
                 "e": limpio(r.edad), "v0": int(r.v0), "v1": int(r.v1), "pct": round(float(r.pct), 0)}
                for i, r in df.iterrows()]
    movimientos = {"fecha": vals.date.max(), "suben": mov(g.sort_values("delta", ascending=False).head(12)),
                   "bajan": mov(g.sort_values("delta").head(12))}

    # ---- detalle por jugador en fragmentos
    vals_a = vals[vals.player_id.isin(act.player_id)]
    tr = transfers[transfers.player_id.isin(act.player_id)].copy()
    tr["transfer_date"] = pd.to_datetime(tr.transfer_date, errors="coerce")
    tr = tr[tr.transfer_date <= HOY + pd.Timedelta(days=200)].sort_values("transfer_date", ascending=False)
    temporadas = pd.DataFrame()
    if not af_j.empty and len(vinc):
        cols_t = ["api_jugador", "temporada", "equipo", "api_equipo", "api_liga", "partidos", "titularidades", "minutos",
                  "goles", "asistencias", "pases_clave", "tiros", "entradas", "intercepciones", "duelos",
                  "duelos_ganados", "regates_exito", "atajadas", "amarillas", "rojas", "calificacion"]
        temporadas = af_j[[c for c in cols_t if c in af_j.columns]].merge(vinc[["player_id", "api_jugador"]], on="api_jugador")
        temporadas = temporadas.sort_values(["temporada", "minutos"], ascending=[False, False])
    frags = {i: {} for i in range(FRAG)}
    vg = {k: v for k, v in vals_a.groupby("player_id")}
    tg = {k: v for k, v in tr.groupby("player_id")}
    sg = {k: v for k, v in temporadas.groupby("player_id")} if len(temporadas) else {}
    for pid in act.player_id:
        d = {}
        if pid in vg:
            d["vh"] = [[r.date.strftime("%Y-%m-%d"), int(r.market_value_in_eur)] for r in vg[pid].itertuples()]
        if pid in tg:
            d["tr"] = [{"f": r.transfer_date.strftime("%Y-%m-%d"), "de": r.from_club_name, "a": r.to_club_name,
                        "dei": int(r.from_club_id) if pd.notna(r.from_club_id) else None,
                        "ai": int(r.to_club_id) if pd.notna(r.to_club_id) else None,
                        "fee": limpio(r.transfer_fee), "mv": limpio(r.market_value_in_eur)} for r in tg[pid].itertuples()]
        if pid in sg:
            d["ts"] = [{k: (int(v) if k in ("api_equipo", "api_liga", "temporada") and limpio(v) is not None else limpio(v))
                        for k, v in r.items() if k not in ("player_id", "api_jugador")}
                       for r in sg[pid].to_dict("records")]
        frags[int(pid) % FRAG][str(int(pid))] = d

    # ---- resumen
    prox = HOY + timedelta(days=(7 - HOY.weekday()) % 7 or 7)
    resumen = {"fecha_datos": HOY.strftime("%Y-%m-%d"), "corte_transfermarkt": vals.date.max().strftime("%Y-%m-%d"),
               "proxima": prox.strftime("%Y-%m-%d"), "jugadores": int(len(act)),
               "ligas": int(af_ligas.tm_liga.nunique()) if not af_ligas.empty else int(sum(1 for l in ligas if l["jugadores"] > 0)),
               "equipos": int(af_eq.api_equipo.nunique()) if not af_eq.empty else int(act.current_club_id.nunique()),
               "con_valor_estimado": int(pd.notna(act.valor_estimado).sum())}

    tam = {"resumen.json": escribir("resumen.json", resumen), "ligas.json": escribir("ligas.json", ligas),
           "clubes.json": escribir("clubes.json", clubes), "jugadores.json": escribir("jugadores.json", jug),
           "paises.json": escribir("paises.json", paises), "movimientos.json": escribir("movimientos.json", movimientos)}
    tam["j/*.json"] = sum(escribir(f"j/{i}.json", frags[i]) for i in range(FRAG))
    for k, v in tam.items():
        print(f"{k}: {v/1e6:.2f} MB")
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
