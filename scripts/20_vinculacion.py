"""
Vinculacion de jugadores Transfermarkt <-> API-Football (record linkage).

Metodo:
  1. Bloqueo por fecha de nacimiento exacta (candidatos = mismo dia de nacimiento).
  2. Puntaje por par:
       nombre       0.55  similitud de caracteres (TF-IDF n-gramas 2-4) y de tokens, la mayor
       nacionalidad 0.20  coincidencia exacta tras normalizar nombres de pais
       club         0.15  similitud del club actual (TM) contra los clubes del jugador (API)
       estatura     0.10  1 si |diferencia| <= 2 cm, decae hasta 0 a los 8 cm
  3. Asignacion uno a uno, de mayor a menor puntaje; se acepta con puntaje >= UMBRAL.
  4. Segunda pasada sin fecha (fecha faltante o desfasada): nombre >= 0.92 + nacionalidad + club.

Entradas:
  Pipeline: data/raw/transfermarkt/*.duckdb y data/api_football/parquet/
  Local:    MUESTRAS=/ruta/a/rama/muestras (CSV gzip)
Salidas:
  data/procesado/vinculos.parquet (o .csv.gz en local)
  data/reports/vinculacion.md
"""
import os
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[1]
MUESTRAS = os.getenv("MUESTRAS")
PROC = RAIZ / "data" / "procesado"
REPORTES = RAIZ / "data" / "reports"
UMBRAL = 0.62

PESOS = {"nombre": 0.55, "nacionalidad": 0.20, "club": 0.15, "estatura": 0.10}

# API-Football -> Transfermarkt para paises que se escriben distinto
PAISES = {
    "usa": "united states", "south-korea": "korea, south", "korea republic": "korea, south",
    "czech-republic": "czech republic", "ivory coast": "cote d'ivoire", "côte d'ivoire": "cote d'ivoire",
    "congo dr": "dr congo", "bosnia": "bosnia-herzegovina", "bosnia and herzegovina": "bosnia-herzegovina",
    "turkiye": "turkey", "türkiye": "turkey", "cape verde islands": "cape verde",
    "north macedonia": "north macedonia", "republic of ireland": "ireland",
    "trinidad and tobago": "trinidad and tobago", "saudi-arabia": "saudi arabia",
    "new-zealand": "new zealand", "costa-rica": "costa rica", "el-salvador": "el salvador",
    "south-africa": "south africa", "curacao": "curacao", "curaçao": "curacao",
}


def norm(s) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def norm_pais(s) -> str:
    n = norm(s).replace(" ", "-") if isinstance(s, str) else ""
    n2 = norm(s)
    return PAISES.get(n, PAISES.get(n2, n2))


