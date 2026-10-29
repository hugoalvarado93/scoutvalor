"""
Ingesta masiva de API-Football (plan Pro).

Fases:
  ligas      verifica IDs y temporadas disponibles de las ligas objetivo
  jugadores  estadisticas por jugador y temporada (/players, paginado)
  plantillas plantillas actuales por equipo (/teams + /players/squads)
  traspasos  traspasos por equipo de la temporada actual (/transfers)

Salida en data/api_football/:
  raw/<fase>/*.json.gz   respuestas originales
  parquet/*.parquet      tablas planas listas para el pipeline

Uso:
  python scripts/10_api_football_ingesta.py --fases ligas,jugadores,plantillas,traspasos
  python scripts/10_api_football_ingesta.py --fases jugadores --temporadas 2025,2026 --presupuesto 3000
"""
import argparse
import gzip
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "data" / "api_football"
load_dotenv(RAIZ / ".env")
BASE = "https://v3.football.api-sports.io"

# codigo Transfermarkt -> (id API-Football, pais esperado)
LIGAS = {
    "GB1": (39, "England"), "ES1": (140, "Spain"), "IT1": (135, "Italy"),
    "L1": (78, "Germany"), "FR1": (61, "France"), "NL1": (88, "Netherlands"),
    "PO1": (94, "Portugal"), "BE1": (144, "Belgium"), "TR1": (203, "Turkey"),
    "GR1": (197, "Greece"), "SC1": (179, "Scotland"), "RU1": (235, "Russia"),
    "UKR1": (333, "Ukraine"), "DK1": (119, "Denmark"), "A1": (218, "Austria"),
    "C1": (207, "Switzerland"), "PL1": (106, "Poland"), "SE1": (113, "Sweden"),
    "NO1": (103, "Norway"), "TS1": (345, "Czech-Republic"), "KR1": (210, "Croatia"),
    "SER1": (286, "Serbia"), "RO1": (283, "Romania"),
    "BRA1": (71, "Brazil"), "ARG1": (128, "Argentina"), "MLS1": (253, "USA"),
    "MEX1": (262, "Mexico"), "COL1": (239, "Colombia"),
    "SA1": (307, "Saudi-Arabia"), "JAP1": (98, "Japan"), "RSK1": (292, "South-Korea"),
    "AUS1": (188, "Australia"),
    # segundas divisiones relevantes para buscar talento barato
    "GB2": (40, "England"), "ES2": (141, "Spain"), "IT2": (136, "Italy"),
    "L2": (79, "Germany"), "FR2": (62, "France"), "NL2": (89, "Netherlands"),
    "PO2": (95, "Portugal"), "BRA2": (72, "Brazil"), "ARG2": (129, "Argentina"),
    "MEX2": (263, "Mexico"), "URU1": (268, "Uruguay"), "CHI1": (265, "Chile"),
    "ECU1": (242, "Ecuador"), "PAR1": (250, "Paraguay"), "PER1": (281, "Peru"),
}


class Cliente:
    def __init__(self, key: str, presupuesto: int):
        self.s = requests.Session()
        self.s.headers["x-apisports-key"] = key
        self.presupuesto = presupuesto
        self.usadas = 0
        self.restantes_dia = None

    def get(self, ruta: str, **params):
        if self.usadas >= self.presupuesto:
            raise RuntimeError("presupuesto agotado")
        for intento in range(5):
            r = self.s.get(BASE + ruta, params=params, timeout=60)
            self.usadas += 1
            min_rest = int(r.headers.get("X-RateLimit-Remaining", 10) or 10)
            self.restantes_dia = r.headers.get("x-ratelimit-requests-remaining", self.restantes_dia)
            if r.status_code == 429 or min_rest <= 1:
                time.sleep(15)
            if r.status_code == 200:
                d = r.json()
                err = d.get("errors")
                if err and "rateLimit" in str(err):
                    time.sleep(15)
                    continue
                return d
            time.sleep(2 ** intento)
        raise RuntimeError(f"fallo {ruta} {params}")


def guardar_raw(fase: str, nombre: str, datos):
    p = SALIDA / "raw" / fase / f"{nombre}.json.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, "wt", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False)


def guardar_parquet(nombre: str, filas: list[dict]):
    if not filas:
        return
    p = SALIDA / "parquet" / f"{nombre}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(filas)
    if p.exists():  # acumula entre corridas parciales
        df = pd.concat([pd.read_parquet(p), df]).drop_duplicates()
    df.to_parquet(p, index=False)
    print(f"  -> {p.relative_to(RAIZ)}: {len(df):,} filas")


