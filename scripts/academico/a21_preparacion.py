"""Actividad 2.1: calidad, limpieza, transformacion, consistencia, muestreo, relevancia y colinealidad."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, skew, spearmanr
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

import comun as c

# 1. Calidad e integridad ---------------------------------------------------------------------
c.titulo("1. Calidad: universo bruto de jugadores activos")
pl = c.tm("players")
pl = pl[pl.last_season == pl.last_season.max()]
print(f"Activos: {len(pl):,} | duplicados por player_id: {pl.player_id.duplicated().sum()}")
crit = ["market_value_in_eur", "date_of_birth", "sub_position", "current_club_domestic_competition_id",
        "contract_expiration_date", "height_in_cm", "foot"]
print((pl[crit].isna().mean() * 100).round(1).rename("faltantes_%").to_string())

# 2. Limpieza: reglas y registros que sobreviven ----------------------------------------------
c.titulo("2. Limpieza: reglas aplicadas en cascada")
va_todo = c.dataset_valor(minimo=0)
pasos = [("activos con valor > 0", len(va_todo))]
edad_ok = va_todo.edad.between(15, 45)
pasos.append(("edad entre 15 y 45", int(edad_ok.sum())))
m = pd.to_numeric(va_todo.minutos, errors="coerce").fillna(0)
pasos.append((f"con >= {c.A.MIN_MODELO} min recientes (modelo)", int((edad_ok & (m >= c.A.MIN_MODELO)).sum())))
pasos.append((f"con >= {c.A.MIN_RADAR} min recientes (radar)", int((edad_ok & (m >= c.A.MIN_RADAR)).sum())))
for p, n in pasos:
    print(f"{p:<40} {n:>8,}")
va = c.dataset_valor()

# 3. Transformacion ---------------------------------------------------------------------------
c.titulo("3. Transformacion: asimetria del valor y normalizacion por 90 minutos")
print(f"Asimetria valor EUR: {skew(va.market_value_in_eur):.2f} -> log(valor): {skew(va.log_valor):.2f}")
print(f"Goles: totales vs por 90, correlacion con minutos: "
      f"{spearmanr(va.goles, va.minutos, nan_policy='omit')[0]:.2f} -> "
      f"{spearmanr(va.goles_90, va.minutos, nan_policy='omit')[0]:.2f}")
fig, ax = plt.subplots(1, 2, figsize=(9, 3))
ax[0].hist(va.market_value_in_eur / 1e6, bins=60, color="#A6272A"); ax[0].set_title("Valor (millones EUR)")
ax[1].hist(va.log_valor, bins=60, color="#C8891A"); ax[1].set_title("log(valor)")
fig.tight_layout(); fig.savefig(c.SALIDA / "a21_transformacion.png", dpi=150)

# 4. Consistencia temporal y contextual -------------------------------------------------------
c.titulo("4. Consistencia temporal y contextual")
v = c.tm("player_valuations")
v["date"] = pd.to_datetime(v.date, errors="coerce")
ult = v.groupby("player_id").date.max().reindex(va.player_id)
ref = v.date.max()
print(f"Ultima valuacion en la fuente: {ref.date()} | antiguedad mediana de la valuacion vigente: "
      f"{(ref - ult).dt.days.median():.0f} dias | > 365 dias: {((ref - ult).dt.days > 365).mean():.1%}")
print(f"Temporadas API-Football usadas por jugador: las 2 mas recientes de cada uno")
apps, games = c.tm("appearances"), c.tm("games")
g = games[["game_id", "season", "competition_type"]].astype({"game_id": str})
a = apps.astype({"game_id": str}).merge(g, on="game_id")
a = a[a.competition_type == "domestic_league"]
temp = int(pd.to_numeric(a.season).max()) - 1
mtm = a[a.season == temp].groupby("player_id").minutes_played.sum()
af = c.A.leer(af="jugadores_temporada")
af = af.assign(temporada=pd.to_numeric(af.temporada), minutos=pd.to_numeric(af.minutos, errors="coerce"))
maf = af[af.temporada == temp].groupby(pd.to_numeric(af.api_jugador)).minutos.sum()
mtm.index = pd.to_numeric(mtm.index)
vin = c.A.leer_vinculos().dropna(subset=["player_id", "api_jugador"])
par = pd.DataFrame({"tm": pd.to_numeric(vin.player_id).map(mtm).values,
                    "af": pd.to_numeric(vin.api_jugador).map(maf).values}).dropna()
par = par[(par.tm > 0) & (par.af > 0)]
print(f"Temporada {temp}: minutos Transfermarkt vs API-Football, {len(par):,} jugadores vinculados, "
      f"Spearman {spearmanr(par.tm, par.af)[0]:.3f}, diferencia mediana {(par.af - par.tm).abs().median():.0f} min")

# 5. Muestreo representativo ------------------------------------------------------------------
c.titulo("5. Muestreo estratificado (20%, estratos liga x grupo de posicion)")
va["grupo"] = va.sub_position.map(c.C.POS).map(c.C.GRUPO)
estr = va.current_club_domestic_competition_id.astype(str) + "|" + va.grupo.astype(str)
muestra = va.groupby(estr, group_keys=False).sample(frac=0.2, random_state=11)
print(f"Poblacion {len(va):,} | muestra {len(muestra):,} | estratos {estr.nunique()}")
for col in ["log_valor", "edad", "minutos", "calificacion"]:
    ks = ks_2samp(va[col].dropna(), muestra[col].dropna())
    print(f"  {col:<13} media pob {va[col].mean():8.2f} | media muestra {muestra[col].mean():8.2f} | KS p={ks.pvalue:.3f}")
dif = (muestra.grupo.value_counts(normalize=True) - va.grupo.value_counts(normalize=True)).abs().max()
print(f"  maxima diferencia de proporcion por grupo de posicion: {dif * 100:.2f} puntos")

# 6. Relevancia de factores -------------------------------------------------------------------
c.titulo("6. Relevancia: factores del valor (Spearman e informacion mutua)")
X, y, _ = c.matriz_valor(va)
num = X.drop(columns=[k for k in c.A.CATEG if k in X]).fillna(X.median())  # solo numericas
mi = mutual_info_regression(num, y, random_state=0)
rel = pd.DataFrame({"spearman": [spearmanr(num[k], y)[0] for k in num], "info_mutua": mi}, index=num.columns)
print(rel.round(3).sort_values("info_mutua", ascending=False).head(12).to_string())
tr, XT = c.dataset_traspasos()
auc = {k: roc_auc_score(tr.exito, XT[k].fillna(XT[k].median())) for k in XT}
auc = pd.Series(auc).sub(0.5).abs().add(0.5).sort_values(ascending=False)
print("\nTraspasos: AUC univariado de cada factor (0.5 = sin poder)")
print(auc.round(3).head(8).to_string())

# 7. Colinealidad -----------------------------------------------------------------------------
def vif(df):
    df = df.fillna(df.median())
    out = {}
    for k in df:
        r2 = LinearRegression().fit(df.drop(columns=k), df[k]).score(df.drop(columns=k), df[k])
        out[k] = np.inf if r2 >= 0.9999 else 1 / (1 - r2)
    return pd.Series(out)


c.titulo("7. Colinealidad (VIF) en los factores de traspasos")
base = XT.drop(columns=[x for x in XT if x.startswith("g_")])
v1 = vif(base)
print("Antes:", ", ".join(f"{k}={x:.1f}" for k, x in v1.sort_values(ascending=False).head(6).items()))
v2 = vif(base.drop(columns=["d_liga", "d_club", "edad2"]))
print("Sin d_liga, d_club y edad2:", ", ".join(f"{k}={x:.1f}" for k, x in v2.sort_values(ascending=False).head(6).items()))
cor = num.corr(method="spearman")
pares = [(a, b, cor.loc[a, b]) for i, a in enumerate(cor) for b in cor.columns[i + 1:] if abs(cor.loc[a, b]) >= 0.7]
print("Pares |rho| >= 0.7 en el modulo A:", "; ".join(f"{a}~{b} {r:.2f}" for a, b, r in pares) or "ninguno")
fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(cor, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(cor)), cor.columns, rotation=90, fontsize=6); ax.set_yticks(range(len(cor)), cor.index, fontsize=6)
fig.colorbar(im, fraction=0.04); fig.tight_layout(); fig.savefig(c.SALIDA / "a21_correlacion.png", dpi=150)
