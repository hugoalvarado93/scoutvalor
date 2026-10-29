# Vinculacion Transfermarkt <-> API-Football

- Jugadores Transfermarkt: 50,149
- Jugadores API-Football: 53,554
- Vinculados: 29,049 (fecha: 28,701, nombre: 348)

## Cobertura por liga Transfermarkt (jugadores activos)

| current_club_domestic_competition_id   |   activos |   pct_vinculado |
|:---------------------------------------|----------:|----------------:|
| ARG1                                   |       954 |            96.1 |
| MLS1                                   |       856 |            93.9 |
| GB1                                    |       826 |            92.3 |
| IT1                                    |       770 |            88.1 |
| ES1                                    |       748 |            89.3 |
| JAP1                                   |       740 |            86.2 |
| TR1                                    |       726 |            86.9 |
| BRA1                                   |       706 |            93.3 |
| MEX1                                   |       674 |            89.5 |
| FR1                                    |       673 |            87.1 |
| NL1                                    |       645 |            91.5 |
| SER1                                   |       636 |            82.7 |
| RO1                                    |       630 |            86.3 |
| SA1                                    |       616 |            83.4 |
| PO1                                    |       615 |            97.1 |
| PL1                                    |       615 |            92.8 |
| TS1                                    |       615 |            88.6 |
| L1                                     |       610 |            93.8 |
| UKR1                                   |       610 |            78.2 |
| BE1                                    |       567 |            93.7 |
| RU1                                    |       560 |            89.1 |
| COL1                                   |       550 |            92   |
| GR1                                    |       515 |            87.6 |
| SE1                                    |       457 |            88.8 |
| SC1                                    |       453 |            92.9 |
| RSK1                                   |       452 |            78.1 |
| C1                                     |       435 |            83   |
| NO1                                    |       424 |            90.1 |
| KR1                                    |       421 |            85.5 |
| AUS1                                   |       411 |            79.8 |
| A1                                     |       400 |            95.2 |
| DK1                                    |       396 |            88.4 |

## Cobertura por liga API-Football (ultima liga del jugador)

|   api_liga |   jugadores |   pct_vinculado |
|-----------:|------------:|----------------:|
|         72 |        2042 |            22.7 |
|        128 |        1936 |            62.1 |
|        129 |        1921 |             3.2 |
|        253 |        1652 |            66.6 |
|        239 |        1650 |            44.7 |
|         40 |        1621 |            51.3 |
|        203 |        1595 |            85.8 |
|        141 |        1532 |            42.4 |
|        136 |        1512 |            46.4 |
|        307 |        1330 |            57.7 |
|         89 |        1319 |            40.6 |
|        283 |        1296 |            62.4 |
|        106 |        1292 |            65.6 |
|         71 |        1276 |            63.2 |
|        286 |        1253 |            64.2 |
|         62 |        1230 |            42.7 |
|         98 |        1215 |            65.8 |
|        265 |        1156 |             8.6 |
|        242 |        1147 |             6.6 |
|         95 |        1093 |            47.2 |
|         79 |        1080 |            47.2 |
|        113 |        1079 |            65.7 |
|        281 |        1077 |            10.3 |
|        345 |        1058 |            68.8 |
|        333 |        1053 |            81.4 |
|        235 |        1028 |            84.6 |
|        103 |         998 |            55.2 |
|        292 |         998 |            53.7 |
|        135 |         995 |            82.2 |
|        197 |         983 |            85.1 |
|        144 |         952 |            80.7 |
|        262 |         951 |            71.1 |
|        270 |         918 |             6.6 |
|        140 |         878 |            78.7 |
|         94 |         874 |            80.8 |
|         39 |         853 |            89   |
|        210 |         840 |            60   |
|        179 |         838 |            87.5 |
|         88 |         819 |            79.2 |
|        263 |         804 |             2.6 |
|         61 |         800 |            79.2 |
|        207 |         719 |            65.6 |
|        218 |         702 |            66.7 |
|         78 |         685 |            84.5 |
|        250 |         673 |             3.1 |
|        119 |         661 |            83.7 |
|        188 |         633 |            72   |
|        252 |         488 |            11.5 |
|       1032 |          41 |             7.3 |
|        268 |           8 |            75   |

