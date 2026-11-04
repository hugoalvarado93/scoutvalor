# Modelo de valor de mercado (modulo A)

- Jugadores: 13,237 (con rendimiento de API-Football: 13,237)
- Validacion cruzada 5 particiones, predicciones fuera de muestra
- R2 en log(valor): **0.833** (linea base solo-liga: 0.407)
- Error absoluto mediano: **42.7%** del valor

## Error por liga (top 15 por jugadores)

| current_club_domestic_competition_id   |   jugadores |   error_mediano_pct |
|:---------------------------------------|------------:|--------------------:|
| ARG1                                   |         762 |                50.4 |
| MLS1                                   |         637 |                43.7 |
| GB1                                    |         573 |                43.9 |
| IT1                                    |         536 |                48.5 |
| BRA1                                   |         534 |                46.2 |
| ES1                                    |         496 |                44.5 |
| FR1                                    |         459 |                58.7 |
| JAP1                                   |         457 |                27.9 |
| L1                                     |         450 |                43.2 |
| NL1                                    |         447 |                49.1 |
| MEX1                                   |         432 |                42.6 |
| PO1                                    |         424 |                54.5 |
| PL1                                    |         419 |                40.7 |
| COL1                                   |         418 |                34.6 |
| TR1                                    |         418 |                48   |

## Top 15 infravalorados (todas las ligas, valor >= 500K)

| name             | current_club_name             | sub_position       |   edad |   market_value_in_eur |   valor_estimado |   brecha |
|:-----------------|:------------------------------|:-------------------|-------:|----------------------:|-----------------:|---------:|
| Tim Drexler      | Fußballclub Red Bull Salzburg | Centre-Back        |     22 |               3000000 |         9e+06    |      200 |
| Pedro Santos     | FC Famalicão                  | Right Winger       |     24 |                600000 |         1.8e+06  |      200 |
| Florent Muslija  | Fortuna Düsseldorf            | Left Winger        |     28 |               1800000 |         5.4e+06  |      200 |
| Ayumu Yokoyama   | KRC Genk                      | Left Winger        |     24 |               1500000 |         4.5e+06  |      200 |
| Nabil Touaizi    | FC Alverca                    | Right Midfield     |     26 |                800000 |         2.4e+06  |      200 |
| Sofus Johannesen | FC Midtjylland                | Central Midfield   |     19 |                550000 |         1.65e+06 |      200 |
| Alberto Cerri    | Como 1907                     | Centre-Forward     |     31 |                600000 |         1.8e+06  |      200 |
| Calvin Ramsay    | Liverpool FC                  | Right-Back         |     23 |               1500000 |         4.5e+06  |      200 |
| Toma Bašić       | Società Sportiva Lazio S.p.A. | Central Midfield   |     30 |               3000000 |         9e+06    |      200 |
| Sadik Fofana     | US Lecce                      | Defensive Midfield |     23 |                800000 |         2.4e+06  |      200 |
| Alexandr Buzek   | SK Slavia Prague              | Central Midfield   |     22 |               1000000 |         3e+06    |      200 |
| Joeri Heerkens   | AC Sparta Prague              | Goalkeeper         |     20 |               1000000 |         3e+06    |      200 |
| Edoardo Iannoni  | US Sassuolo                   | Central Midfield   |     26 |                800000 |         2.4e+06  |      200 |
| Ángel Sepúlveda  | CD Cruz Azul                  | Centre-Forward     |     36 |                500000 |         1.5e+06  |      200 |
| Orest Lebedenko  | Vitória Guimarães SC          | Left-Back          |     28 |                500000 |         1.5e+06  |      200 |