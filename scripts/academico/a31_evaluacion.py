"""Actividad 3.1: implementacion y evaluacion de los modelos de los modulos A y C."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (brier_score_loss, confusion_matrix, f1_score, precision_score, r2_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import KFold, StratifiedKFold

import comun as c


def hgb(cat, l2=1.0, hoja=30, semilla=42, iters=600):
    return HistGradientBoostingRegressor(max_iter=iters, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=hoja,
                                         l2_regularization=l2, categorical_features=cat, random_state=semilla)


def metricas_valor(y, pred, eur):
    """R2 en log, error mediano relativo y WMAPE en euros."""
    real, est = np.exp(y), np.exp(pred)
    return {"R2": r2_score(y, pred), "err_med_%": np.median(np.abs(est / real - 1)) * 100,
            "WMAPE_%": np.abs(est - real).sum() / real.sum() * 100}


# 1. Modulo A: validacion cruzada con metricas por particion ----------------------------------
c.titulo("1. Modulo A (HistGradientBoosting): metricas por particion")
va = c.dataset_valor()
X, y, cat = c.matriz_valor(va)
pred, filas = np.zeros(len(y)), []
for k, (tr, te) in enumerate(KFold(5, shuffle=True, random_state=42).split(X), 1):
    m = hgb(cat).fit(X.iloc[tr], y[tr])
    pred[te] = m.predict(X.iloc[te])
    filas.append({"particion": k, "R2_entren": r2_score(y[tr], m.predict(X.iloc[tr])), **metricas_valor(y[te], pred[te], None)})
f = pd.DataFrame(filas)
print(f.round(3).to_string(index=False))
print(f"Promedio R2 prueba {f.R2.mean():.3f} +/- {f.R2.std():.3f} | brecha entrenamiento-prueba {(f.R2_entren - f.R2).mean():.3f}")
glob = metricas_valor(y, pred, None)
print("Global fuera de muestra:", ", ".join(f"{k} {v:.3f}" for k, v in glob.items()))

# 2. Sobreajuste: regularizacion -------------------------------------------------------------
c.titulo("2. Regularizacion: efecto de l2, tamano minimo de hoja e iteraciones")
for l2, hoja, it in [(0.0, 5, 600), (1.0, 30, 600), (5.0, 60, 600), (5.0, 60, 200)]:
    p = np.zeros(len(y)); r2e = []
    for tr, te in KFold(5, shuffle=True, random_state=42).split(X):
        m = hgb(cat, l2, hoja, iters=it).fit(X.iloc[tr], y[tr]); p[te] = m.predict(X.iloc[te]); r2e.append(r2_score(y[tr], m.predict(X.iloc[tr])))
    print(f"l2={l2:<4} hoja={hoja:<3} iter={it:<4} R2 entren {np.mean(r2e):.3f} | R2 prueba {r2_score(y, p):.3f} | brecha {np.mean(r2e) - r2_score(y, p):.3f}")

# 3. Robustez y consistencia ------------------------------------------------------------------
c.titulo("3. Robustez (ruido y datos faltantes) y consistencia entre semillas")
rng = np.random.default_rng(0)
tr, te = next(KFold(5, shuffle=True, random_state=1).split(X))
m = hgb(cat).fit(X.iloc[tr], y[tr])
Xr = X.iloc[te].copy()
num = [k for k, es in zip(X.columns, cat) if not es]
Xr[num] = Xr[num] + rng.normal(0, 0.10, Xr[num].shape) * Xr[num].std().values
print(f"R2 limpio {r2_score(y[te], m.predict(X.iloc[te])):.3f} | con ruido 10% desv {r2_score(y[te], m.predict(Xr)):.3f}")
Xf = X.iloc[te].copy()
Xf[["calificacion", "goles_90", "asistencias_90"]] = np.nan
print(f"R2 si faltan calificacion y produccion ofensiva: {r2_score(y[te], m.predict(Xf)):.3f}")
r2s = []
for s in range(5):
    p = np.zeros(len(y))
    for a, b in KFold(5, shuffle=True, random_state=100 + s).split(X):
        p[b] = hgb(cat, semilla=s).fit(X.iloc[a], y[a]).predict(X.iloc[b])
    r2s.append(r2_score(y, p))
print(f"R2 con 5 semillas y particiones distintas: {np.round(r2s, 3).tolist()} | desv {np.std(r2s):.4f}")

# 4. Sesgo: error por confederacion de la liga ------------------------------------------------
c.titulo("4. Sesgo: error mediano por region de la liga del jugador")
paises = c.tm("countries")
conf = {r.country_name: ("CONMEBOL" if r.country_name in c.C.CONMEBOL else c.C.CONF_TM.get(r.confederation))
        for r in paises.itertuples()}
va["region"] = va.liga_pais.map(conf).fillna("sin dato")
va["err"] = np.abs(np.exp(pred - y) - 1) * 100
va["sesgo"] = (pred - y)
print(va.groupby("region").agg(jugadores=("err", "size"), error_mediano=("err", "median"),
                               sesgo_medio_log=("sesgo", "mean")).round(3).to_string())

# 5. Modulo C: clasificacion del exito del fichaje -------------------------------------------
c.titulo("5. Modulo C (regresion logistica): AUC, Brier, precision, recall y F1")
trs, XT = c.dataset_traspasos()
Z, yt = c.estandarizar(XT), trs.exito.values
for C in [0.01, 0.1, 0.5, 2.0]:
    p = np.zeros(len(yt))
    for a, b in StratifiedKFold(5, shuffle=True, random_state=7).split(Z, yt):
        p[b] = LogisticRegression(C=C, max_iter=2000).fit(Z[a], yt[a]).predict_proba(Z[b])[:, 1]
    print(f"C={C:<5} AUC {roc_auc_score(yt, p):.4f} | Brier {brier_score_loss(yt, p):.4f}")
    if C == 0.5:
        p_lr = p
corte = np.quantile(p_lr, 0.80)         # regla de decision: recomendar el 20% con mayor probabilidad
yhat = (p_lr >= corte).astype(int)
print(f"Umbral (top 20%) = {corte:.3f}: precision {precision_score(yt, yhat):.3f}, recall {recall_score(yt, yhat):.3f},"
      f" F1 {f1_score(yt, yhat):.3f}")
print("Matriz de confusion [[VN, FP], [FN, VP]]:", confusion_matrix(yt, yhat).tolist())

# 6. Generalizacion temporal ------------------------------------------------------------------
c.titulo("6. Generalizacion temporal: entrenar con traspasos <= 2021, probar con 2022 en adelante")
viejo, nuevo = trs.S_desp <= 2021, trs.S_desp >= 2022
lr = LogisticRegression(C=0.5, max_iter=2000).fit(Z[viejo], yt[viejo])
pn = lr.predict_proba(Z[nuevo])[:, 1]
print(f"Entrenamiento {viejo.sum():,} | prueba {nuevo.sum():,} | AUC prueba {roc_auc_score(yt[nuevo], pn):.3f} "
      f"| tasa real {yt[nuevo].mean():.3f} vs predicha {pn.mean():.3f}")
print("AUC por region destino:", ", ".join(f"{r} {roc_auc_score(yt[(trs.conf_dest == r).values], p_lr[(trs.conf_dest == r).values]):.3f}"
                                         for r in trs.conf_dest.value_counts().index[:5]
                                         if yt[(trs.conf_dest == r).values].std() > 0))

fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
fpr, tpr, _ = roc_curve(yt, p_lr)
ax[0].plot(fpr, tpr, color="#A6272A"); ax[0].plot([0, 1], [0, 1], "--", color="gray")
ax[0].set_title(f"Modulo C: curva ROC (AUC {roc_auc_score(yt, p_lr):.3f})"); ax[0].set_xlabel("FPR"); ax[0].set_ylabel("TPR")
ax[1].scatter(y, pred, s=3, alpha=0.3, color="#C8891A"); ax[1].plot([y.min(), y.max()], [y.min(), y.max()], color="#A6272A")
ax[1].set_title("Modulo A: log(valor) real vs estimado"); ax[1].set_xlabel("real"); ax[1].set_ylabel("estimado")
fig.tight_layout(); fig.savefig(c.SALIDA / "a31_evaluacion.png", dpi=150)