def fase_ligas(c: Cliente, temporadas: list[int]):
    print("\n[ligas]")
    filas = []
    for tm, (lid, pais) in LIGAS.items():
        d = c.get("/leagues", id=lid)
        guardar_raw("ligas", f"{tm}_{lid}", d)
        if not d.get("response"):
            print(f"  {tm}: id {lid} sin respuesta")
            continue
        info = d["response"][0]
        ok_pais = info["country"]["name"] == pais
        for s in info["seasons"]:
            cov = s.get("coverage", {})
            filas.append({
                "tm_liga": tm, "api_liga": lid, "nombre": info["league"]["name"],
                "pais": info["country"]["name"], "pais_ok": ok_pais,
                "temporada": s["year"], "actual": s.get("current"),
                "inicio": s.get("start"), "fin": s.get("end"),
                "cov_jugadores": cov.get("players"),
                "cov_stats_jugador": (cov.get("fixtures") or {}).get("statistics_players"),
                "cov_lesiones": cov.get("injuries"),
            })
        marca = "OK" if ok_pais else f"REVISAR (pais={info['country']['name']})"
        print(f"  {tm:5} {lid:4} {info['league']['name'][:30]:30} {marca}")
    df = pd.DataFrame(filas)
    p = SALIDA / "parquet" / "ligas.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return df


def objetivos(df_ligas: pd.DataFrame, temporadas: list[int]):
    df = df_ligas[df_ligas.pais_ok & df_ligas.cov_jugadores.fillna(False)]
    actuales = df[df.actual == True]  # noqa: E712
    if temporadas:
        df = df[df.temporada.isin(temporadas)]
    return df, actuales


def aplanar_jugador(item: dict) -> list[dict]:
    p = item["player"]
    base = {
        "api_jugador": p["id"], "nombre": p.get("name"), "nombres": p.get("firstname"),
        "apellidos": p.get("lastname"), "edad": p.get("age"),
        "nacimiento": (p.get("birth") or {}).get("date"),
        "lugar_nacimiento": (p.get("birth") or {}).get("place"),
        "pais_nacimiento": (p.get("birth") or {}).get("country"),
        "nacionalidad": p.get("nationality"), "altura": p.get("height"),
        "peso": p.get("weight"), "lesionado": p.get("injured"), "foto": p.get("photo"),
    }
    filas = []
    for st in item.get("statistics", []):
        g, sh, go, pa = st.get("games", {}), st.get("shots", {}), st.get("goals", {}), st.get("passes", {})
        ta, du, dr, fo = st.get("tackles", {}), st.get("duels", {}), st.get("dribbles", {}), st.get("fouls", {})
        ca, pe, su = st.get("cards", {}), st.get("penalty", {}), st.get("substitutes", {})
        filas.append({
            **base,
            "api_equipo": st["team"]["id"], "equipo": st["team"]["name"],
            "api_liga": st["league"]["id"], "temporada": st["league"]["season"],
            "partidos": g.get("appearences"), "titularidades": g.get("lineups"),
            "minutos": g.get("minutes"), "posicion": g.get("position"),
            "calificacion": g.get("rating"), "capitan": g.get("captain"),
            "entro_cambio": su.get("in"), "salio_cambio": su.get("out"), "banca": su.get("bench"),
            "tiros": sh.get("total"), "tiros_puerta": sh.get("on"),
            "goles": go.get("total"), "goles_concedidos": go.get("conceded"),
            "asistencias": go.get("assists"), "atajadas": go.get("saves"),
            "pases": pa.get("total"), "pases_clave": pa.get("key"), "precision_pase": pa.get("accuracy"),
            "entradas": ta.get("total"), "bloqueos": ta.get("blocks"), "intercepciones": ta.get("interceptions"),
            "duelos": du.get("total"), "duelos_ganados": du.get("won"),
            "regates_intentos": dr.get("attempts"), "regates_exito": dr.get("success"),
            "regateado": dr.get("past"),
            "faltas_recibidas": fo.get("drawn"), "faltas_cometidas": fo.get("committed"),
            "amarillas": ca.get("yellow"), "doble_amarilla": ca.get("yellowred"), "rojas": ca.get("red"),
            "penal_ganado": pe.get("won"), "penal_cometido": pe.get("commited"),
            "penal_anotado": pe.get("scored"), "penal_fallado": pe.get("missed"),
            "penal_atajado": pe.get("saved"),
        })
    return filas


