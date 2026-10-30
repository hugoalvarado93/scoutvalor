"""
Modulo A: modelo de valor de mercado ("valor estimado") y brecha de infravaloracion.

Metodo:
  - Universo: jugadores activos de Transfermarkt con valor de mercado > 0 y al menos 450 minutos
    en sus dos temporadas mas recientes (sin rendimiento no se estima valor).
  - Objetivo: log(valor de mercado).
  - Variables: edad, posicion, liga (fuerza = valor medio de la liga), club (valor de plantilla),
    meses de contrato restantes, selecciones nacionales, estatura, pie, maximo historico relativo,
    y rendimiento reciente de API-Football (minutos, titularidades, goles/asistencias/pases clave/
    entradas/intercepciones/duelos por 90, calificacion) via la tabla de vinculos.
  - Modelo: HistGradientBoostingRegressor (maneja nulos de forma nativa).
  - Predicciones fuera de muestra con validacion cruzada de 5 particiones: a cada jugador lo
    valora un modelo que NO lo vio en entrenamiento, para que la brecha no este sesgada.
  - Brecha = valor estimado / valor de mercado - 1.

Entradas: pipeline (duckdb + parquet) o MUESTRAS=/ruta (CSV gzip, para desarrollo).
Salidas: data/procesado/valor.parquet|csv.gz y data/reports/modelo_valor.md
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[1]
MUESTRAS = os.getenv("MUESTRAS")
PROC = RAIZ / "data" / "procesado"
REPORTES = RAIZ / "data" / "reports"
HOY = pd.Timestamp(os.getenv("FECHA_CORTE", "2026-10-29"))


def leer(nombre_tm: str = None, af: str = None):
    if MUESTRAS:
        base = Path(MUESTRAS)
        if nombre_tm:
            return pd.read_csv(base / f"tm_{nombre_tm}.csv.gz")
        p = base / f"af_{af}.csv.gz"
        return pd.read_csv(p) if p.exists() else pd.DataFrame()
    if nombre_tm:
        import duckdb
        con = duckdb.connect(str(RAIZ / "data/raw/transfermarkt/transfermarkt-datasets.duckdb"), read_only=True)
        return con.execute(f"SELECT * FROM {nombre_tm}").df()
    return pd.read_parquet(RAIZ / f"data/api_football/parquet/{af}.parquet")


def leer_vinculos() -> pd.DataFrame:
    for p in (PROC / "vinculos.parquet", PROC / "vinculos.csv.gz"):
        if p.exists():
            return pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
    return pd.DataFrame(columns=["player_id", "api_jugador"])


def rendimiento(af: pd.DataFrame) -> pd.DataFrame:
    """Suma de las dos temporadas mas recientes de cada jugador (aprox. ultimos 12-18 meses)."""
    if af.empty:
        return pd.DataFrame()
    num = ["partidos", "titularidades", "minutos", "goles", "asistencias", "pases_clave", "tiros",
           "entradas", "intercepciones", "duelos", "duelos_ganados", "regates_exito", "atajadas",
           "goles_concedidos"]
    af = af.copy()
    for c in num + ["calificacion"]:
        af[c] = pd.to_numeric(af[c], errors="coerce")
    ult = af.groupby("api_jugador").temporada.transform("max")
    af = af[af.temporada >= ult - 1]
    af["cal_x_min"] = af.calificacion * af.minutos.fillna(0)
    g = af.groupby("api_jugador")
    r = g[num].sum(min_count=1)
    # liga donde jugo mas minutos: el contexto real de sus estadisticas
    r["liga_rend"] = af.sort_values("minutos").groupby("api_jugador").api_liga.last()
    r["calificacion"] = g.cal_x_min.sum() / r.minutos.replace(0, np.nan)
    m90 = r.minutos.replace(0, np.nan) / 90
    for c in ["goles", "asistencias", "pases_clave", "tiros", "entradas", "intercepciones", "regates_exito", "atajadas"]:
        r[f"{c}_90"] = r[c] / m90
    r["pct_duelos"] = r.duelos_ganados / r.duelos.replace(0, np.nan)
    r["pct_titular"] = r.titularidades / r.partidos.replace(0, np.nan)
    return r.reset_index()


def construir() -> pd.DataFrame:
    pl = leer("players")
    clubs = leer("clubs")
    comps = leer("competitions")
    pl = pl[(pl.last_season == pl.last_season.max()) & (pl.market_value_in_eur.fillna(0) > 0)].copy()
    pl["edad"] = (HOY - pd.to_datetime(pl.date_of_birth, errors="coerce")).dt.days / 365.25
    pl["meses_contrato"] = (pd.to_datetime(pl.contract_expiration_date, errors="coerce") - HOY).dt.days / 30.4
    pl["log_valor"] = np.log(pl.market_value_in_eur)
    pl["max_relativo"] = np.log(pl.highest_market_value_in_eur / pl.market_value_in_eur)
    liga = pl.groupby("current_club_domestic_competition_id").log_valor.mean().rename("fuerza_liga")
    pl = pl.join(liga, on="current_club_domestic_competition_id")
    clubs["club_id"] = pd.to_numeric(clubs.club_id, errors="coerce")
    pl["current_club_id"] = pd.to_numeric(pl.current_club_id, errors="coerce")
    pl = pl.merge(clubs[["club_id", "total_market_value", "squad_size"]].rename(columns={"club_id": "current_club_id"}),
                  on="current_club_id", how="left")
    pl["valor_plantilla_log"] = np.log1p(pd.to_numeric(pl.total_market_value, errors="coerce"))
    # fuerza de club alternativa (valor medio de jugadores del club) cuando clubs no trae el total
    club_media = pl.groupby("current_club_id").log_valor.transform("mean")
    pl["fuerza_club"] = club_media
    v = leer_vinculos()
    rend = rendimiento(leer(af="jugadores_temporada"))
    if not rend.empty and len(v):
        pl = pl.merge(v[["player_id", "api_jugador"]], on="player_id", how="left").merge(rend, on="api_jugador", how="left")
    pl = pl.merge(comps[["competition_id", "name", "country_name"]].rename(
        columns={"competition_id": "current_club_domestic_competition_id", "name": "liga_nombre", "country_name": "liga_pais"}),
        on="current_club_domestic_competition_id", how="left")
    return pl


CATEG = ["sub_position", "foot", "current_club_domestic_competition_id", "liga_rend"]
NUMER = ["edad", "meses_contrato", "international_caps", "height_in_cm", "max_relativo", "fuerza_liga",
         "fuerza_club", "valor_plantilla_log", "minutos", "partidos", "pct_titular", "calificacion",
         "goles_90", "asistencias_90", "pases_clave_90", "tiros_90", "entradas_90", "intercepciones_90",
         "regates_exito_90", "atajadas_90", "pct_duelos"]


def entrenar(df: pd.DataFrame):
    num = [c for c in NUMER if c in df.columns]
    X = df[num].apply(pd.to_numeric, errors="coerce").copy()
    for c in CATEG:
        X[c] = df[c].astype("category").cat.codes.replace(-1, np.nan)
    X = X.loc[:, X.nunique(dropna=True) >= 2]  # descarta columnas vacias o constantes
    cat_mask = [c in CATEG for c in X.columns]
    y = df.log_valor.values
    pred = np.zeros(len(df))
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    for tr, te in kf.split(X):
        m = HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05, max_leaf_nodes=31,
                                          min_samples_leaf=30, l2_regularization=1.0,
                                          categorical_features=cat_mask, random_state=42)
        m.fit(X.iloc[tr], y[tr])
        pred[te] = m.predict(X.iloc[te])
    return pred, num


def reporte(df: pd.DataFrame, num: list[str]) -> str:
    err = df.pred_log - df.log_valor
    ss_res = (err ** 2).sum()
    ss_tot = ((df.log_valor - df.log_valor.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot
    mae_pct = (np.exp(np.abs(err)) - 1).median() * 100
    base = df.groupby("current_club_domestic_competition_id").log_valor.transform("mean")
    r2_base = 1 - ((base - df.log_valor) ** 2).sum() / ss_tot
    out = ["# Modelo de valor de mercado (modulo A)\n",
           f"- Jugadores: {len(df):,} (con rendimiento de API-Football: {df.minutos.notna().sum():,})",
           f"- Validacion cruzada 5 particiones, predicciones fuera de muestra",
           f"- R2 en log(valor): **{r2:.3f}** (linea base solo-liga: {r2_base:.3f})",
           f"- Error absoluto mediano: **{mae_pct:.1f}%** del valor", "",
           "## Error por liga (top 15 por jugadores)\n"]
    g = df.assign(e=np.abs(err)).groupby("current_club_domestic_competition_id")
    t = pd.DataFrame({"jugadores": g.size(), "error_mediano_pct": ((np.exp(g.e.median()) - 1) * 100).round(1)})
    out.append(t.sort_values("jugadores", ascending=False).head(15).reset_index().to_markdown(index=False))
    out += ["", "## Top 15 infravalorados (todas las ligas, valor >= 500K)\n"]
    top = df[(df.market_value_in_eur >= 5e5) & df.elegible_radar].sort_values("brecha", ascending=False).head(15)
    out.append(top[["name", "current_club_name", "sub_position", "edad", "market_value_in_eur", "valor_estimado", "brecha"]]
               .assign(edad=lambda d: d.edad.round(0), brecha=lambda d: (d.brecha * 100).round(0))
               .to_markdown(index=False))
    return "\n".join(out)


MIN_MODELO = 450   # minutos minimos en las dos ultimas temporadas para estimar valor
MIN_RADAR = 900    # minutos minimos para aparecer en el radar


def main():
    df = construir()
    df = df[pd.to_numeric(df.get("minutos"), errors="coerce").fillna(0) >= MIN_MODELO].reset_index(drop=True)
    pred, num = entrenar(df)
    df["pred_log"] = pred
    # recorte: el modelo no puede estimar mas de 3x ni menos de 1/3 del valor actual
    df["valor_estimado"] = np.exp(np.clip(pred, df.log_valor - np.log(3), df.log_valor + np.log(3))).round(-4)
    df["brecha"] = df.valor_estimado / df.market_value_in_eur - 1
    df["elegible_radar"] = df.minutos >= MIN_RADAR
    PROC.mkdir(parents=True, exist_ok=True)
    REPORTES.mkdir(parents=True, exist_ok=True)
    cols = ["player_id", "valor_estimado", "brecha", "pred_log", "elegible_radar", "edad", "meses_contrato", "api_jugador",
            "minutos", "partidos", "goles", "asistencias", "calificacion", "pases_clave_90", "goles_90",
            "asistencias_90", "entradas_90", "intercepciones_90", "pct_duelos"]
    cols = [c for c in cols if c in df.columns]
    if MUESTRAS:
        df[cols].to_csv(PROC / "valor.csv.gz", index=False)
    else:
        df[cols].to_parquet(PROC / "valor.parquet", index=False)
    txt = reporte(df, num)
    (REPORTES / "modelo_valor.md").write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()
