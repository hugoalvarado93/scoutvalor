"""Funciones compartidas por los analisis academicos de ScoutValor.

Construye los dos conjuntos analiticos del proyecto a partir de las fuentes
originales:
  - valor: un registro por jugador activo (modulo A, valor de mercado).
  - traspasos: un registro por traspaso historico etiquetado (modulo C, exito
    del fichaje).
Lee la base completa (DuckDB de Transfermarkt + parquet de API-Football) o, para
desarrollo, las muestras CSV indicadas en la variable de entorno MUESTRAS.
"""

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
MUESTRAS = os.getenv("MUESTRAS")
SALIDA = RAIZ / "data" / "reports" / "academico"
SALIDA.mkdir(parents=True, exist_ok=True)
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 12)


def modulo(nombre):
    """Importa un script del pipeline (sus nombres empiezan con numero)."""
    spec = importlib.util.spec_from_file_location(
        nombre, RAIZ / "scripts" / f"{nombre}.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = modulo("40_modelo_valor")  # construccion del dataset de valor
C = modulo("60_modulos_bc")  # constantes de idioma, confederacion y posiciones


def tm(tabla):
    """Tabla de Transfermarkt (DuckDB completo o muestra CSV)."""
    if MUESTRAS:
        return pd.read_csv(Path(MUESTRAS) / f"tm_{tabla}.csv.gz")
    import duckdb

    con = duckdb.connect(
        str(RAIZ / "data/raw/transfermarkt/transfermarkt-datasets.duckdb"),
        read_only=True,
    )
    return con.execute(f"SELECT * FROM {tabla}").df()


def titulo(texto):
    print("\n" + "=" * 78 + f"\n{texto}\n" + "=" * 78)


def dataset_valor(minimo=A.MIN_MODELO):
    """Jugadores activos con valor > 0 y al menos `minimo` minutos recientes."""
    df = A.construir()
    df = df[pd.to_numeric(df.get("minutos"), errors="coerce").fillna(0) >= minimo]
    return df.reset_index(drop=True)


def matriz_valor(df):
    """Matriz de factores del modulo A: numericas + categoricas codificadas."""
    num = [c for c in A.NUMER if c in df.columns]
    X = df[num].apply(pd.to_numeric, errors="coerce").copy()
    for c in A.CATEG:
        X[c] = df[c].astype("category").cat.codes.replace(-1, np.nan)
    X = X.loc[:, X.nunique(dropna=True) >= 2]
    # tipos anulables de parquet -> float
    X = X.astype("float64")
    return X, df.log_valor.values.astype(float), [c in A.CATEG for c in X.columns]


def dataset_traspasos():
    """Traspasos historicos con su etiqueta de exito y factores (misma logica que
    el modulo C).
    """
    players, clubs, comps = tm("players"), tm("clubs"), tm("competitions")
    countries, games, apps = tm("countries"), tm("games"), tm("appearances")
    tr, vals = tm("transfers"), tm("player_valuations")
    conf_pais = {
        r.country_name: (
            "CONMEBOL"
            if r.country_name in C.CONMEBOL
            else C.CONF_TM.get(r.confederation)
        )
        for r in countries.itertuples()
    }
    clubs["club_id"] = pd.to_numeric(clubs.club_id, errors="coerce")
    club_liga = dict(zip(clubs.club_id, clubs.domestic_competition_id))
    liga_pais = dict(zip(comps.competition_id, comps.country_name))
    # fuerza de liga y club = log del valor medio de sus jugadores activos
    pl = players[
        (players.last_season == players.last_season.max())
        & (players.market_value_in_eur.fillna(0) > 0)
    ].copy()
    pl["lv"] = np.log(pl.market_value_in_eur)
    f_liga = pl.groupby("current_club_domestic_competition_id").lv.mean().to_dict()
    f_club = (
        pl.groupby(pd.to_numeric(pl.current_club_id, errors="coerce"))
        .lv.mean()
        .to_dict()
    )
    piso_liga = float(np.nanpercentile(list(f_liga.values()), 10))
    piso_club = float(np.nanpercentile(list(f_club.values()), 10))
    # minutos de liga por jugador, club y temporada
    games["season_i"] = pd.to_numeric(games.season, errors="coerce")
    g = games[["game_id", "season_i", "competition_type"]].astype({"game_id": str})
    a = apps.astype({"game_id": str}).merge(g, on="game_id")
    a = a[a.competition_type == "domestic_league"]
    min_pcs = a.groupby(
        ["player_id", "player_club_id", "season_i"]
    ).minutes_played.sum()
    min_ps = a.groupby(["player_id", "season_i"]).minutes_played.sum()
    cub = a.groupby(["competition_id", "season_i"]).size()
    cubiertas = set(cub[cub >= 1000].index)  # liga-temporada con minutos confiables
    ult = int(games.season_i.max())
    nac = dict(zip(players.player_id, players.country_of_citizenship))
    grp = dict(zip(players.player_id, players.sub_position.map(C.POS).map(C.GRUPO)))
    pcs = min_pcs.reset_index().assign(
        nac=lambda d: d.player_id.map(nac), g=lambda d: d.player_id.map(grp)
    )
    compat = (
        pcs[pcs.minutes_played > 0]
        .groupby(["player_club_id", "season_i", "nac"])
        .player_id.nunique()
    )
    compet = (
        pcs[pcs.minutes_played >= 1500]
        .groupby(["player_club_id", "season_i", "g"])
        .player_id.nunique()
    )
    # traspasos a clubes cubiertos, con temporada posterior observable
    tr["transfer_date"] = pd.to_datetime(tr.transfer_date, errors="coerce")
    for c in ["to_club_id", "from_club_id"]:
        tr[c] = pd.to_numeric(tr[c], errors="coerce")
    tr = tr[
        tr.transfer_date.notna()
        & tr.to_club_id.isin(club_liga.keys())
        & (tr.to_club_id != tr.from_club_id)
    ].copy()
    S = tr.transfer_date.map(C.temporada_de)
    verano = tr.transfer_date.dt.month.isin([5, 6, 7, 8, 9])
    tr["S_desp"] = np.where(verano, S, S + 1)
    tr["S_antes"] = np.where(verano, S - 1, S)
    tr["liga_dest"] = tr.to_club_id.map(club_liga)
    tr["liga_orig"] = tr.from_club_id.map(club_liga)
    ok = [(l, s) in cubiertas for l, s in zip(tr.liga_dest, tr.S_desp)]
    tr = tr[np.array(ok) & (tr.S_desp <= ult)].drop_duplicates(
        ["player_id", "transfer_date"]
    )
    # valor al fichar y al cierre de la primera temporada completa
    vals["date"] = pd.to_datetime(vals.date, errors="coerce")
    v = vals.dropna(subset=["date"]).sort_values("date")[
        ["player_id", "date", "market_value_in_eur"]
    ]
    tr = pd.merge_asof(
        tr.sort_values("transfer_date"),
        v.rename(columns={"date": "f0", "market_value_in_eur": "v_en"}),
        left_on="transfer_date",
        right_on="f0",
        by="player_id",
    )
    tr["fin_S"] = pd.to_datetime((tr.S_desp + 1).astype(str) + "-06-30")
    tr = pd.merge_asof(
        tr.sort_values("fin_S"),
        v.rename(columns={"date": "f1", "market_value_in_eur": "v_desp"}),
        left_on="fin_S",
        right_on="f1",
        by="player_id",
    )
    tr = tr[tr.v_en > 0].copy()
    tr["min_desp"] = [
        min_pcs.get((p, c, s), 0)
        for p, c, s in zip(tr.player_id, tr.to_club_id, tr.S_desp)
    ]
    tr["min_antes"] = [
        min_ps.get((p, s), np.nan) for p, s in zip(tr.player_id, tr.S_antes)
    ]
    tr["exito"] = ((tr.min_desp >= 1500) & (tr.v_desp >= 0.9 * tr.v_en)).astype(int)
    born = dict(
        zip(players.player_id, pd.to_datetime(players.date_of_birth, errors="coerce"))
    )
    tr["edad"] = [
        (d - born[p]).days / 365.25 if pd.notna(born.get(p)) else np.nan
        for p, d in zip(tr.player_id, tr.transfer_date)
    ]
    tr["nac"], tr["g"] = tr.player_id.map(nac), tr.player_id.map(grp)
    tr["pais_dest"] = tr.liga_dest.map(liga_pais)
    tr["pais_orig"] = tr.liga_orig.map(liga_pais)
    tr["conf_dest"] = tr.pais_dest.map(conf_pais)
    tr["fee"] = pd.to_numeric(tr.transfer_fee, errors="coerce").fillna(0)
    tr["comp_n"] = [
        compat.get((c, s, n), 0) for c, s, n in zip(tr.to_club_id, tr.S_antes, tr.nac)
    ]
    tr["compet_n"] = [
        compet.get((c, s, gg), 0) for c, s, gg in zip(tr.to_club_id, tr.S_antes, tr.g)
    ]
    tr = tr[tr.edad.notna() & tr.g.notna()].reset_index(drop=True)
    # factores (tabla FEATS del modulo C)
    X = pd.DataFrame(index=tr.index)
    X["edad"], X["edad2"] = tr.edad, (tr.edad - 26) ** 2
    X["log_valor"] = np.log(np.maximum(tr.v_en, 25000))
    X["log_fee"] = np.log1p(tr.fee)
    X["min_antes"] = tr.min_antes.fillna(0) / 1000
    X["sin_min_antes"] = tr.min_antes.isna().astype(float)
    X["f_liga_dest"] = tr.liga_dest.map(f_liga).fillna(piso_liga)
    X["f_liga_orig"] = tr.liga_orig.map(f_liga).fillna(piso_liga)
    X["d_liga"] = X.f_liga_dest - X.f_liga_orig
    X["f_club_dest"] = tr.to_club_id.map(f_club).fillna(piso_club)
    X["f_club_orig"] = tr.from_club_id.map(f_club).fillna(piso_club)
    X["d_club"] = X.f_club_dest - X.f_club_orig
    local = (tr.pais_orig.fillna("?") == tr.pais_dest).values
    idi = np.array([
        C.IDIOMA.get(a) is not None and C.IDIOMA.get(a) == C.IDIOMA.get(b)
        for a, b in zip(tr.nac, tr.pais_dest)
    ])
    cnf = np.array([
        conf_pais.get(a) is not None and conf_pais.get(a) == conf_pais.get(b)
        for a, b in zip(tr.nac, tr.pais_dest)
    ])
    X["mov_local"] = local.astype(float)
    X["mov_idioma"] = (~local & idi).astype(float)
    X["mov_conf"] = (~local & ~idi & cnf).astype(float)
    X["compatriotas"] = np.minimum(tr.comp_n, 5)
    X["competencia"] = np.minimum(tr.compet_n, 4)
    for gg in ["POR", "DEF", "MED", "DEL"]:
        X[f"g_{gg}"] = (tr.g == gg).astype(float)
    return tr, X[C.FEATS]


def estandarizar(X):
    """Imputa con la mediana y estandariza (z) para la regresion logistica."""
    med = X.median()
    Xi = X.fillna(med)
    return ((Xi - Xi.mean()) / Xi.std().replace(0, 1)).values