## Distribucion de puntajes

| puntaje     |   pares |
|:------------|--------:|
| (0.6, 0.7]  |     366 |
| (0.7, 0.8]  |    2179 |
| (0.8, 0.9]  |    6028 |
| (0.9, 1.01] |   20476 |

## Muestra para revision manual (zona dudosa 0.62-0.75)

| nombre_tm                | nombre_af                             |   puntaje |   s_nombre |   s_pais |   s_club | metodo   |
|:-------------------------|:--------------------------------------|----------:|-----------:|---------:|---------:|:---------|
| Sirozhiddin Astanakulov  | sirozhiddin astanakulov               |      0.75 |       1    |      0   |      1   | fecha    |
| Chance Cowell            | chance derek cowell maldonado         |      0.62 |       0.95 |      0   |      0   | fecha    |
| Joe Bryan                | joseph edward bryan                   |      0.67 |       0.68 |      1   |      0   | fecha    |
| Matej Rynes              | matej rynes                           |      0.73 |       1    |      0   |      0.5 | fecha    |
| Diamantis Chouchoumis    | diamantis houhoumis                   |      0.68 |       0.7  |      1   |      0   | fecha    |
| Lukas Matejka            | lukas matejka                         |      0.72 |       1    |      0   |      0.5 | fecha    |
| Turki Al-Ghumayl         | turki mashour al ghamil               |      0.75 |       0.63 |      1   |      1   | fecha    |
| Aleksandr Chupayov       | aleksandr chupaev                     |      0.67 |       0.68 |      1   |      0   | fecha    |
| Harramiz                 | harramiz quieta ferreira soares       |      0.65 |       1    |      0   |      0   | fecha    |
| Chang-geun Lee           | chang geun lee                        |      0.65 |       1    |      0   |      0   | fecha    |
| Frederik Roslyng         | frederik roslyng                      |      0.7  |       1    |      0.5 |      0   | fecha    |
| Will Alves               | william thomas alves                  |      0.74 |       0.71 |      1   |      1   | fecha    |
| Tomas Holes              | tomas holes                           |      0.72 |       1    |      0   |      0.5 | fecha    |
| Rade Krunic              | rade krunic                           |      0.65 |       1    |      0   |      0   | fecha    |
| Jakub Slowik             | jakub sowik                           |      0.69 |       0.7  |      1   |      0   | fecha    |
| Athanasios Triantafyllou | thanasis triantafyllou                |      0.71 |       0.84 |      1   |      0   | fecha    |
| Benjamin Tahirović       | benjamin tahirovic                    |      0.7  |       1    |      0   |      1   | fecha    |
| Seung-woo Ryu            | seung woo ryu                         |      0.65 |       1    |      0   |      0   | fecha    |
| Seung-bin Jung           | seung bin jeong                       |      0.66 |       0.75 |      0   |      1   | fecha    |
| Adam Karabec             | adam karabec                          |      0.72 |       1    |      0   |      0.5 | fecha    |
| Khoder Kaddour           | khoder kaddour                        |      0.68 |       1    |      0   |      0.5 | fecha    |
| Theo Folgado             | theo mickael kevin folgado            |      0.72 |       0.95 |      0   |      1   | fecha    |
| Sadik Bas                | sadk bas                              |      0.71 |       0.48 |      1   |      1   | fecha    |
| Rafa Vieira              | rafael jose fernandes teixeira vieira |      0.75 |       0.81 |      1   |      0   | fecha    |
| Jon Gudni Fjóluson       | jon guni fjoluson                     |      0.72 |       0.76 |      1   |      0   | fecha    |