def fase_jugadores(c: Cliente, obj: pd.DataFrame):
    print(f"\n[jugadores] {len(obj)} liga-temporadas")
    for _, o in obj.iterrows():
        nombre = f"{o.tm_liga}_{o.temporada}"
        marca = SALIDA / "raw" / "jugadores" / f"{nombre}.completo"
        if marca.exists():
            continue
        filas, pagina, total = [], 1, 1
        while pagina <= total:
            d = c.get("/players", league=int(o.api_liga), season=int(o.temporada), page=pagina)
            guardar_raw("jugadores", f"{nombre}_p{pagina}", d)
            total = (d.get("paging") or {}).get("total", 1)
            for item in d.get("response", []):
                filas.extend(aplanar_jugador(item))
            pagina += 1
        print(f"  {nombre}: {total} paginas, {len(filas):,} filas (consultas usadas {c.usadas})")
        guardar_parquet("jugadores_temporada", filas)
        marca.write_text(str(total))


def fase_plantillas(c: Cliente, actuales: pd.DataFrame):
    print(f"\n[plantillas] {len(actuales)} ligas en temporada actual")
    equipos, plantillas = [], []
    for _, o in actuales.iterrows():
        d = c.get("/teams", league=int(o.api_liga), season=int(o.temporada))
        guardar_raw("equipos", f"{o.tm_liga}_{o.temporada}", d)
        for t in d.get("response", []):
            tm, ve = t["team"], t.get("venue") or {}
            equipos.append({"api_equipo": tm["id"], "equipo": tm["name"], "codigo": tm.get("code"),
                            "pais": tm.get("country"), "fundado": tm.get("founded"), "logo": tm.get("logo"),
                            "estadio": ve.get("name"), "ciudad": ve.get("city"), "capacidad": ve.get("capacity"),
                            "api_liga": int(o.api_liga), "tm_liga": o.tm_liga, "temporada": int(o.temporada)})
    guardar_parquet("equipos", equipos)
    for e in equipos:
        d = c.get("/players/squads", team=e["api_equipo"])
        guardar_raw("plantillas", str(e["api_equipo"]), d)
        for sq in d.get("response", []):
            for p in sq.get("players", []):
                plantillas.append({"api_equipo": e["api_equipo"], "api_jugador": p["id"], "nombre": p.get("name"),
                                   "edad": p.get("age"), "numero": p.get("number"),
                                   "posicion": p.get("position"), "foto": p.get("photo")})
    print(f"  {len(equipos)} equipos (consultas usadas {c.usadas})")
    guardar_parquet("plantillas_actuales", plantillas)
    return equipos


def fase_traspasos(c: Cliente, equipos: list[dict]):
    print(f"\n[traspasos] {len(equipos)} equipos")
    filas = []
    for e in equipos:
        d = c.get("/transfers", team=e["api_equipo"])
        guardar_raw("traspasos", str(e["api_equipo"]), d)
        for it in d.get("response", []):
            for t in it.get("transfers", []):
                filas.append({"api_jugador": it["player"]["id"], "nombre": it["player"].get("name"),
                              "fecha": t.get("date"), "tipo": t.get("type"),
                              "de_equipo": (t["teams"]["out"] or {}).get("id"),
                              "de_nombre": (t["teams"]["out"] or {}).get("name"),
                              "a_equipo": (t["teams"]["in"] or {}).get("id"),
                              "a_nombre": (t["teams"]["in"] or {}).get("name")})
    guardar_parquet("traspasos", filas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fases", default="ligas,jugadores,plantillas,traspasos")
    ap.add_argument("--temporadas", default="2023,2024,2025,2026")
    ap.add_argument("--presupuesto", type=int, default=6500, help="maximo de consultas en esta corrida")
    a = ap.parse_args()
    key = os.getenv("API_FOOTBALL_KEY")
    if not key:
        sys.exit("Falta API_FOOTBALL_KEY")
    fases = a.fases.split(",")
    temporadas = [int(t) for t in a.temporadas.split(",") if t]
    c = Cliente(key, a.presupuesto)
    try:
        df_ligas = fase_ligas(c, temporadas)
        obj, actuales = objetivos(df_ligas, temporadas)
        if "jugadores" in fases:
            fase_jugadores(c, obj)
        equipos = []
        if "plantillas" in fases or "traspasos" in fases:
            equipos = fase_plantillas(c, actuales)
        if "traspasos" in fases:
            fase_traspasos(c, equipos)
    except RuntimeError as e:
        print(f"\nDetenido: {e}")
    print(f"\nConsultas usadas: {c.usadas}. Restantes hoy segun API: {c.restantes_dia}")


if __name__ == "__main__":
    main()
