# Vinculacion Transfermarkt <-> API-Football

- Jugadores Transfermarkt: 50,149
- Jugadores API-Football: 53,763
- Vinculados: 29,056 (fecha: 28,708, nombre: 348)

## Cobertura por liga Transfermarkt (jugadores activos)

| current_club_domestic_competition_id   |   activos |   pct_vinculado |
|:---------------------------------------|----------:|----------------:|
| ARG1                                   |       954 |            96.1 |
| MLS1                                   |       856 |            94   |
| GB1                                    |       826 |            92.4 |
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
| RSK1                                   |       452 |            78.3 |
| C1                                     |       435 |            83   |
| NO1                                    |       424 |            90.1 |
| KR1                                    |       421 |            85.5 |
| AUS1                                   |       411 |            79.8 |
| A1                                     |       400 |            95.2 |
| DK1                                    |       396 |            88.4 |

## Cobertura por liga API-Football (ultima liga del jugador)

|   api_liga |   jugadores |   pct_vinculado |
|-----------:|------------:|----------------:|
|         72 |        2025 |            23.1 |
|        129 |        1924 |             3.3 |
|        128 |        1847 |            61.1 |
|        239 |        1664 |            43.8 |
|         40 |        1652 |            51.9 |
|        253 |        1630 |            66.1 |
|        203 |        1586 |            85.4 |
|        141 |        1562 |            43.5 |
|        136 |        1510 |            46.3 |
|        307 |        1332 |            57.7 |
|         89 |        1327 |            39.9 |
|        283 |        1313 |            62.6 |
|         71 |        1308 |            61.9 |
|        106 |        1274 |            64.7 |
|        286 |        1256 |            63.9 |
|         98 |        1211 |            65.3 |
|         62 |        1196 |            41.6 |
|        265 |        1175 |             9.4 |
|        242 |        1158 |             7.3 |
|        281 |        1091 |            10.8 |
|         79 |        1083 |            47   |
|         95 |        1078 |            46.8 |
|        345 |        1061 |            68.6 |
|        333 |        1059 |            81.3 |
|        113 |        1040 |            64.4 |
|        235 |        1033 |            84.3 |
|        197 |        1005 |            85.4 |
|        103 |         999 |            54.8 |
|        144 |         997 |            80.8 |
|        135 |         995 |            81.7 |
|        292 |         990 |            53.6 |
|        262 |         944 |            68.4 |
|        270 |         924 |             7.7 |
|         94 |         923 |            81.6 |
|        263 |         896 |             6.5 |
|        140 |         885 |            78.5 |
|         39 |         864 |            89.1 |
|        210 |         841 |            59.8 |
|         88 |         827 |            80.4 |
|        179 |         819 |            87.1 |
|         61 |         817 |            79.1 |
|        207 |         704 |            64.8 |
|        218 |         703 |            66.3 |
|         78 |         695 |            83.9 |
|        119 |         673 |            83.4 |
|        250 |         668 |             2.8 |
|        188 |         644 |            71.6 |
|        252 |         506 |            13.2 |
|       1032 |          41 |             7.3 |
|        268 |           8 |            75   |

## Distribucion de puntajes

| puntaje     |   pares |
|:------------|--------:|
| (0.6, 0.7]  |     362 |
| (0.7, 0.8]  |    2105 |
| (0.8, 0.9]  |    6100 |
| (0.9, 1.01] |   20489 |

## Muestra para revision manual (zona dudosa 0.62-0.75)

| nombre_tm                | nombre_af                             |   puntaje |   s_nombre |   s_pais |   s_club | metodo   |
|:-------------------------|:--------------------------------------|----------:|-----------:|---------:|---------:|:---------|
| Pavel Gaszczyk           | pavel gaszczyk                        |      0.62 |       1    |      0   |      0.5 | fecha    |
| Kleiton Cuéllar          | klieton david cuellar gamboa          |      0.74 |       0.62 |      1   |      1   | fecha    |
| Vasilios Nikolakoulis    | vasileios nikolakoulis                |      0.69 |       0.8  |      1   |      0   | fecha    |
| Tomas Holes              | tomas holes                           |      0.72 |       1    |      0   |      0.5 | fecha    |
| Stepan Sebrle            | stepan sebrle                         |      0.68 |       1    |      0   |      0.5 | fecha    |
| Eun-woo Jeong            | eun woo jung                          |      0.63 |       0.7  |      0   |      1   | fecha    |
| Gonzalo Paz              | gonzalo ezequiel paz                  |      0.72 |       0.95 |      0.5 |      0   | fecha    |
| Ivan Basic               | ivan basic                            |      0.73 |       1    |      0   |      0.5 | fecha    |
| David Jurásek            | david jurasek                         |      0.72 |       1    |      0   |      0.5 | fecha    |
| San Jeong                | san jeong                             |      0.65 |       1    |      0   |      0   | fecha    |
| Sam Cleall-Harding       | samuel harding                        |      0.65 |       0.58 |      1   |      0.5 | fecha    |
| Georgios Kyriakopoulos   | giorgos kiriakopoulos                 |      0.68 |       0.6  |      1   |      1   | fecha    |
| Jakub Reznicek           | jakub reznicek                        |      0.72 |       1    |      0   |      0.5 | fecha    |
| Martin Suchomel          | martin suchomel                       |      0.73 |       1    |      0   |      0.5 | fecha    |
| Aleksa Djurasovic        | aleksa urasovic                       |      0.68 |       0.79 |      0   |      1   | fecha    |
| Marko Johansson          | marko johansson                       |      0.75 |       1    |      0.5 |      0   | fecha    |
| Hugo Jan Backovsky       | hugo jan backovsky                    |      0.73 |       1    |      0   |      0.5 | fecha    |
| Lukas Moudry             | lukas moudry                          |      0.68 |       1    |      0   |      0.5 | fecha    |
| Adel Anzimati-Aboudou    | adel anzimati aboudou                 |      0.72 |       1    |      0   |      0.5 | fecha    |
| Tincho Conde             | martin conde gomez                    |      0.69 |       0.53 |      1   |      1   | fecha    |
| Josh Maja                | joshua erowoli orisunmihare oluwaseun |      0.68 |       0.69 |      1   |      0   | fecha    |
| Freddie Ladapo           | olayinka fredrick oladotun ladapo     |      0.67 |       0.67 |      1   |      0   | fecha    |
| Konstantinos Karagiannis | constantinos karagiannis              |      0.75 |       0.91 |      1   |      0   | fecha    |
| Joe Bryan                | joseph edward bryan                   |      0.67 |       0.68 |      1   |      0   | fecha    |
| Bong-soo Kim             | bong soo kim                          |      0.65 |       1    |      0   |      0   | fecha    |