def norm_club(s) -> str:
    n = norm(s)
    n = re.sub(r"\b(fc|cf|cd|club|sc|ac|afc|sd|ca|cs|fk|sk|ud|rc|ssc|as|de|deportivo|futbol|football)\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


# ---------------------------------------------------------------- carga
def cargar_tm() -> pd.DataFrame:
    if MUESTRAS:
        return pd.read_csv(Path(MUESTRAS) / "tm_players.csv.gz")
    import duckdb
    con = duckdb.connect(str(RAIZ / "data/raw/transfermarkt/transfermarkt-datasets.duckdb"), read_only=True)
    return con.execute("SELECT * FROM players").df()


def cargar_af() -> pd.DataFrame:
    if MUESTRAS:
        p = Path(MUESTRAS) / "af_jugadores_temporada.csv.gz"
        return pd.read_csv(p) if p.exists() else pd.DataFrame()
    p = RAIZ / "data/api_football/parquet/jugadores_temporada.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def preparar_tm(tm: pd.DataFrame) -> pd.DataFrame:
    tm = tm.copy()
    tm["dob"] = pd.to_datetime(tm["date_of_birth"], errors="coerce").dt.date
    tm["nombre_n"] = (tm["first_name"].fillna("") + " " + tm["last_name"].fillna("")).map(norm)
    tm.loc[tm.nombre_n == "", "nombre_n"] = tm["name"].map(norm)
    tm["corto_n"] = tm["name"].map(norm)
    tm["pais_n"] = tm["country_of_citizenship"].map(norm_pais)
    tm["pais_nac_n"] = tm["country_of_birth"].map(norm_pais)
    tm["club_n"] = tm["current_club_name"].map(norm_club)
    tm["altura"] = pd.to_numeric(tm["height_in_cm"], errors="coerce")
    return tm[["player_id", "dob", "nombre_n", "corto_n", "pais_n", "pais_nac_n", "club_n", "altura",
               "current_club_domestic_competition_id", "last_season", "name"]]


def preparar_af(af: pd.DataFrame) -> pd.DataFrame:
    """Un registro por jugador de API-Football, con todos sus clubes."""
    af = af.copy()
    af["dob"] = pd.to_datetime(af["nacimiento"], errors="coerce").dt.date
    af["altura"] = pd.to_numeric(af["altura"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    af = af.sort_values("temporada")
    g = af.groupby("api_jugador")
    j = g.agg(nombres=("nombres", "last"), apellidos=("apellidos", "last"), nombre=("nombre", "last"),
              dob=("dob", "last"), nacionalidad=("nacionalidad", "last"), altura=("altura", "max"),
              api_liga=("api_liga", "last"), temporada=("temporada", "max"),
              clubes=("equipo", lambda s: sorted({norm_club(x) for x in s if isinstance(x, str)}))).reset_index()
    j["nombre_n"] = (j["nombres"].fillna("") + " " + j["apellidos"].fillna("")).map(norm)
    j["corto_n"] = j["nombre"].map(norm)
    j["pais_n"] = j["nacionalidad"].map(norm_pais)
    return j


# ---------------------------------------------------------------- puntaje
class Similitud:
    def __init__(self, textos: list[str]):
        self.v = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1)
        self.v.fit(textos)

    def cos(self, a: list[str], b: list[str]) -> np.ndarray:
        A, B = self.v.transform(a), self.v.transform(b)
        return np.asarray(A.multiply(B).sum(axis=1)).ravel()


def tokens(a: str, b: str) -> float:
    ta, tb = set(a.split()), set(b.split())
    if not ta or not tb:
        return 0.0
    # proporcion de tokens del nombre mas corto contenidos en el otro (apellidos compuestos)
    return len(ta & tb) / min(len(ta), len(tb))


def puntuar(pares: pd.DataFrame, sim: Similitud) -> pd.DataFrame:
    p = pares
    c1 = sim.cos(p.nombre_n_tm.tolist(), p.nombre_n_af.tolist())
    c2 = sim.cos(p.corto_n_tm.tolist(), p.corto_n_af.tolist())
    tk = np.array([max(tokens(a, b), tokens(c, d)) for a, b, c, d in
                   zip(p.nombre_n_tm, p.nombre_n_af, p.corto_n_tm, p.nombre_n_af)])
    p["s_nombre"] = np.maximum.reduce([c1, c2, tk * 0.95])
    p["s_pais"] = ((p.pais_n_tm == p.pais_n_af) | (p.pais_nac_n == p.pais_n_af)).astype(float)
    p.loc[(p.pais_n_af == "") | (p.pais_n_tm == ""), "s_pais"] = 0.5
    club_tm = p.club_n.tolist()
    p["s_club"] = [max((tokens(ct, x) for x in cl), default=0.0) if ct else 0.5
                   for ct, cl in zip(club_tm, p.clubes)]
    d = (p.altura_tm - p.altura_af).abs()
    p["s_altura"] = np.where(d.isna(), 0.5, np.clip(1 - (d - 2) / 6, 0, 1))
    p["puntaje"] = (PESOS["nombre"] * p.s_nombre + PESOS["nacionalidad"] * p.s_pais
                    + PESOS["club"] * p.s_club + PESOS["estatura"] * p.s_altura)
    # Nombre compuesto cuyo apellido no aparece en el otro registro: solo coincide el nombre de pila
    # (p. ej. "Luis Vega" vs "Luis Espinoza"). Los apodos de una sola palabra (Savinho, Kuni) no se penalizan.
    apellido_tm = p.corto_n_tm.str.split().str[-1].fillna("")
    multi = p.corto_n_tm.str.split().str.len().fillna(0) >= 2
    falta_apellido = [a not in set(b.split()) and a not in b for a, b in zip(apellido_tm, p.nombre_n_af)]
    p.loc[multi & pd.Series(falta_apellido, index=p.index) & (p.s_nombre < 0.6), "puntaje"] = 0.0
    return p


def uno_a_uno(p: pd.DataFrame, umbral: float) -> pd.DataFrame:
    p = p[p.puntaje >= umbral].sort_values("puntaje", ascending=False)
    p = p.drop_duplicates("player_id").drop_duplicates("api_jugador")
    return p


# ---------------------------------------------------------------- principal
def vincular(tm: pd.DataFrame, af: pd.DataFrame) -> pd.DataFrame:
    sim = Similitud(tm.nombre_n.tolist() + af.nombre_n.tolist())
    # pasada 1: misma fecha de nacimiento
    pares = tm.dropna(subset=["dob"]).merge(af.dropna(subset=["dob"]), on="dob", suffixes=("_tm", "_af"))
    print(f"Pasada 1: {len(pares):,} pares candidatos")
    v1 = uno_a_uno(puntuar(pares, sim), UMBRAL).assign(metodo="fecha")
    # pasada 2: sin fecha, nombre casi identico + pais + club
    tm2 = tm[~tm.player_id.isin(v1.player_id)]
    af2 = af[~af.api_jugador.isin(v1.api_jugador)]
    tm2 = tm2.assign(k=tm2.nombre_n.str.split().str[-1])
    af2 = af2.assign(k=af2.nombre_n.str.split().str[-1])
    pares2 = tm2.merge(af2, on="k", suffixes=("_tm", "_af"))
    pares2 = pares2[pares2.pais_n_tm == pares2.pais_n_af]
    print(f"Pasada 2: {len(pares2):,} pares candidatos")
    if len(pares2):
        pares2 = puntuar(pares2, sim)
        pares2 = pares2[(pares2.s_nombre >= 0.92) & (pares2.s_club >= 0.5)]
        v2 = uno_a_uno(pares2, 0.80).assign(metodo="nombre")
    else:
        v2 = pd.DataFrame()
    cols = ["player_id", "api_jugador", "puntaje", "s_nombre", "s_pais", "s_club", "s_altura", "metodo",
            "name", "nombre_n_af", "current_club_domestic_competition_id", "api_liga", "temporada"]
    return pd.concat([v1, v2])[cols].rename(columns={"name": "nombre_tm", "nombre_n_af": "nombre_af"})


def reporte(tm, af, v) -> str:
    out = ["# Vinculacion Transfermarkt <-> API-Football\n",
           f"- Jugadores Transfermarkt: {len(tm):,}", f"- Jugadores API-Football: {len(af):,}",
           f"- Vinculados: {len(v):,} (fecha: {(v.metodo=='fecha').sum():,}, nombre: {(v.metodo=='nombre').sum():,})\n"]
    ult = tm.last_season.max()
    act = tm[tm.last_season == ult]
    r = (act.assign(ok=act.player_id.isin(v.player_id))
         .groupby("current_club_domestic_competition_id").ok.agg(["size", "mean"])
         .rename(columns={"size": "activos", "mean": "pct_vinculado"}))
    r["pct_vinculado"] = (r.pct_vinculado * 100).round(1)
    out += ["## Cobertura por liga Transfermarkt (jugadores activos)\n",
            r.sort_values("activos", ascending=False).reset_index().to_markdown(index=False), ""]
    ra = (af.assign(ok=af.api_jugador.isin(v.api_jugador)).groupby("api_liga").ok.agg(["size", "mean"])
          .rename(columns={"size": "jugadores", "mean": "pct_vinculado"}))
    ra["pct_vinculado"] = (ra.pct_vinculado * 100).round(1)
    out += ["## Cobertura por liga API-Football (ultima liga del jugador)\n",
            ra.sort_values("jugadores", ascending=False).reset_index().to_markdown(index=False), ""]
    bandas = pd.cut(v.puntaje, [0.6, 0.7, 0.8, 0.9, 1.01])
    out += ["## Distribucion de puntajes\n", v.groupby(bandas, observed=True).size().rename("pares")
            .reset_index().astype(str).to_markdown(index=False), ""]
    out += ["## Muestra para revision manual (zona dudosa 0.62-0.75)\n",
            v[v.puntaje < 0.75].sample(min(25, (v.puntaje < 0.75).sum()), random_state=1)
            [["nombre_tm", "nombre_af", "puntaje", "s_nombre", "s_pais", "s_club", "metodo"]]
            .round(2).to_markdown(index=False)]
    return "\n".join(out)


def main():
    tm_raw, af_raw = cargar_tm(), cargar_af()
    if af_raw.empty:
        sys.exit("No hay datos de API-Football todavia")
    tm, af = preparar_tm(tm_raw), preparar_af(af_raw)
    v = vincular(tm, af)
    PROC.mkdir(parents=True, exist_ok=True)
    REPORTES.mkdir(parents=True, exist_ok=True)
    if MUESTRAS:
        v.to_csv(PROC / "vinculos.csv.gz", index=False)
    else:
        v.to_parquet(PROC / "vinculos.parquet", index=False)
    txt = reporte(tm, af, v)
    (REPORTES / "vinculacion.md").write_text(txt, encoding="utf-8")
    print(txt[:4000])


if __name__ == "__main__":
    main()
