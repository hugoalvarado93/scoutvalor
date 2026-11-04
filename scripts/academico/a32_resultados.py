"""Actividad 3.2: interpretabilidad, prueba de hipotesis, retroprueba del radar
y contraste externo.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict

import comun as c

VEREDICTO = []
hgb = lambda cat: HistGradientBoostingRegressor(
    max_iter=600,
    learning_rate=0.05,
    min_samples_leaf=30,
    l2_regularization=1.0,
    categorical_features=cat,
    random_state=42,
)

# 1. H1: que explica el valor de mercado ---------------------------------------
c.titulo("1. H1: importancia por permutacion (caida de R2) y dependencia parcial")
va = c.dataset_valor()
X, y, cat = c.matriz_valor(va)
pred = cross_val_predict(hgb(cat), X, y, cv=KFold(5, shuffle=True, random_state=42))
r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
idx = np.random.RandomState(1).permutation(len(X))
k = int(len(X) * 0.8)
m = hgb(cat).fit(X.iloc[idx[:k]], y[idx[:k]])
pi = permutation_importance(
    m, X.iloc[idx[k:]], y[idx[k:]], n_repeats=5, random_state=1, scoring="r2"
)
imp = pd.Series(pi.importances_mean, X.columns)
grupos = pd.Series(
    {g: imp.reindex(cs).fillna(0).sum() for g, cs in c.A.GRUPOS_VAR.items()}
).sort_values(ascending=False)
print(grupos.round(3).to_string())
for var, rejilla in [
    ("edad", [19, 22, 25, 28, 31, 34]),
    ("meses_contrato", [3, 12, 24, 36, 48, 60]),
]:
    Xp, prom = X.iloc[idx[k:]].copy(), []
    # dependencia parcial: fija la variable y
    # promedia la prediccion
    for val in rejilla:
        Xp[var] = val
        prom.append(m.predict(Xp).mean())
    ef = np.exp(np.array(prom) - prom[0])
    print(
        f"Dependencia parcial de {var} (x valor vs {rejilla[0]}): "
        + " | ".join(f"{g}: x{e:.2f}" for g, e in zip(rejilla, ef))
    )
VEREDICTO.append(["H1", "R2 fuera de muestra >= 0.75", f"{r2:.3f}", r2 >= 0.75])

# 2. H2 y H3: modelo de exito y efecto del tipo de movimiento ------------------
c.titulo("2. H2 y H3: razones de momios (OR) con intervalo bootstrap al 95%")
tr, XT = c.dataset_traspasos()
Z, yt = c.estandarizar(XT), tr.exito.values
sd = XT.fillna(XT.median()).std().replace(0, 1).values
p = cross_val_predict(
    LogisticRegression(C=0.5, max_iter=2000),
    Z,
    yt,
    cv=StratifiedKFold(5, shuffle=True, random_state=7),
    method="predict_proba",
)[:, 1]
auc = roc_auc_score(yt, p)
VEREDICTO.append(["H2", "AUC fuera de muestra >= 0.70", f"{auc:.3f}", auc >= 0.70])
clave = [
    "mov_local",
    "mov_idioma",
    "mov_conf",
    "compatriotas",
    "log_fee",
    "d_liga",
    "min_antes",
    "edad",
]
pos = [c.C.FEATS.index(v) for v in clave]
rng, boots = np.random.default_rng(3), []
for _ in range(200):
    s = rng.integers(0, len(yt), len(yt))
    boots.append(
        LogisticRegression(C=0.5, max_iter=2000).fit(Z[s], yt[s]).coef_[0][pos]
        / sd[pos]
    )
boots = np.array(boots)
orr = pd.DataFrame(
    {
        "OR": np.exp(np.median(boots, 0)),
        "IC_inf": np.exp(np.percentile(boots, 2.5, 0)),
        "IC_sup": np.exp(np.percentile(boots, 97.5, 0)),
    },
    index=clave,
)
orr["unidad"] = [
    "si/no",
    "si/no",
    "si/no",
    "+1 compatriota",
    "+1 log(monto)",
    "+1 log fuerza",
    "+1000 min",
    "+1 ano",
]
print(orr.round(3).to_string())
# emparejamiento por estratos: mismo idioma vs otro idioma y confederacion,
# comparando dentro de estratos
d = tr.assign(
    mov=np.select(
        [XT.mov_local == 1, XT.mov_idioma == 1, XT.mov_conf == 1],
        ["local", "idioma", "conf"],
        "otro",
    )
)
d = d[d.mov.isin(["idioma", "otro"])].copy()
d["estrato"] = (
    pd.qcut(XT.loc[d.index, "d_liga"], 3, labels=False, duplicates="drop").astype(str)
    + d.g.astype(str)
    + pd.cut(d.edad, [0, 23, 28, 99], labels=False).astype(str)
    + pd.qcut(np.log(d.v_en), 3, labels=False, duplicates="drop").astype(str)
)
t = d.groupby(["estrato", "mov"]).exito.agg(["mean", "size"]).unstack()
t = t[(t["size"] >= 5).all(axis=1)]
efecto = np.average(
    t["mean"]["idioma"] - t["mean"]["otro"], weights=t["size"]["idioma"]
)
print(
    f"Emparejamiento por {len(t)} estratos: efecto de mismo idioma sobre la tasa de"
    f" exito {efecto * 100:+.1f} puntos"
)
VEREDICTO.append([
    "H3",
    "OR mismo idioma > 1 con IC sin cruzar 1",
    (
        f"{orr.loc['mov_idioma', 'OR']:.2f} [{orr.loc['mov_idioma', 'IC_inf']:.2f},"
        f" {orr.loc['mov_idioma', 'IC_sup']:.2f}]"
    ),
    orr.loc["mov_idioma", "IC_inf"] > 1,
])

# 3. H4: regla prescriptiva (elegir por probabilidad, dentro del presupuesto) --
c.titulo(
    "3. H4: tasa de exito por quintil de probabilidad estimada (elevacion sobre la"
    " tasa base)"
)
q = pd.qcut(p, 5, labels=["Q1 (baja)", "Q2", "Q3", "Q4", "Q5 (alta)"])
lift = (
    pd.DataFrame({"q": q, "y": yt})
    .groupby("q", observed=True)
    .y.agg(traspasos="size", tasa_exito="mean")
)
lift["elevacion"] = lift.tasa_exito / yt.mean()
print(lift.round(3).to_string())
barato = tr.fee.values <= np.percentile(tr.fee[tr.fee > 0], 50)
sel = barato & (p >= np.quantile(p[barato], 0.8))
print(
    f"Con presupuesto bajo (monto <= mediana): tasa base {yt[barato].mean():.3f},"
    f" regla top 20% {yt[sel].mean():.3f}"
)
VEREDICTO.append([
    "H4",
    "Elevacion del quintil superior >= 1.5",
    f"{lift.elevacion.iloc[-1]:.2f}",
    lift.elevacion.iloc[-1] >= 1.5,
])

# 4. H5: retroprueba del radar con corte en julio de 2024 ----------------------
c.titulo(
    "4. H5: retroprueba del radar (valor a jul-2024, desempeno 2023/24, cambio a"
    " jul-2025)"
)
t0, t1 = pd.Timestamp("2024-07-01"), pd.Timestamp("2025-07-01")
v = c.tm("player_valuations")
v["date"] = pd.to_datetime(v.date, errors="coerce")
v0 = (
    v[(v.date <= t0) & (v.date > t0 - pd.Timedelta(days=183))]
    .sort_values("date")
    .groupby("player_id")
    .last()
)
v1 = (
    v[(v.date > t0 + pd.Timedelta(days=150)) & (v.date <= t1)]
    .sort_values("date")
    .groupby("player_id")
    .market_value_in_eur.last()
)
apps, games = c.tm("appearances"), c.tm("games")
g = games[["game_id", "season", "competition_type"]].astype({"game_id": str})
a = apps.astype({"game_id": str}).merge(g, on="game_id")
a = a[(a.competition_type == "domestic_league") & (pd.to_numeric(a.season) == 2023)]
perf = a.groupby("player_id").agg(
    min=("minutes_played", "sum"),
    pj=("game_id", "nunique"),
    gol=("goals", "sum"),
    asi=("assists", "sum"),
)
pl = c.tm("players").set_index("player_id")
b = v0.join(perf, how="inner").join(v1.rename("v1"), how="inner")
b = b[(b["min"] >= 450) & (b.market_value_in_eur > 0)].copy()
b["edad"] = (
    t0 - pd.to_datetime(pl.date_of_birth.reindex(b.index), errors="coerce")
).dt.days / 365.25
b["lv0"] = np.log(b.market_value_in_eur)
b["f_liga"] = b.groupby("player_club_domestic_competition_id").lv0.transform("mean")
b["f_club"] = b.groupby("current_club_id").lv0.transform("mean")
b["gol90"], b["asi90"] = b.gol / b["min"] * 90, b.asi / b["min"] * 90
b["pos"] = pl.sub_position.reindex(b.index).astype("category").cat.codes
F = ["edad", "f_liga", "f_club", "min", "pj", "gol90", "asi90", "pos"]
b["pred"] = cross_val_predict(
    HistGradientBoostingRegressor(
        max_iter=400, learning_rate=0.05, min_samples_leaf=30, random_state=42
    ),
    b[F],
    b.lv0,
    cv=KFold(5, shuffle=True, random_state=1),
)
b["brecha"] = np.exp(b.pred - b.lv0) - 1
b["cambio"] = np.log(b.v1 / b.market_value_in_eur)
r = b[b["min"] >= 900].copy()
r["grupo"] = pd.qcut(r.brecha, 10, labels=False).map(
    lambda x: (
        "radar (decil 10)"
        if x == 9
        else ("sobrevaluados (decil 1)" if x == 0 else "resto")
    )
)
res = r.groupby("grupo").agg(
    jugadores=("cambio", "size"),
    cambio_mediano=("cambio", lambda s: np.exp(s.median()) - 1),
    suben=("cambio", lambda s: (s > 0).mean()),
)
print(res.round(3).to_string())
d5 = (
    res.loc["radar (decil 10)", "cambio_mediano"] - res.loc["resto", "cambio_mediano"]
)
VEREDICTO.append(
    ["H5", "Radar sube mas que el resto a 12 meses", f"{d5 * 100:+.1f} pp", d5 > 0]
)

# 5. Contraste externo: montos reales de traspaso ------------------------------
c.titulo("5. Contraste externo: montos pagados entre jul-2024 y jul-2025")
tf = c.tm("transfers")
tf["transfer_date"] = pd.to_datetime(tf.transfer_date, errors="coerce")
tf["fee"] = pd.to_numeric(tf.transfer_fee, errors="coerce")
tf = (
    tf[(tf.transfer_date > t0) & (tf.transfer_date <= t1) & (tf.fee > 0)]
    .drop_duplicates("player_id")
    .set_index("player_id")
)
e = b.join(tf.fee, how="inner")
print(
    f"Traspasos con monto: {len(e):,} | Spearman monto vs valor Transfermarkt"
    f" {spearmanr(e.fee, e.market_value_in_eur)[0]:.3f} | vs valor estimado"
    f" ScoutValor {spearmanr(e.fee, np.exp(e.pred))[0]:.3f} | vs promedio de ambos"
    f" {spearmanr(e.fee, np.sqrt(e.market_value_in_eur * np.exp(e.pred)))[0]:.3f}"
)

c.titulo("Veredicto de las hipotesis")
print(
    pd.DataFrame(
        VEREDICTO, columns=["hipotesis", "criterio", "resultado", "se sostiene"]
    ).to_string(index=False)
)

fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
ax[0].barh(grupos.index[::-1], grupos.values[::-1], color="#A6272A")
ax[0].set_title("H1: importancia (caida de R2)")
ax[1].bar(range(5), lift.tasa_exito * 100, color="#C8891A")
ax[1].axhline(yt.mean() * 100, color="#A6272A", ls="--")
ax[1].set_xticks(range(5), ["Q1", "Q2", "Q3", "Q4", "Q5"])
ax[1].set_title("H4: tasa de exito (%) por quintil")
fig.tight_layout()
fig.savefig(c.SALIDA / "a32_resultados.png", dpi=150)
