# Modelo de valor de mercado (modulo A)

- Jugadores: 13,005 (con rendimiento de API-Football: 13,005)
- Validacion cruzada 5 particiones, predicciones fuera de muestra
- R2 en log(valor): **0.848** (linea base solo-liga: 0.411)
- Error absoluto mediano: **40.3%** del valor

## Error por liga (top 15 por jugadores)

| current_club_domestic_competition_id   |   jugadores |   error_mediano_pct |
|:---------------------------------------|------------:|--------------------:|
| ARG1                                   |         748 |                51.4 |
| MLS1                                   |         626 |                43.2 |
| GB1                                    |         563 |                39.8 |
| IT1                                    |         528 |                43.9 |
| BRA1                                   |         523 |                44.4 |
| ES1                                    |         488 |                45   |
| JAP1                                   |         457 |                30   |
| FR1                                    |         454 |                51.7 |
| NL1                                    |         438 |                47.8 |
| L1                                     |         433 |                40   |
| MEX1                                   |         423 |                42.4 |
| PO1                                    |         420 |                47.9 |
| COL1                                   |         418 |                33.6 |
| TR1                                    |         417 |                47   |
| PL1                                    |         412 |                37.3 |

## Top 15 infravalorados (todas las ligas, valor >= 500K)

| name                   | current_club_name              | sub_position       |   edad |   market_value_in_eur |   valor_estimado |   brecha |
|:-----------------------|:-------------------------------|:-------------------|-------:|----------------------:|-----------------:|---------:|
| Nabil Touaizi          | FC Alverca                     | Right Midfield     |     26 |                800000 |          2.4e+06 |      200 |
| Alex Marchal           | Real Sociedad                  | Left Winger        |     19 |                800000 |          2.4e+06 |      200 |
| Mohammed Abu Al-Shamat | Al-Qadsiah Saudi Football Club | Right-Back         |     24 |               1800000 |          5.4e+06 |      200 |
| Luuk de Jong           | FC Porto                       | Centre-Forward     |     36 |                500000 |          1.5e+06 |      200 |
| Tyrese Spicer          | Orlando City Soccer Club       | Left Winger        |     26 |                500000 |          1.5e+06 |      200 |
| Carlos Isaac           | Widzew Lodz                    | Right-Back         |     28 |                600000 |          1.8e+06 |      200 |
| Wessel Kuhn            | PSV Eindhoven                  | Centre-Back        |     20 |                500000 |          1.5e+06 |      200 |
| Alberto Cerri          | Como 1907                      | Centre-Forward     |     31 |                600000 |          1.8e+06 |      200 |
| David Mokwa            | TSG 1899 Hoffenheim            | Centre-Forward     |     22 |               1000000 |          3e+06   |      200 |
| Jalen Blesa            | Rio Ave FC                     | Centre-Forward     |     26 |               2000000 |          6e+06   |      200 |
| Myles Peart-Harris     | Brentford FC                   | Attacking Midfield |     24 |                900000 |          2.7e+06 |      200 |
| Milson                 | Red Star Belgrade              | Left Winger        |     27 |                900000 |          2.7e+06 |      200 |
| Will Sands             | New England Revolution         | Left-Back          |     26 |                600000 |          1.8e+06 |      200 |
| Dominic Sadi           | AFC Bournemouth                | Right Winger       |     23 |                800000 |          2.4e+06 |      200 |
| Federico Ravaglia      | Bologna Football Club 1909     | Goalkeeper         |     27 |               1800000 |          5.4e+06 |      200 |