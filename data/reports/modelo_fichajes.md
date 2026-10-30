# Modelo de exito de fichajes (modulo C)

- Traspasos etiquetados: 42,252 (temporadas destino 2012-2025)
- Tasa base de exito: 14.6%
- Exito = >= 1,500 min de liga en la primera temporada completa y valor >= 90% del valor al fichar
- Regresion logistica (publicada): AUC 0.746, Brier 0.112
- Gradient boosting (referencia): AUC 0.788, Brier 0.107

## Coeficientes estandarizados (logistica)

| variable      |   coef_estandarizado |
|:--------------|---------------------:|
| edad2         |               -0.251 |
| f_liga_dest   |               -0.235 |
| d_club        |               -0.186 |
| edad          |               -0.174 |
| g_DEL         |               -0.151 |
| f_club_dest   |               -0.142 |
| d_liga        |               -0.099 |
| f_liga_orig   |               -0.095 |
| mov_local     |               -0.049 |
| mov_conf      |               -0.042 |
| mov_idioma    |               -0.009 |
| g_MED         |                0.003 |
| compatriotas  |                0.013 |
| g_POR         |                0.065 |
| f_club_orig   |                0.082 |
| competencia   |                0.086 |
| g_DEF         |                0.106 |
| sin_min_antes |                0.122 |
| min_antes     |                0.277 |
| log_valor     |                0.289 |
| log_fee       |                0.496 |

## Calibracion por deciles (logistica, fuera de muestra)

|   dec |   prob_media |   tasa_real |    n |
|------:|-------------:|------------:|-----:|
|     0 |        0.03  |       0.023 | 4226 |
|     1 |        0.049 |       0.042 | 4225 |
|     2 |        0.065 |       0.054 | 4225 |
|     3 |        0.081 |       0.072 | 4225 |
|     4 |        0.098 |       0.093 | 4225 |
|     5 |        0.119 |       0.134 | 4225 |
|     6 |        0.146 |       0.164 | 4225 |
|     7 |        0.185 |       0.2   | 4225 |
|     8 |        0.258 |       0.271 | 4225 |
|     9 |        0.425 |       0.403 | 4226 |

## Pares de ligas con mas traspasos

| liga_orig   | liga_dest   |   traspasos |   tasa_exito |
|:------------|:------------|------------:|-------------:|
| IT1         | IT1         |        2628 |        0.123 |
| GB1         | GB1         |        1482 |        0.151 |
| ES1         | ES1         |        1371 |        0.145 |
| TR1         | TR1         |        1137 |        0.124 |
| RU1         | RU1         |        1102 |        0.151 |
| FR1         | FR1         |        1095 |        0.174 |
| UKR1        | UKR1        |        1084 |        0.118 |
| L1          | L1          |        1080 |        0.175 |
| NL1         | NL1         |         854 |        0.221 |
| PO1         | PO1         |         807 |        0.165 |
| BE1         | BE1         |         578 |        0.176 |
| GR1         | GR1         |         576 |        0.132 |
| SC1         | SC1         |         465 |        0.163 |
| DK1         | DK1         |         431 |        0.125 |
| FR1         | GB1         |         320 |        0.206 |
| ES1         | GB1         |         316 |        0.19  |
| GB1         | ES1         |         304 |        0.22  |
| IT1         | GB1         |         263 |        0.163 |
| L1          | GB1         |         258 |        0.178 |
| GB1         | IT1         |         248 |        0.21  |