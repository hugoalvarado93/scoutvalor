"""Complementos solicitados en la revision de avance (16 nov 2026).

1. Protocolo de validacion cruzada de los modulos A y C.
2. Modulo A: metricas dentro de muestra contra fuera de muestra.
3. Modulo A: contribucion de cada variable (importancia por permutacion).
4. Modulo A: como se forma la estimacion de un jugador (descomposicion).
5. Modulo A: recorte de las estimaciones extremas (cuantas y cuanto).
6. Modulo C: metricas dentro de muestra contra fuera de muestra.
7. Modulo C: matriz de confusion, exactitud, precision, recall y soporte.
8. Modulo C: coeficientes y calculo de una probabilidad paso a paso.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    classification_report,
    confusion_matrix,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold, StratifiedKFold

import comun as c

ETIQUETA = {
    "edad": "Edad",
    "meses_contrato": "Meses de contrato restantes",
    "international_caps": "Partidos con su seleccion",
    "height_in_cm": "Estatura",
    "max_relativo": "Valor actual contra su maximo historico",
    "fuerza_liga": "Fuerza de la liga",
    "fuerza_club": "Fuerza del club",
    "minutos": "Minutos jugados",
    "partidos": "Partidos jugados",
    "pct_titular": "Porcentaje como titular",
    "calificacion": "Calificacion promedio",
    "goles_90": "Goles por 90",
    "asistencias_90": "Asistencias por 90",
    "pases_clave_90": "Pases clave por 90",
    "tiros_90": "Tiros por 90",
    "entradas_90": "Entradas por 90",
    "intercepciones_90": "Intercepciones por 90",
    "regates_exito_90": "Regates exitosos por 90",
    "atajadas_90": "Atajadas por 90",
    "pct_duelos": "Duelos ganados (%)",
    "sub_position": "Posicion",
    "foot": "Pierna habil",
    "current_club_domestic_competition_id": "Liga (identificador)",
    "liga_rend": "Liga de las estadisticas",
}


def hgb(cat):
    """Mismo modelo y parametros que a32_resultados.py."""
    return HistGradientBoostingRegressor(
        max_iter=600,
        learning_rate=0.05,
        min_samples_leaf=30,
        l2_regularization=1.0,
        categorical_features=cat,
        random_state=42,
    )


def metricas_a(y, p):
    real, est = np.exp(y), np.exp(p)
    return (
        r2_score(y, p),
        np.median(np.abs(est / real - 1)) * 100,
        np.abs(est - real).sum() / real.sum() * 100,
    )


# 1. Protocolo de validacion cruzada -------------------------------------------
c.titulo("1. Protocolo de validacion cruzada (k = 5)")
va = c.dataset_valor()
X, y, cat = c.matriz_valor(va)
kf = KFold(5, shuffle=True, random_state=42)
print(f"Modulo A: KFold(5, shuffle=True, random_state=42) sobre {len(y):,} jugadores")
for k, (a, b) in enumerate(kf.split(X), 1):
    print(
        f"  Particion {k}: entrena con {len(a):,} | evalua con {len(b):,} no vistos"
    )
trs, XT = c.dataset_traspasos()
yt = trs.exito.values
skf = StratifiedKFold(5, shuffle=True, random_state=7)
print(
    f"Modulo C: StratifiedKFold(5, shuffle=True, random_state=7) sobre {len(yt):,}"
    " traspasos"
)
for k, (a, b) in enumerate(skf.split(XT, yt), 1):
    print(
        f"  Particion {k}: entrena {len(a):,} | evalua {len(b):,} | tasa de exito"
        f" en prueba {yt[b].mean():.3f}"
    )
print(f"Tasa de exito global: {yt.mean():.3f} (la estratificacion la conserva)")

# 2. Modulo A: dentro de muestra contra fuera de muestra -----------------------
c.titulo(
    "2. Modulo A: metricas dentro de muestra (entrenamiento) vs fuera de muestra"
)
filas, pred = [], np.zeros(len(y))
for k, (a, b) in enumerate(kf.split(X), 1):
    m = hgb(cat).fit(X.iloc[a], y[a])
    pred[b] = m.predict(X.iloc[b])
    dentro = metricas_a(y[a], m.predict(X.iloc[a]))
    fuera = metricas_a(y[b], pred[b])
    filas.append([k, *dentro, *fuera])
t = pd.DataFrame(
    filas,
    columns=["part", "R2_dentro", "err%_dentro", "WMAPE_dentro", "R2_fuera"]
    + ["err%_fuera", "WMAPE_fuera"],
)
print(t.round(3).to_string(index=False))
print("Promedio:", t.mean().drop("part").round(3).to_dict())

# 3. Modulo A: contribucion de cada variable -----------------------------------
c.titulo("3. Modulo A: contribucion de cada variable (caida de R2 al revolverla)")
idx = np.random.RandomState(1).permutation(len(X))
k = int(len(X) * 0.8)
m = hgb(cat).fit(X.iloc[idx[:k]], y[idx[:k]])
pi = permutation_importance(
    m, X.iloc[idx[k:]], y[idx[k:]], n_repeats=5, random_state=1, scoring="r2"
)
imp = pd.Series(pi.importances_mean, X.columns).sort_values(ascending=False)
pos = imp.clip(lower=0)
tabla = pd.DataFrame(
    {
        "variable": [ETIQUETA.get(v, v) for v in imp.index],
        "caida_R2": imp.values.round(3),
        "participacion_%": (pos / pos.sum() * 100).round(1).values,
    }
)
print(tabla.head(14).to_string(index=False))
print(f"Resto ({len(tabla) - 14} variables): {tabla.caida_R2.iloc[14:].sum():.3f}")

# 4. Modulo A: como se forma la estimacion de un jugador -----------------------
c.titulo("4. Modulo A: descomposicion de la estimacion de un jugador (Liga MX)")
Xp = X.iloc[idx[k:]]
vp = va.iloc[idx[k:]]
pp = m.predict(Xp)
mx = (vp.current_club_domestic_competition_id == "MEX1").to_numpy()
if not mx.any():
    mx = np.ones(len(vp), bool)
cand = np.where(mx)[0]
j = cand[np.argmin(np.abs(pp[cand] - np.median(pp[cand])))]
fila = Xp.iloc[[j]]
tipico = X.median()
for col, es_cat in zip(X.columns, cat):
    if es_cat:
        tipico[col] = X[col].mode().iloc[0]
actual = pd.DataFrame([tipico.values], columns=X.columns)
base = m.predict(actual)[0]
grupos = {g: [v for v in vs if v in X.columns] for g, vs in c.A.GRUPOS_VAR.items()}
orden = sorted(grupos, key=lambda g: -imp.reindex(grupos[g]).fillna(0).sum())
jug = vp.iloc[j]
print(
    f"Jugador: {jug['name']} | {jug.current_club_name} | edad {jug.edad:.0f} |"
    f" valor de mercado {jug.market_value_in_eur / 1e6:.2f} M EUR"
)
print(f"Punto de partida (jugador tipico de la base): {np.exp(base) / 1e6:.2f} M EUR")
previo = base
for g in orden:
    if not grupos[g]:
        continue
    actual[grupos[g]] = fila[grupos[g]].values
    nuevo = m.predict(actual)[0]
    print(
        f"  + {g:<24} x{np.exp(nuevo - previo):5.2f}  ->"
        f" {np.exp(nuevo) / 1e6:6.2f} M EUR"
    )
    previo = nuevo
print(
    f"Valor estimado final: {np.exp(pp[j]) / 1e6:.2f} M EUR"
    f" (coincide con el modelo: {np.isclose(previo, pp[j])})"
)

# 5. Modulo A: recorte de estimaciones extremas --------------------------------
c.titulo("5. Modulo A: recorte de la estimacion a [1/3, 3] veces el valor actual")
tope_sup, tope_inf = pred > y + np.log(3), pred < y - np.log(3)
rec = np.clip(pred, y - np.log(3), y + np.log(3))
print(
    f"Jugadores recortados: {(tope_sup | tope_inf).mean() * 100:.1f}% (arriba"
    f" {tope_sup.mean() * 100:.1f}%, abajo {tope_inf.mean() * 100:.1f}%)"
)
for nombre, sel in [("arriba", tope_sup), ("abajo", tope_inf)]:
    if sel.any():
        exceso = np.exp(np.abs(pred[sel] - rec[sel]))
        print(
            f"Recorte {nombre}: el modelo estimaba en mediana"
            f" x{np.median(exceso):.2f}"
            f" mas alla del tope (p90 x{np.quantile(exceso, 0.9):.2f})"
        )
for nombre, p in [("sin recorte", pred), ("con recorte", rec)]:
    r2, err, wm = metricas_a(y, p)
    print(
        f"Metricas {nombre}: R2 {r2:.3f} | error mediano {err:.1f}% | WMAPE {wm:.1f}%"
    )

# 6. Modulo C: dentro de muestra contra fuera de muestra -----------------------
c.titulo("6. Modulo C: AUC y Brier dentro de muestra vs fuera de muestra")
Z = c.estandarizar(XT)
res = {}
for nombre, fab, M in [
    ("Logistica", lambda: LogisticRegression(C=0.5, max_iter=2000), Z),
    ("Gradient boosting", lambda: HistGradientBoostingClassifier(random_state=7), XT),
]:
    fuera, dentro = np.zeros(len(yt)), []
    for a, b in skf.split(M, yt):
        mod = fab().fit(M[a] if nombre == "Logistica" else M.iloc[a], yt[a])
        Ma = M[a] if nombre == "Logistica" else M.iloc[a]
        Mb = M[b] if nombre == "Logistica" else M.iloc[b]
        pa = mod.predict_proba(Ma)[:, 1]
        fuera[b] = mod.predict_proba(Mb)[:, 1]
        dentro.append([roc_auc_score(yt[a], pa), brier_score_loss(yt[a], pa)])
    d = np.mean(dentro, axis=0)
    res[nombre] = fuera
    print(
        f"{nombre:<18} AUC dentro {d[0]:.3f} | fuera {roc_auc_score(yt, fuera):.3f}"
        f" || Brier dentro {d[1]:.3f} | fuera {brier_score_loss(yt, fuera):.3f}"
    )

# 7. Modulo C: matriz de confusion --------------------------------------------
c.titulo("7. Modulo C: matriz de confusion y metricas derivadas (fuera de muestra)")
p_lr = res["Logistica"]
for nombre, umbral in [
    ("Umbral 0.5", 0.5),
    ("Regla top 20%", np.quantile(p_lr, 0.8)),
]:
    yhat = (p_lr >= umbral).astype(int)
    vn, fp, fn, vp_ = confusion_matrix(yt, yhat).ravel()
    n = len(yt)
    print(f"--- {nombre} (umbral {umbral:.3f}) ---")
    print(f"                 Pred. exito   Pred. fracaso")
    print(f"Real exito       VP {vp_:>7,}   FN {fn:>7,}")
    print(f"Real fracaso     FP {fp:>7,}   VN {vn:>7,}")
    print(
        f"VP {vp_ / n:.1%} | VN {vn / n:.1%} | FP {fp / n:.1%} | FN {fn / n:.1%} |"
        f" exactitud {(vp_ + vn) / n:.3f}"
    )
    print(
        classification_report(
            yt, yhat, target_names=["fracaso", "exito"], digits=3, zero_division=0
        ).rstrip()
    )

# 8. Modulo C: coeficientes y calculo de una probabilidad ----------------------
c.titulo("8. Modulo C: coeficientes y calculo de una probabilidad paso a paso")
lr = LogisticRegression(C=0.5, max_iter=2000).fit(Z, yt)
Xi = XT.fillna(XT.median())
media, desv = Xi.mean(), Xi.std().replace(0, 1)
coef = pd.DataFrame(
    {
        "coef_z": lr.coef_[0],
        "OR_por_desv": np.exp(lr.coef_[0]),
        "media": media.values,
        "desv": desv.values,
    },
    index=XT.columns,
).sort_values("coef_z")
print(f"Intercepto: {lr.intercept_[0]:.3f}")
print(coef.round(3).to_string())
pz = lr.predict_proba(Z)[:, 1]
sel = np.where((trs.fee > 0).to_numpy() & (trs.S_desp >= 2023).to_numpy())[0]
i = sel[np.argmin(np.abs(pz[sel] - np.median(pz[sel])))]
r = trs.iloc[i]
print(
    f"\nEjemplo: {r.get('player_name', r.player_id)} | {r.get('from_club_name', '')}"
    f" -> {r.get('to_club_name', '')} | temporada {r.S_desp} | exito real {r.exito}"
)
contrib = lr.coef_[0] * Z[i]
top = np.argsort(-np.abs(contrib))[:8]
for q in top:
    v = XT.columns[q]
    print(
        f"  {v:<14} valor {Xi.iloc[i, q]:8.2f} -> z {Z[i, q]:6.2f} x coef"
        f" {lr.coef_[0][q]:6.3f} = {contrib[q]:+.3f}"
    )
resto = contrib.sum() - contrib[top].sum()
z = lr.intercept_[0] + contrib.sum()
print(f"  resto ({len(contrib) - len(top)} variables)            = {resto:+.3f}")
print(f"Logit z = {lr.intercept_[0]:.3f} {contrib.sum():+.3f} = {z:.3f}")
print(
    f"Probabilidad = 1 / (1 + e^(-z)) = {1 / (1 + np.exp(-z)):.3f}"
    f" (modelo {pz[i]:.3f})"
)
