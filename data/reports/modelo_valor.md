# Modelo de valor de mercado (modulo A)

- Jugadores: 13,427 (con rendimiento de API-Football: 13,427)
- Validacion cruzada 5 particiones, predicciones fuera de muestra
- R2 en log(valor): **0.821** (linea base solo-liga: 0.403)
- Error absoluto mediano: **44.4%** del valor

## Error por liga (top 15 por jugadores)

| current_club_domestic_competition_id   |   jugadores |   error_mediano_pct |
|:---------------------------------------|------------:|--------------------:|
| ARG1                                   |         774 |                52.4 |
| MLS1                                   |         645 |                47.9 |
| GB1                                    |         580 |                45.1 |
| IT1                                    |         541 |                48.2 |
| BRA1                                   |         541 |                49.7 |
| ES1                                    |         504 |                49.2 |
| FR1                                    |         468 |                59.9 |
| JAP1                                   |         457 |                29.2 |
| NL1                                    |         455 |                54.6 |
| L1                                     |         455 |                46.9 |
| MEX1                                   |         433 |                49   |
| PO1                                    |         432 |                62.5 |
| COL1                                   |         423 |                33.7 |
| PL1                                    |         422 |                41.9 |
| TR1                                    |         422 |                54.7 |

## Top 15 infravalorados (todas las ligas, valor >= 500K)

| name             | current_club_name            | sub_position       |   edad |   market_value_in_eur |   valor_estimado |   brecha |
|:-----------------|:-----------------------------|:-------------------|-------:|----------------------:|-----------------:|---------:|
| Branimir Mlacic  | Udinese Calcio               | Centre-Back        |     20 |               5000000 |          1.5e+07 |      200 |
| Massiré Sylla    | Union Saint-Gilloise         | Centre-Back        |     22 |                800000 |          2.4e+06 |      200 |
| Noel Törnqvist   | Como 1907                    | Goalkeeper         |     25 |               2000000 |          6e+06   |      200 |
| Oleksandr Yatsyk | Dynamo Kyiv                  | Central Midfield   |     24 |               1000000 |          3e+06   |      200 |
| Shunsuke Saito   | KVC Westerlo                 | Right Winger       |     22 |               1300000 |          3.9e+06 |      200 |
| Rodrigo Ribeiro  | Sporting CP                  | Centre-Forward     |     22 |               4000000 |          1.2e+07 |      200 |
| Guillermo Varela | Clube de Regatas do Flamengo | Right-Back         |     34 |               1000000 |          3e+06   |      200 |
| Pathé Mboup      | Stade Brestois 29            | Left Winger        |     23 |               2500000 |          7.5e+06 |      200 |
| David Mokwa      | TSG 1899 Hoffenheim          | Centre-Forward     |     22 |               1000000 |          3e+06   |      200 |
| Fabian Bredlow   | VfB Stuttgart                | Goalkeeper         |     32 |                700000 |          2.1e+06 |      200 |
| Dermane Karim    | FC Lorient                   | Attacking Midfield |     23 |               2500000 |          7.5e+06 |      200 |
| Mathis Lambourde | Hellas Verona                | Centre-Forward     |     21 |                800000 |          2.4e+06 |      200 |
| Noah Ohio        | FC Utrecht                   | Centre-Forward     |     24 |               1000000 |          3e+06   |      200 |
| Malthe Højholt   | Pisa Sporting Club           | Defensive Midfield |     26 |               1200000 |          3.6e+06 |      200 |
| Miguel Reichmuth | FC Zürich                    | Central Midfield   |     23 |                500000 |          1.5e+06 |      200 |