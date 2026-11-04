"""Actividad 1.2: disponibilidad de los datos que exige cada hipotesis de ScoutValor.

H1 (explicativa)   El rendimiento, la edad, el contrato y el contexto explican
                   el valor de mercado.
H2 (predictiva)    El exito de un fichaje se puede anticipar con datos previos
                   al traspaso.
H3 (causal)        Compartir idioma o confederacion con el pais destino eleva
                   la probabilidad de exito.
H4 (prescriptiva)  Elegir fichajes por probabilidad de exito, dentro del
                   presupuesto, supera a la tasa base.
H5 (predictiva)    Los jugadores que el modelo marca como subvaluados ganan
                   valor en los 12 meses siguientes.
"""

import numpy as np
import pandas as pd

import comun as c

# 1. Inventario de fuentes -----------------------------------------------------
c.titulo("1. Inventario de fuentes (filas x columnas)")
for t in [
    "players",
    "player_valuations",
    "transfers",
    "appearances",
    "games",
    "clubs",
]:
    d = c.tm(t)
    print(f"Transfermarkt.{t:<18} {len(d):>10,} x {d.shape[1]:>2}")
af = c.A.leer(af="jugadores_temporada")
print(
    f"API-Football.jugadores_temp   {len(af):>10,} x {af.shape[1]:>2}   temporadas"
    f" {int(af.temporada.min())}-{int(af.temporada.max())}, ligas"
    f" {af.api_liga.nunique()}"
)

# 2. Variables de respuesta y factores para H1 y H5 (modulo A) -----------------
c.titulo("2. Modulo A: variable de respuesta y cobertura de factores (H1, H5)")
va = c.dataset_valor()
print(f"Jugadores elegibles (>= {c.A.MIN_MODELO} min): {len(va):,}")
print(
    f"Respuesta log(valor): media {va.log_valor.mean():.2f}, desv"
    f" {va.log_valor.std():.2f}, rango EUR {va.market_value_in_eur.min():,.0f} a"
    f" {va.market_value_in_eur.max():,.0f}"
)
grupos = c.A.GRUPOS_VAR
filas = []
for grupo, cols in grupos.items():
    cols = [x for x in cols if x in va.columns]
    cob = va[cols].notna().mean().mean() * 100 if cols else 0
    filas.append([grupo, len(cols), round(cob, 1)])
print(
    pd.DataFrame(
        filas, columns=["grupo de factores", "variables", "cobertura_%"]
    ).to_string(index=False)
)

# 3. Variables de respuesta y factores para H2, H3 y H4 (modulo C) -------------
c.titulo("3. Modulo C: traspasos etiquetados y tipo de movimiento (H2, H3, H4)")
tr, X = c.dataset_traspasos()
print(
    f"Traspasos etiquetados: {len(tr):,} | temporadas destino"
    f" {tr.S_desp.min()}-{tr.S_desp.max()} | tasa de exito {tr.exito.mean():.1%}"
)
print(
    f"Con monto de traspaso > 0: {(tr.fee > 0).mean():.1%} | con minutos previos:"
    f" {tr.min_antes.notna().mean():.1%}"
)
mov = np.select(
    [X.mov_local == 1, X.mov_idioma == 1, X.mov_conf == 1],
    ["mismo pais", "mismo idioma", "misma confederacion"],
    "otro idioma y confed.",
)
t = (
    pd.DataFrame({"mov": mov, "exito": tr.exito})
    .groupby("mov")
    .exito.agg(traspasos="size", tasa_exito="mean")
)
print(t.assign(tasa_exito=lambda d: (d.tasa_exito * 100).round(1)).to_string())

# 4. Datos para la retroprueba de H5 -------------------------------------------
c.titulo("4. H5: valuaciones historicas disponibles para una retroprueba de 12 meses")
v = c.tm("player_valuations")
v["date"] = pd.to_datetime(v.date, errors="coerce")
for corte in ["2023-07-01", "2024-07-01", "2025-07-01"]:
    t0 = pd.Timestamp(corte)
    a0 = v[
        (v.date <= t0) & (v.date > t0 - pd.Timedelta(days=183))
    ].player_id.nunique()
    a1 = v[
        (v.date > t0) & (v.date <= t0 + pd.Timedelta(days=365))
    ].player_id.nunique()
    print(
        f"corte {corte}: jugadores valuados 6m antes {a0:>6,} | valuados 12m despues"
        f" {a1:>6,}"
    )

# 5. Matriz hipotesis -> datos -------------------------------------------------
c.titulo("5. Hipotesis, variable de respuesta y estado de los datos")
req = [
    [
        "H1",
        "log(valor de mercado)",
        len(va),
        va[["minutos", "calificacion", "edad"]].notna().all(axis=1).mean(),
    ],
    ["H2", "exito del fichaje (0/1)", len(tr), X.notna().all(axis=1).mean()],
    ["H3", "exito por tipo de movimiento", len(tr), tr.nac.notna().mean()],
    ["H4", "tasa de exito del top 20%", len(tr), X.notna().all(axis=1).mean()],
    [
        "H5",
        "cambio de valor a 12 meses",
        v.player_id.nunique(),
        v.market_value_in_eur.notna().mean(),
    ],
]
r = pd.DataFrame(
    req, columns=["hip.", "variable de respuesta", "registros", "completitud"]
)
r["completitud"] = (r.completitud * 100).round(1).astype(str) + " %"
r["estado"] = np.where(r.registros >= 1000, "suficiente", "insuficiente")
print(r.to_string(index=False))
