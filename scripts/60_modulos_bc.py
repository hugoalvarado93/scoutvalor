"""
Modulos B y C.

Modulo C (simulador de fichaje)
  Unidad: traspaso historico a un club de las ligas cubiertas (Transfermarkt).
  Exito: en su primera temporada completa en el club destino juega >= 1,500 minutos de liga
         y su valor de mercado al cierre de esa temporada es >= 90% del valor al momento del traspaso.
  Variables: edad, valor, monto, minutos de la temporada previa, fuerza de liga y club (origen y destino),
             mismo pais / idioma / confederacion, compatriotas en el club, competencia en su posicion.
  Modelos: regresion logistica (se publica: interpretable y ejecutable en el navegador) y gradient
           boosting (referencia). Validacion cruzada estratificada de 5 particiones (AUC, Brier).

Modulo B (reemplazos por equipo)
  XI de referencia por club: formacion mas usada en sus ultimos partidos y, para cada puesto, el jugador
  del plantel actual con mas minutos en la temporada mas reciente compatible con el puesto.
  Perfiles estadisticos por 90 min estandarizados por grupo de posicion (similitud en el navegador).

Salidas (web/public/data): modelo_c.json, clubes_ctx.json, ligas_ctx.json, xi.json, perfiles.json, pares_ligas.json
Reporte: data/reports/modelo_fichajes.md
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[1]
MUESTRAS = os.getenv("MUESTRAS")
PROC = RAIZ / "data" / "procesado"
REPORTES = RAIZ / "data" / "reports"
OUT = Path(os.getenv("SALIDA_PORTAL", RAIZ / "web" / "public" / "data"))

POS = {"Goalkeeper": "POR", "Centre-Back": "DFC", "Left-Back": "LI", "Right-Back": "LD",
       "Defensive Midfield": "MCD", "Central Midfield": "MC", "Attacking Midfield": "MCO",
       "Left Midfield": "MI", "Right Midfield": "MD", "Left Winger": "EI", "Right Winger": "ED",
       "Second Striker": "SD", "Centre-Forward": "DC"}
GRUPO = {"POR": "POR", "DFC": "DEF", "LI": "DEF", "LD": "DEF", "MCD": "MED", "MC": "MED", "MCO": "MED",
         "MI": "MED", "MD": "MED", "EI": "DEL", "ED": "DEL", "SD": "DEL", "DC": "DEL"}

IDIOMA = {}
for lengua, paises in {
    "es": ["Spain", "Mexico", "Argentina", "Colombia", "Chile", "Uruguay", "Paraguay", "Peru", "Ecuador", "Venezuela",
           "Bolivia", "Costa Rica", "Honduras", "Panama", "Guatemala", "El Salvador", "Cuba", "Dominican Republic",
           "Equatorial Guinea", "Nicaragua", "Puerto Rico"],
    "pt": ["Brazil", "Portugal", "Angola", "Cape Verde", "Mozambique", "Guinea-Bissau", "Sao Tome and Principe"],
    "en": ["England", "Scotland", "Wales", "Northern Ireland", "Ireland", "United States", "Canada", "Australia",
           "New Zealand", "Jamaica", "Nigeria", "Ghana", "South Africa", "Zambia", "Zimbabwe", "Kenya", "Gambia",
           "Sierra Leone", "Liberia", "Trinidad and Tobago", "Uganda", "Tanzania", "Malawi", "Bermuda", "Grenada"],
    "fr": ["France", "Belgium", "Senegal", "Cote d'Ivoire", "Cameroon", "Mali", "Guinea", "DR Congo", "Congo", "Gabon",
           "Burkina Faso", "Benin", "Togo", "Haiti", "Luxembourg", "Morocco", "Algeria", "Tunisia", "Madagascar",
           "Comoros", "Niger", "Chad", "Central African Republic", "Mauritania", "Guadeloupe", "Martinique"],
    "de": ["Germany", "Austria", "Switzerland", "Liechtenstein"],
    "it": ["Italy", "San Marino"],
    "nl": ["Netherlands", "Suriname", "Curacao", "Aruba"],
    "ar": ["Saudi Arabia", "Egypt", "Qatar", "Iraq", "United Arab Emirates", "Jordan", "Syria", "Lebanon", "Libya",
           "Kuwait", "Bahrain", "Oman", "Palestine", "Yemen", "Sudan"],
    "ru": ["Russia", "Belarus", "Kazakhstan", "Kyrgyzstan"],
    "uk": ["Ukraine"], "sh": ["Serbia", "Croatia", "Bosnia-Herzegovina", "Montenegro"],
    "tr": ["Türkiye", "Turkey"], "el": ["Greece", "Cyprus"], "pl": ["Poland"], "cs": ["Czech Republic"], "sk": ["Slovakia"],
    "ro": ["Romania", "Moldova"], "da": ["Denmark"], "no": ["Norway"], "sv": ["Sweden"], "ja": ["Japan"],
    "ko": ["Korea, South"], "hu": ["Hungary"], "bg": ["Bulgaria"], "sl": ["Slovenia"], "sq": ["Albania", "Kosovo"],
    "mk": ["North Macedonia"], "ka": ["Georgia"], "hy": ["Armenia"], "he": ["Israel"], "fa": ["Iran"],
    "zh": ["China"], "fi": ["Finland"], "is": ["Iceland"], "uz": ["Uzbekistan"], "az": ["Azerbaijan"],
    "lt": ["Lithuania"], "lv": ["Latvia"], "et": ["Estonia"],
}.items():
    for p in paises:
        IDIOMA[p] = lengua

CONMEBOL = {"Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Paraguay", "Peru", "Uruguay", "Venezuela"}
CONF_TM = {"europa": "UEFA", "afrika": "CAF", "asien": "AFC", "ozeanien": "OFC", "amerika": "CONCACAF"}

FEATS = ["edad", "edad2", "log_valor", "log_fee", "min_antes", "sin_min_antes",
         "f_liga_dest", "f_liga_orig", "d_liga", "f_club_dest", "f_club_orig", "d_club",
         "mov_local", "mov_idioma", "mov_conf", "compatriotas", "competencia",
         "g_POR", "g_DEF", "g_MED", "g_DEL"]
# Tipo de movimiento (excluyente; la categoria base es "otro idioma y otra confederacion"):
#   mov_local  = mismo pais de liga origen y destino
#   mov_idioma = cambia de pais y el idioma de su nacionalidad es el del pais destino
#   mov_conf   = cambia de pais, otro idioma, pero misma confederacion

# Plantillas de formacion: (puesto, x%, y%) con ataque hacia arriba
F = {
    "4-2-3-1": [("POR", 50, 91), ("LI", 13, 70), ("DFC", 37, 75), ("DFC", 63, 75), ("LD", 87, 70), ("MCD", 36, 53),
                ("MCD", 64, 53), ("EI", 17, 29), ("MCO", 50, 33), ("ED", 83, 29), ("DC", 50, 10)],
    "4-3-3": [("POR", 50, 91), ("LI", 13, 70), ("DFC", 37, 75), ("DFC", 63, 75), ("LD", 87, 70), ("MC", 28, 47),
              ("MCD", 50, 55), ("MC", 72, 47), ("EI", 18, 22), ("DC", 50, 12), ("ED", 82, 22)],
    "4-4-2": [("POR", 50, 91), ("LI", 13, 70), ("DFC", 37, 75), ("DFC", 63, 75), ("LD", 87, 70), ("MI", 13, 44),
              ("MC", 38, 49), ("MC", 62, 49), ("MD", 87, 44), ("DC", 38, 14), ("DC", 62, 14)],
    "4-1-4-1": [("POR", 50, 91), ("LI", 13, 70), ("DFC", 37, 75), ("DFC", 63, 75), ("LD", 87, 70), ("MCD", 50, 57),
                ("MI", 13, 37), ("MC", 38, 40), ("MC", 62, 40), ("MD", 87, 37), ("DC", 50, 12)],
    "4-4-1-1": [("POR", 50, 91), ("LI", 13, 70), ("DFC", 37, 75), ("DFC", 63, 75), ("LD", 87, 70), ("MI", 13, 46),
                ("MC", 38, 51), ("MC", 62, 51), ("MD", 87, 46), ("MCO", 50, 30), ("DC", 50, 11)],
    "4-3-1-2": [("POR", 50, 91), ("LI", 13, 70), ("DFC", 37, 75), ("DFC", 63, 75), ("LD", 87, 70), ("MC", 26, 51),
                ("MCD", 50, 57), ("MC", 74, 51), ("MCO", 50, 34), ("DC", 38, 13), ("DC", 62, 13)],
    "3-5-2": [("POR", 50, 91), ("DFC", 28, 74), ("DFC", 50, 77), ("DFC", 72, 74), ("MI", 10, 45), ("MC", 32, 48),
              ("MCD", 50, 56), ("MC", 68, 48), ("MD", 90, 45), ("DC", 38, 14), ("DC", 62, 14)],
    "3-4-3": [("POR", 50, 91), ("DFC", 28, 74), ("DFC", 50, 77), ("DFC", 72, 74), ("MI", 12, 46), ("MC", 38, 50),
              ("MC", 62, 50), ("MD", 88, 46), ("EI", 18, 20), ("DC", 50, 12), ("ED", 82, 20)],
    "3-4-2-1": [("POR", 50, 91), ("DFC", 28, 74), ("DFC", 50, 77), ("DFC", 72, 74), ("MI", 12, 48), ("MC", 38, 53),
                ("MC", 62, 53), ("MD", 88, 48), ("MCO", 34, 29), ("MCO", 66, 29), ("DC", 50, 11)],
    "5-3-2": [("POR", 50, 91), ("LI", 10, 63), ("DFC", 30, 75), ("DFC", 50, 78), ("DFC", 70, 75), ("LD", 90, 63),
              ("MC", 28, 45), ("MCD", 50, 51), ("MC", 72, 45), ("DC", 38, 14), ("DC", 62, 14)],
    "5-4-1": [("POR", 50, 91), ("LI", 10, 63), ("DFC", 30, 75), ("DFC", 50, 78), ("DFC", 70, 75), ("LD", 90, 63),
              ("MI", 14, 40), ("MC", 38, 44), ("MC", 62, 44), ("MD", 86, 40), ("DC", 50, 12)],
}
COMPAT = {"POR": ["POR"], "LI": ["LI", "MI", "DFC"], "LD": ["LD", "MD", "DFC"], "DFC": ["DFC", "MCD", "LI", "LD"],
          "MCD": ["MCD", "MC", "DFC"], "MC": ["MC", "MCD", "MCO"], "MCO": ["MCO", "MC", "SD", "EI", "ED"],
          "MI": ["MI", "EI", "LI", "MC"], "MD": ["MD", "ED", "LD", "MC"], "EI": ["EI", "MI", "MCO", "ED", "DC"],
          "ED": ["ED", "MD", "MCO", "EI", "DC"], "DC": ["DC", "SD", "EI", "ED", "MCO"]}


def tm(nombre):
    if MUESTRAS:
        return pd.read_csv(Path(MUESTRAS) / f"tm_{nombre}.csv.gz")
    import duckdb
    con = duckdb.connect(str(RAIZ / "data/raw/transfermarkt/transfermarkt-datasets.duckdb"), read_only=True)
    return con.execute(f"SELECT * FROM {nombre}").df()


def proc(nombre):
    for p in (PROC / f"{nombre}.parquet", PROC / f"{nombre}.csv.gz"):
        if p.exists():
            return pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
    return pd.DataFrame()


def escribir(nombre, obj):
    p = OUT / nombre
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return p.stat().st_size


def norm_formacion(s):
    if not isinstance(s, str):
        return None
    base = s.split(" ")[0]
    alias = {"4-4-2": "4-4-2", "4-1-3-2": "4-3-1-2", "3-4-1-2": "3-5-2", "3-1-4-2": "3-5-2", "4-5-1": "4-1-4-1",
             "4-2-2-2": "4-4-2", "4-3-2-1": "4-3-3", "5-2-3": "3-4-3", "3-5-1-1": "3-5-2", "4-2-4": "4-3-3"}
    base = alias.get(base, base)
    return base if base in F else None


def temporada_de(fecha):
    """Temporada (anio de inicio, convencion Transfermarkt) a la que corresponde una fecha."""
    return fecha.year if fecha.month >= 7 else fecha.year - 1


def main():
    players = tm("players")
    clubs = tm("clubs")
    comps = tm("competitions")
    countries = tm("countries")
    games = tm("games")
    apps = tm("appearances")
    transfers = tm("transfers")
    vals = tm("player_valuations")
    jug = json.loads((OUT / "jugadores.json").read_text(encoding="utf-8"))
    act = pd.DataFrame(jug)
    valor = proc("valor")

    conf_pais = {r.country_name: ("CONMEBOL" if r.country_name in CONMEBOL else CONF_TM.get(r.confederation))
                 for r in countries.itertuples()}
    clubs["club_id"] = pd.to_numeric(clubs.club_id, errors="coerce")
    club_liga = dict(zip(clubs.club_id, clubs.domestic_competition_id))
    liga_pais = dict(zip(comps.competition_id, comps.country_name))

    # ---------- fuerzas (log valor medio de jugadores activos)
    pl = players[players.last_season == players.last_season.max()].copy()
    pl = pl[pl.market_value_in_eur.fillna(0) > 0]
    pl["lv"] = np.log(pl.market_value_in_eur)
    pl["current_club_id"] = pd.to_numeric(pl.current_club_id, errors="coerce")
    f_liga = pl.groupby("current_club_domestic_competition_id").lv.mean().to_dict()
    f_club = pl.groupby("current_club_id").lv.mean().to_dict()
    piso_liga = float(np.nanpercentile(list(f_liga.values()), 10))
    piso_club = float(np.nanpercentile(list(f_club.values()), 10))

    # ---------- minutos por jugador / club / temporada
    games["season_i"] = pd.to_numeric(games.season, errors="coerce")
    gs = games[["game_id", "season_i", "competition_type"]].copy()
    gs["game_id"] = gs.game_id.astype(str)
    apps["game_id"] = apps.game_id.astype(str)
    a = apps.merge(gs, on="game_id", how="inner")
    a = a[a.competition_type == "domestic_league"]
    min_pcs = a.groupby(["player_id", "player_club_id", "season_i"]).minutes_played.sum()
    min_ps = a.groupby(["player_id", "season_i"]).minutes_played.sum()
    # liga-temporada con minutos por partido disponibles (Transfermarkt no los tiene para todas las ligas)
    cub = a.groupby(["competition_id", "season_i"]).size()
    cubiertas = set(cub[cub >= 1000].index)
    ult_temp = int(games.season_i.max())

    nac = dict(zip(players.player_id, players.country_of_citizenship))
    grp = dict(zip(players.player_id, players.sub_position.map(POS).map(GRUPO)))
    pcs = min_pcs.reset_index()
    pcs["nac"] = pcs.player_id.map(nac)
    pcs["g"] = pcs.player_id.map(grp)
    compat = pcs[pcs.minutes_played > 0].groupby(["player_club_id", "season_i", "nac"]).player_id.nunique()
    compet = pcs[pcs.minutes_played >= 1500].groupby(["player_club_id", "season_i", "g"]).player_id.nunique()

    # ---------- traspasos etiquetados
    tr = transfers.copy()
    tr["transfer_date"] = pd.to_datetime(tr.transfer_date, errors="coerce")
    tr["to_club_id"] = pd.to_numeric(tr.to_club_id, errors="coerce")
    tr["from_club_id"] = pd.to_numeric(tr.from_club_id, errors="coerce")
    tr = tr[tr.transfer_date.notna() & tr.to_club_id.isin(club_liga.keys()) & (tr.to_club_id != tr.from_club_id)]
    tr["S"] = tr.transfer_date.map(temporada_de)
    todos = tr.assign(lo=tr.from_club_id.map(club_liga), ld=tr.to_club_id.map(club_liga))
    todos = todos[todos.lo.notna() & (todos.transfer_date >= "2017-07-01")]
    verano = tr.transfer_date.dt.month.isin([5, 6, 7, 8, 9])
    tr["S_desp"] = np.where(verano, tr.S, tr.S + 1)
    tr["S_antes"] = np.where(verano, tr.S - 1, tr.S)
    tr["liga_dest"] = tr.to_club_id.map(club_liga)
    tr["liga_orig"] = tr.from_club_id.map(club_liga)
    tr = tr[np.array([(l, s) in cubiertas for l, s in zip(tr.liga_dest, tr.S_desp)]) & (tr.S_desp <= ult_temp).values]
    tr = tr.drop_duplicates(["player_id", "transfer_date"])

    vals["date"] = pd.to_datetime(vals.date, errors="coerce")
    vals = vals.dropna(subset=["date"]).sort_values("date")
    tr = tr.sort_values("transfer_date")
    tr = pd.merge_asof(tr, vals[["player_id", "date", "market_value_in_eur"]].rename(columns={"date": "f_val", "market_value_in_eur": "v_en"}),
                       left_on="transfer_date", right_on="f_val", by="player_id", direction="backward")
    tr["fin_S"] = pd.to_datetime((tr.S_desp + 1).astype(str) + "-06-30")
    tr = tr.sort_values("fin_S")
    tr = pd.merge_asof(tr, vals[["player_id", "date", "market_value_in_eur"]].rename(columns={"date": "f_val2", "market_value_in_eur": "v_desp"}),
                       left_on="fin_S", right_on="f_val2", by="player_id", direction="backward")
    tr = tr[tr.v_en.notna() & (tr.v_en > 0)]
    tr["min_desp"] = [min_pcs.get((p, c, s), 0) for p, c, s in zip(tr.player_id, tr.to_club_id, tr.S_desp)]
    tr["min_antes_raw"] = [min_ps.get((p, s), np.nan) for p, s in zip(tr.player_id, tr.S_antes)]
    tr["exito"] = ((tr.min_desp >= 1500) & (tr.v_desp >= 0.9 * tr.v_en)).astype(int)

    born = dict(zip(players.player_id, pd.to_datetime(players.date_of_birth, errors="coerce")))
    tr["edad"] = [(d - born.get(p)).days / 365.25 if pd.notna(born.get(p)) else np.nan for p, d in zip(tr.player_id, tr.transfer_date)]
    tr["nac"] = tr.player_id.map(nac)
    tr["g"] = tr.player_id.map(grp)
    tr["pais_dest"] = tr.liga_dest.map(liga_pais)
    tr["pais_orig"] = tr.liga_orig.map(liga_pais)
    tr["fee"] = pd.to_numeric(tr.transfer_fee, errors="coerce").fillna(0)
    tr["comp_n"] = [compat.get((c, s, n), 0) for c, s, n in zip(tr.to_club_id, tr.S_antes, tr.nac)]
    tr["compet_n"] = [compet.get((c, s, g), 0) for c, s, g in zip(tr.to_club_id, tr.S_antes, tr.g)]

    def features(d):
        X = pd.DataFrame(index=d.index)
        X["edad"] = d.edad
        X["edad2"] = (d.edad - 26) ** 2
        X["log_valor"] = np.log(np.maximum(d.valor, 25000))
        X["log_fee"] = np.log1p(d.fee)
        X["min_antes"] = d.min_antes.fillna(0) / 1000
        X["sin_min_antes"] = d.min_antes.isna().astype(float)
        X["f_liga_dest"] = d.liga_dest.map(f_liga).fillna(piso_liga)
        X["f_liga_orig"] = d.liga_orig.map(f_liga).fillna(piso_liga)
        X["d_liga"] = X.f_liga_dest - X.f_liga_orig
        X["f_club_dest"] = d.club_dest.map(f_club).fillna(piso_club)
        X["f_club_orig"] = d.club_orig.map(f_club).fillna(piso_club)
        X["d_club"] = X.f_club_dest - X.f_club_orig
        local = (d.pais_orig.fillna("?") == d.pais_dest).values
        idi = np.array([IDIOMA.get(a) is not None and IDIOMA.get(a) == IDIOMA.get(b) for a, b in zip(d.nac, d.pais_dest)])
        cnf = np.array([conf_pais.get(a) is not None and conf_pais.get(a) == conf_pais.get(b) for a, b in zip(d.nac, d.pais_dest)])
        X["mov_local"] = local.astype(float)
        X["mov_idioma"] = (~local & idi).astype(float)
        X["mov_conf"] = (~local & ~idi & cnf).astype(float)
        X["compatriotas"] = np.minimum(d.comp_n, 5)
        X["competencia"] = np.minimum(d.compet_n, 4)
        for g in ["POR", "DEF", "MED", "DEL"]:
            X[f"g_{g}"] = (d.g == g).astype(float)
        return X[FEATS]

    d = tr.rename(columns={"v_en": "valor", "min_antes_raw": "min_antes", "to_club_id": "club_dest", "from_club_id": "club_orig"})
    d = d[d.edad.notna() & d.g.notna()]
    X = features(d)
    y = d.exito.values
    print(f"Traspasos etiquetados: {len(d):,} | tasa de exito {y.mean():.3f}")

    med = X.median()
    mu = X.fillna(med).mean()
    sd = X.fillna(med).std().replace(0, 1)
    Z = ((X.fillna(med) - mu) / sd).values
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    p_lr = np.zeros(len(y)); p_gb = np.zeros(len(y))
    for tr_i, te_i in skf.split(Z, y):
        lr = LogisticRegression(C=0.5, max_iter=2000).fit(Z[tr_i], y[tr_i])
        p_lr[te_i] = lr.predict_proba(Z[te_i])[:, 1]
        gb = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05, min_samples_leaf=40, random_state=7).fit(X.values[tr_i], y[tr_i])
        p_gb[te_i] = gb.predict_proba(X.values[te_i])[:, 1]
    lr = LogisticRegression(C=0.5, max_iter=2000).fit(Z, y)
    auc_lr, auc_gb = roc_auc_score(y, p_lr), roc_auc_score(y, p_gb)
    bri_lr, bri_gb = brier_score_loss(y, p_lr), brier_score_loss(y, p_gb)
    print(f"AUC logistica {auc_lr:.3f} | AUC gradient boosting {auc_gb:.3f}")

    # calibracion por deciles (logistica)
    cal = pd.DataFrame({"p": p_lr, "y": y})
    cal["dec"] = pd.qcut(cal.p, 10, labels=False, duplicates="drop")
    cal_t = cal.groupby("dec").agg(prob_media=("p", "mean"), tasa_real=("y", "mean"), n=("y", "size")).round(3)

    # pares de ligas (movimientos comparables)
    # pares de ligas: [traspasos desde 2017, tasa de exito (si hay >= 8 etiquetados) , serie por temporada]
    cnt = todos.groupby(["lo", "ld"]).size()
    tasa = d.groupby(["liga_orig", "liga_dest"]).exito.agg(["size", "mean"])
    serie = todos.groupby(["lo", "ld", "S"]).size()
    pares_json = {}
    for (o, de), n in cnt.items():
        if n < 3:
            continue
        r = tasa.loc[(o, de)] if (o, de) in tasa.index else None
        tx = round(float(r["mean"]), 3) if r is not None and r["size"] >= 8 else None
        s = serie.loc[(o, de)]
        pares_json[f"{o}>{de}"] = [int(n), tx, {str(int(a)): int(b) for a, b in s.items()}]
    pares = tasa.reset_index()

    modelo = {"feats": FEATS, "coef": [round(float(c), 5) for c in lr.coef_[0]], "intercepto": round(float(lr.intercept_[0]), 5),
              "media": [round(float(mu[f]), 5) for f in FEATS], "desv": [round(float(sd[f]), 5) for f in FEATS],
              "mediana": [round(float(med[f]), 5) for f in FEATS], "tasa_base": round(float(y.mean()), 4),
              "auc": round(float(auc_lr), 3), "auc_gb": round(float(auc_gb), 3), "n": int(len(y)),
              "piso_liga": round(piso_liga, 4), "piso_club": round(piso_club, 4),
              "idioma": IDIOMA, "conf": {k: v for k, v in conf_pais.items() if v}}

    # ---------- contexto de clubes y ligas para inferencia
    act["g"] = act.p.map(GRUPO)
    min_ult = min_ps.xs(ult_temp, level="season_i") if ult_temp in min_ps.index.get_level_values(1) else pd.Series(dtype=float)
    act["m_ult"] = act.id.map(min_ult)
    vinc = proc("vinculos")
    if MUESTRAS:
        afj = pd.read_csv(Path(MUESTRAS) / "af_jugadores_temporada.csv.gz")
    else:
        pa = RAIZ / "data/api_football/parquet/jugadores_temporada.parquet"
        afj = pd.read_parquet(pa) if pa.exists() else pd.DataFrame()
    if len(afj) and len(vinc):
        afj["minutos"] = pd.to_numeric(afj.minutos, errors="coerce")
        ult_af = afj.groupby("api_jugador").temporada.transform("max")
        m_af = afj[afj.temporada == ult_af].groupby("api_jugador").minutos.sum()
        m_af = vinc.set_index("player_id").api_jugador.map(m_af)
        act["m_ult"] = act.m_ult.fillna(act.id.map(m_af))
    act["m_ult"] = act.m_ult.fillna(0)
    min_ult = act.set_index("id").m_ult
    ref_fee = tr[tr.fee > 0].groupby("to_club_id").fee.quantile(0.9)
    clubes_ctx = {}
    for cid, sq in act[act.cl.notna()].groupby("cl"):
        cid = int(cid)
        lg = club_liga.get(cid)
        clubes_ctx[cid] = {
            "lg": lg, "pais": liga_pais.get(lg), "f": round(float(f_club.get(cid, piso_club)), 4),
            "nac": {k: int(v) for k, v in sq.nac.value_counts().items() if k},
            "comp": {k: int(v) for k, v in sq[sq.m_ult >= 1500].g.value_counts().items()},
            "ref": int(ref_fee.get(cid, 0) or (np.nanpercentile(sq.v.dropna(), 90) if sq.v.notna().any() else 0)),
        }
    ligas_ctx = {k: round(float(v), 4) for k, v in f_liga.items() if isinstance(k, str)}

    # ---------- XI de referencia
    games["date"] = pd.to_datetime(games.date, errors="coerce")
    gr = games.sort_values("date")
    form_rows = pd.concat([
        gr[["date", "home_club_id", "home_club_formation"]].rename(columns={"home_club_id": "club", "home_club_formation": "f"}),
        gr[["date", "away_club_id", "away_club_formation"]].rename(columns={"away_club_id": "club", "away_club_formation": "f"})])
    form_rows["f"] = form_rows.f.map(norm_formacion)
    form_rows = form_rows.dropna(subset=["f"]).sort_values("date").groupby("club").tail(15)
    formacion = form_rows.groupby("club").f.agg(lambda s: s.value_counts().index[0]).to_dict()
    xi = {}
    for cid, sq in act[act.cl.notna()].groupby("cl"):
        cid = int(cid)
        f = formacion.get(cid, "4-2-3-1")
        pool = sq.sort_values("m_ult", ascending=False)
        usados, slots = set(), []
        for puesto, x, yy in F[f]:
            elegido = None
            for pref in COMPAT[puesto]:
                cand = pool[(pool.p == pref) & ~pool.id.isin(usados)]
                if len(cand):
                    elegido = int(cand.iloc[0].id)
                    break
            if elegido:
                usados.add(elegido)
            slots.append([puesto, x, yy, elegido])
        xi[cid] = {"f": f, "s": slots}

    # ---------- perfiles estadisticos estandarizados por grupo
    dims = ["goles_90", "asistencias_90", "pases_clave_90", "tiros_90", "regates_exito_90", "entradas_90",
            "intercepciones_90", "pct_duelos", "calificacion", "atajadas_90"]
    perf = {"dims": dims, "id": [], "z": [], "q": []}
    if len(valor):
        v = valor.copy()
        v["g"] = v.sub_position.map(POS).map(GRUPO) if "sub_position" in v else np.nan
        v = v[v.minutos.fillna(0) >= 900]
        for g, sub in v.groupby("g"):
            M = sub[[c for c in dims if c in sub.columns]].apply(pd.to_numeric, errors="coerce")
            M = M.fillna(M.median())
            Zg = ((M - M.mean()) / M.std().replace(0, 1)).clip(-3, 3).round(2)
            q = (sub.calificacion.rank(pct=True) * 100).round(0)
            perf["id"] += sub.player_id.astype(int).tolist()
            perf["z"] += Zg.values.tolist()
            perf["q"] += q.fillna(50).astype(int).tolist()

    # comportamiento de factores para el reporte
    coef = pd.DataFrame({"variable": FEATS, "coef_estandarizado": lr.coef_[0].round(3)}).sort_values("coef_estandarizado")
    REPORTES.mkdir(parents=True, exist_ok=True)
    rep = ["# Modelo de exito de fichajes (modulo C)\n",
           f"- Traspasos etiquetados: {len(y):,} (temporadas destino {int(d.S_desp.min())}-{int(d.S_desp.max())})",
           f"- Tasa base de exito: {y.mean():.1%}",
           "- Exito = >= 1,500 min de liga en la primera temporada completa y valor >= 90% del valor al fichar",
           f"- Regresion logistica (publicada): AUC {auc_lr:.3f}, Brier {bri_lr:.3f}",
           f"- Gradient boosting (referencia): AUC {auc_gb:.3f}, Brier {bri_gb:.3f}", "",
           "## Coeficientes estandarizados (logistica)\n", coef.to_markdown(index=False), "",
           "## Calibracion por deciles (logistica, fuera de muestra)\n", cal_t.reset_index().to_markdown(index=False), "",
           "## Pares de ligas con mas traspasos\n",
           pares.sort_values("size", ascending=False).head(20).rename(columns={"size": "traspasos", "mean": "tasa_exito"}).round(3).to_markdown(index=False)]
    (REPORTES / "modelo_fichajes.md").write_text("\n".join(rep), encoding="utf-8")

    tam = {"modelo_c.json": escribir("modelo_c.json", modelo), "clubes_ctx.json": escribir("clubes_ctx.json", clubes_ctx),
           "ligas_ctx.json": escribir("ligas_ctx.json", ligas_ctx), "xi.json": escribir("xi.json", xi),
           "perfiles.json": escribir("perfiles.json", perf), "pares_ligas.json": escribir("pares_ligas.json", pares_json),
           "min_ult.json": escribir("min_ult.json", {str(int(k)): int(v) for k, v in min_ult.items() if v > 0 and int(k) in set(act.id)})}
    for k, v in tam.items():
        print(f"{k}: {v/1e6:.2f} MB")
    print("\n".join(rep[:7]))


if __name__ == "__main__":
    main()
