# Modelo de valor de mercado (modulo A)

- Jugadores: 13,387 (con rendimiento de API-Football: 13,387)
- Validacion cruzada 5 particiones, predicciones fuera de muestra
- R2 en log(valor): **0.825** (linea base solo-liga: 0.403)
- Error absoluto mediano: **43.8%** del valor

## Error por liga (top 15 por jugadores)

| current_club_domestic_competition_id   |   jugadores |   error_mediano_pct |
|:---------------------------------------|------------:|--------------------:|
| ARG1                                   |         774 |                54.9 |
| MLS1                                   |         645 |                47   |
| GB1                                    |         579 |                46.5 |
| IT1                                    |         541 |                48.7 |
| BRA1                                   |         540 |                49.4 |
| ES1                                    |         503 |                47.2 |
| FR1                                    |         467 |                58.9 |
| JAP1                                   |         457 |                30.2 |
| L1                                     |         456 |                44   |
| NL1                                    |         452 |                46.6 |
| PO1                                    |         431 |                53.6 |
| MEX1                                   |         430 |                49   |
| TR1                                    |         422 |                50.4 |
| PL1                                    |         422 |                40.4 |
| COL1                                   |         420 |                33.6 |

## Top 15 infravalorados (todas las ligas, valor >= 500K)

| name                | current_club_name     | sub_position       |   edad |   market_value_in_eur |   valor_estimado |   brecha |
|:--------------------|:----------------------|:-------------------|-------:|----------------------:|-----------------:|---------:|
| Pedro Santos        | FC Famalicão          | Right Winger       |     24 |                600000 |         1.8e+06  |      200 |
| Paul Smyth          | Queens Park Rangers   | Right Winger       |     29 |                800000 |         2.4e+06  |      200 |
| Ángel Sepúlveda     | CD Cruz Azul          | Centre-Forward     |     36 |                500000 |         1.5e+06  |      200 |
| Lucas Jetten        | Ajax Amsterdam        | Left-Back          |     19 |                700000 |         2.1e+06  |      200 |
| Joël van den Berg   | PSV Eindhoven         | Central Midfield   |     20 |               1500000 |         4.5e+06  |      200 |
| Matteo Cocchi       | Inter Milan           | Left-Back          |     20 |               1500000 |         4.5e+06  |      200 |
| Ariel Lassiter      | Portland Timbers      | Left Winger        |     32 |                500000 |         1.5e+06  |      200 |
| Daniel Luna         | RCD Mallorca          | Attacking Midfield |     23 |                600000 |         1.8e+06  |      200 |
| David Mokwa         | TSG 1899 Hoffenheim   | Centre-Forward     |     22 |               1000000 |         3e+06    |      200 |
| Pathé Mboup         | Stade Brestois 29     | Left Winger        |     23 |               2500000 |         7.5e+06  |      200 |
| Sabit Abdulai       | FC Alverca            | Defensive Midfield |     27 |                700000 |         2.1e+06  |      200 |
| Dani van den Heuvel | Club Brugge KV        | Goalkeeper         |     23 |                800000 |         2.4e+06  |      200 |
| Sofus Johannesen    | FC Midtjylland        | Central Midfield   |     19 |                550000 |         1.65e+06 |      200 |
| Ahmed Abdullahi     | Sunderland AFC        | Centre-Forward     |     22 |                800000 |         2.4e+06  |      200 |
| Caíque Gonçalves    | Esporte Clube Vitória | Defensive Midfield |     31 |                500000 |         1.5e+06  |      200 |