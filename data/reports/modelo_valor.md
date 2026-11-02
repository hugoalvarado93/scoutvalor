# Modelo de valor de mercado (modulo A)

- Jugadores: 13,237 (con rendimiento de API-Football: 13,237)
- Validacion cruzada 5 particiones, predicciones fuera de muestra
- R2 en log(valor): **0.834** (linea base solo-liga: 0.407)
- Error absoluto mediano: **43.1%** del valor

## Error por liga (top 15 por jugadores)

| current_club_domestic_competition_id   |   jugadores |   error_mediano_pct |
|:---------------------------------------|------------:|--------------------:|
| ARG1                                   |         762 |                49.7 |
| MLS1                                   |         637 |                41.7 |
| GB1                                    |         573 |                44.5 |
| IT1                                    |         536 |                46.7 |
| BRA1                                   |         534 |                48.8 |
| ES1                                    |         496 |                45.7 |
| FR1                                    |         459 |                58.1 |
| JAP1                                   |         457 |                28.9 |
| L1                                     |         450 |                41.1 |
| NL1                                    |         447 |                49.7 |
| MEX1                                   |         432 |                44.4 |
| PO1                                    |         424 |                55.3 |
| PL1                                    |         419 |                39.8 |
| COL1                                   |         418 |                33.3 |
| TR1                                    |         418 |                49.3 |

## Top 15 infravalorados (todas las ligas, valor >= 500K)

| name               | current_club_name      | sub_position       |   edad |   market_value_in_eur |   valor_estimado |   brecha |
|:-------------------|:-----------------------|:-------------------|-------:|----------------------:|-----------------:|---------:|
| Vincent Burlet     | LOSC Lille             | Left Midfield      |     21 |                600000 |         1.8e+06  |      200 |
| Giuseppe Ambrosino | SSC Napoli             | Centre-Forward     |     23 |               1800000 |         5.4e+06  |      200 |
| Marko Farji        | Venezia FC             | Left Winger        |     23 |               1700000 |         5.1e+06  |      200 |
| Robert Navarro     | Athletic Bilbao        | Right Winger       |     25 |               6000000 |         1.8e+07  |      200 |
| Will Sands         | New England Revolution | Left-Back          |     26 |                600000 |         1.8e+06  |      200 |
| Peter Federico     | Getafe CF              | Right Winger       |     24 |               1500000 |         4.5e+06  |      200 |
| James Wilson       | Tottenham Hotspur      | Centre-Forward     |     20 |               1200000 |         3.6e+06  |      200 |
| Renato Marin       | Paris Saint-Germain    | Goalkeeper         |     20 |               1000000 |         3e+06    |      200 |
| Myles Peart-Harris | Brentford FC           | Attacking Midfield |     24 |                900000 |         2.7e+06  |      200 |
| Orest Lebedenko    | Vitória Guimarães SC   | Left-Back          |     28 |                500000 |         1.5e+06  |      200 |
| Giovanni Bonfanti  | Pisa Sporting Club     | Centre-Back        |     24 |               1000000 |         3e+06    |      200 |
| Sabit Abdulai      | FC Alverca             | Defensive Midfield |     27 |                700000 |         2.1e+06  |      200 |
| Gabriel Novaes     | Red Bull Bragantino    | Centre-Forward     |     28 |                600000 |         1.8e+06  |      200 |
| Petar Sukacev      | FK Vojvodina Novi Sad  | Left Winger        |     21 |                500000 |         1.5e+06  |      200 |
| Lukas Kirkegaard   | Viborg FF              | Centre-Back        |     21 |                650000 |         1.95e+06 |      200 |