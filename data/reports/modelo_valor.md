# Modelo de valor de mercado (modulo A)

- Jugadores: 13,005 (con rendimiento de API-Football: 13,005)
- Validacion cruzada 5 particiones, predicciones fuera de muestra
- R2 en log(valor): **0.847** (linea base solo-liga: 0.411)
- Error absoluto mediano: **40.6%** del valor

## Error por liga (top 15 por jugadores)

| current_club_domestic_competition_id   |   jugadores |   error_mediano_pct |
|:---------------------------------------|------------:|--------------------:|
| ARG1                                   |         748 |                50   |
| MLS1                                   |         626 |                42.4 |
| GB1                                    |         563 |                40.5 |
| IT1                                    |         528 |                45.9 |
| BRA1                                   |         523 |                46   |
| ES1                                    |         488 |                43.8 |
| JAP1                                   |         457 |                29.8 |
| FR1                                    |         454 |                51.6 |
| NL1                                    |         438 |                46.1 |
| L1                                     |         433 |                40.3 |
| MEX1                                   |         423 |                43.9 |
| PO1                                    |         420 |                50   |
| COL1                                   |         418 |                31.7 |
| TR1                                    |         417 |                45.7 |
| PL1                                    |         412 |                37.7 |

## Top 15 infravalorados (todas las ligas, valor >= 500K)

| name                   | current_club_name            | sub_position     |   edad |   market_value_in_eur |   valor_estimado |   brecha |
|:-----------------------|:-----------------------------|:-----------------|-------:|----------------------:|-----------------:|---------:|
| Roger Martínez         | Al-Taawoun Football Club     | Centre-Forward   |     32 |               1500000 |         4.5e+06  |      200 |
| Mohamed Kanno          | Al-Hilal Saudi Football Club | Central Midfield |     32 |                800000 |         2.4e+06  |      200 |
| Rey Manaj              | Sivasspor                    | Centre-Forward   |     30 |               1800000 |         5.4e+06  |      200 |
| Alessandro Gabrielloni | Como 1907                    | Centre-Forward   |     32 |                500000 |         1.5e+06  |      200 |
| Daniel Ríos            | Club de Foot Montréal        | Centre-Forward   |     32 |                500000 |         1.5e+06  |      200 |
| Ariel Lassiter         | Portland Timbers             | Left Winger      |     32 |                500000 |         1.5e+06  |      200 |
| Florent Muslija        | Fortuna Düsseldorf           | Left Winger      |     28 |               1800000 |         5.4e+06  |      200 |
| Joël van den Berg      | PSV Eindhoven                | Central Midfield |     20 |               1500000 |         4.5e+06  |      200 |
| Alexandru Stoian       | FCSB                         | Centre-Forward   |     19 |                550000 |         1.65e+06 |      200 |
| Otávio Costa           | Cruzeiro Esporte Clube       | Goalkeeper       |     21 |                500000 |         1.5e+06  |      200 |
| Ethan Kohler           | New England Revolution       | Centre-Back      |     21 |                500000 |         1.5e+06  |      200 |
| Justin Ellis           | Orlando City Soccer Club     | Centre-Forward   |     19 |                500000 |         1.5e+06  |      200 |
| Billy van Duijl        | AZ Alkmaar                   | Centre-Back      |     21 |               1500000 |         4.5e+06  |      200 |
| Sofus Johannesen       | FC Midtjylland               | Central Midfield |     19 |                550000 |         1.65e+06 |      200 |
| Amando Lapage          | KVC Westerlo                 | Centre-Back      |     22 |                800000 |         2.4e+06  |      200 |