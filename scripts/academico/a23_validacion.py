"""Actividad 2.3: validaciones del pipeline, manejo de errores, escalabilidad y puertas de calidad."""
import logging
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import cross_val_predict, StratifiedKFold

import comun as c

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("validacion")
RESULTADOS = []


def registrar(prueba, ok, detalle):
    RESULTADOS.append([prueba, "PASA" if ok else "FALLA", detalle])
    (log.info if ok else log.warning)(f"{prueba}: {detalle}")


def validar_esquema(df, columnas, nombre):
    faltan = [k for k in columnas if k not in df.columns]
    registrar(f"esquema {nombre}", not faltan, "completo" if not faltan else f"faltan {faltan}")


def validar_rango(serie, minimo, maximo, nombre, tolerancia=0.001):
    fuera = (~serie.dropna().between(minimo, maximo)).mean()
    registrar(f"rango {nombre}", fuera <= tolerancia, f"{fuera:.2%} fuera de [{minimo}, {maximo}]")


def validar_nulos(serie, limite, nombre):
    nulos = serie.isna().mean()
    registrar(f"nulos {nombre}", nulos <= limite, f"{nulos:.1%} (limite {limite:.0%})")


def psi(a, b, bins=10):
    """Indice de estabilidad poblacional entre dos distribuciones (deriva)."""
    cortes = np.unique(np.quantile(a.dropna(), np.linspace(0, 1, bins + 1)))
    pa = np.histogram(a.dropna(), cortes)[0] / a.notna().sum() + 1e-6
    pb = np.histogram(b.dropna().clip(cortes[0], cortes[-1]), cortes)[0] / b.notna().sum() + 1e-6
    return float(((pa - pb) * np.log(pa / pb)).sum())


# 1. Validacion de entradas -------------------------------------------------------------------
c.titulo("1. Validacion de entradas (esquema, rangos, nulos)")
try:
    va = c.dataset_valor()
    validar_esquema(va, ["player_id", "log_valor", "edad", "minutos", "sub_position"], "valor")
    validar_rango(va.edad, 15, 45, "edad")
    validar_rango(va.minutos, c.A.MIN_MODELO, 12000, "minutos")
    validar_rango(va.market_value_in_eur, 10_000, 250_000_000, "valor EUR")
    validar_nulos(va.calificacion, 0.05, "calificacion")
    validar_nulos(va.meses_contrato, 0.30, "meses de contrato")
    registrar("unicidad player_id", not va.player_id.duplicated().any(), f"{va.player_id.duplicated().sum()} duplicados")
except Exception as e:                       # una fuente rota no debe tumbar el resto del pipeline
    registrar("carga dataset valor", False, f"{type(e).__name__}: {e}")
    raise SystemExit(1)

tr, XT = c.dataset_traspasos()
validar_rango(tr.exito, 0, 1, "etiqueta exito")
registrar("tasa de exito plausible", 0.05 <= tr.exito.mean() <= 0.40, f"{tr.exito.mean():.1%}")
registrar("ventana observada", (tr.fin_S <= pd.Timestamp("2026-07-06")).all(), "toda temporada evaluada cerro antes del corte")

# 2. Deriva entre periodos --------------------------------------------------------------------
c.titulo("2. Deriva de factores entre periodos (PSI: < 0.10 estable, 0.10-0.25 moderada, > 0.25 alta)")
viejo, nuevo = XT[tr.S_desp <= 2019], XT[tr.S_desp >= 2022]
for k in ["edad", "log_valor", "log_fee", "f_liga_dest", "min_antes"]:
    v = psi(viejo[k], nuevo[k])
    registrar(f"deriva {k}", v < 0.25, f"PSI {v:.3f}")

# 3. Escalabilidad ----------------------------------------------------------------------------
c.titulo("3. Escalabilidad: tiempo de entrenamiento contra volumen de datos")
X, y, cat = c.matriz_valor(va)
filas = []
for frac in [0.25, 0.5, 0.75, 1.0]:
    n = int(len(X) * frac)
    t0 = time.time()
    HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05, min_samples_leaf=30, l2_regularization=1.0,
                                  categorical_features=cat, random_state=42).fit(X.values[:n], y[:n])
    filas.append([frac, n, time.time() - t0])
esc = pd.DataFrame(filas, columns=["fraccion", "filas", "segundos"])
esc["seg_por_1000"] = esc.segundos / esc.filas * 1000
print(esc.round(3).to_string(index=False))

# 4. Puertas de calidad antes de publicar -----------------------------------------------------
c.titulo("4. Puertas de calidad del modelo (bloquean la publicacion si fallan)")
m = HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05, min_samples_leaf=30, l2_regularization=1.0,
                                  categorical_features=cat, random_state=42)
pred = cross_val_predict(m, X.values, y, cv=5)
r2 = r2_score(y, pred)
registrar("R2 modulo A >= 0.75", r2 >= 0.75, f"R2 = {r2:.3f}")
p = cross_val_predict(LogisticRegression(C=0.5, max_iter=2000), c.estandarizar(XT), tr.exito,
                      cv=StratifiedKFold(5, shuffle=True, random_state=7), method="predict_proba")[:, 1]
auc = roc_auc_score(tr.exito, p)
registrar("AUC modulo C >= 0.70", auc >= 0.70, f"AUC = {auc:.3f}")

c.titulo("Resumen de validaciones")
res = pd.DataFrame(RESULTADOS, columns=["prueba", "estado", "detalle"])
print(res.to_string(index=False))
print(f"\n{(res.estado == 'PASA').sum()} de {len(res)} pruebas pasan; "
      f"{'se permite publicar' if (res.estado == 'PASA').all() else 'revisar antes de publicar'}")
