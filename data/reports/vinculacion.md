# Vinculacion Transfermarkt <-> API-Football

- Jugadores Transfermarkt: 50,149
- Jugadores API-Football: 53,724
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
|        129 |        2100 |             5.4 |
|         72 |        2022 |            22.8 |
|        128 |        1701 |            64.1 |
|        239 |        1646 |            44.4 |
|        253 |        1632 |            66.2 |
|         40 |        1628 |            51.2 |
|        203 |        1603 |            85.6 |
|        141 |        1544 |            42.9 |
|        136 |        1519 |            46.5 |
|         89 |        1352 |            40.9 |
|        307 |        1327 |            57.3 |
|        283 |        1298 |            62.1 |
|         71 |        1298 |            62.5 |
|        106 |        1286 |            65.1 |
|        286 |        1265 |            64.2 |
|         62 |        1223 |            42.6 |
|         98 |        1202 |            65.4 |
|        265 |        1168 |             9.2 |
|        242 |        1145 |             7.1 |
|         95 |        1088 |            47   |
|         79 |        1087 |            47.3 |
|        281 |        1079 |            10.8 |
|        345 |        1062 |            68.6 |
|        333 |        1060 |            81.3 |
|        113 |        1050 |            64.7 |
|        235 |        1031 |            84.4 |
|        103 |         994 |            54.6 |
|        292 |         993 |            53.4 |
|        197 |         992 |            85.2 |
|        135 |         985 |            81.5 |
|        144 |         983 |            80.7 |
|        270 |         933 |             7.7 |
|        263 |         925 |             6.9 |
|         94 |         915 |            81.2 |
|        140 |         896 |            78.7 |
|        262 |         894 |            70.9 |
|         39 |         870 |            89   |
|        210 |         836 |            59.7 |
|        179 |         832 |            87.5 |
|         88 |         816 |            80.1 |
|         61 |         809 |            79.1 |
|        207 |         709 |            65   |
|        218 |         703 |            66.3 |
|         78 |         691 |            83.8 |
|        119 |         669 |            83.3 |
|        250 |         666 |             3   |
|        188 |         643 |            71.7 |
|        252 |         505 |            13.3 |
|       1032 |          41 |             7.3 |
|        268 |           8 |            75   |

## Distribucion de puntajes

| puntaje     |   pares |
|:------------|--------:|
| (0.6, 0.7]  |     364 |
| (0.7, 0.8]  |    2164 |
| (0.8, 0.9]  |    6045 |
| (0.9, 1.01] |   20483 |

## Muestra para revision manual (zona dudosa 0.62-0.75)

| nombre_tm              | nombre_af                        |   puntaje |   s_nombre |   s_pais |   s_club | metodo   |
|:-----------------------|:---------------------------------|----------:|-----------:|---------:|---------:|:---------|
| Jaroslav Harustak      | jaroslav harustak                |      0.75 |       1    |        0 |      1   | fecha    |
| Sefa Yilmaz            | sefa ylmaz                       |      0.68 |       0.69 |        1 |      0   | fecha    |
| Aleksandr Silyanov     | aleksandr siljanov               |      0.73 |       0.65 |        1 |      0.5 | fecha    |
| Sergiy Buletsa         | serhii buletsa                   |      0.72 |       0.76 |        1 |      0   | fecha    |
| Min-jae Kim            | min jae kim                      |      0.72 |       1    |        0 |      0.5 | fecha    |
| Andersson Ordóñez      | anderson rafael ordonez valdez   |      0.68 |       0.69 |        1 |      0   | fecha    |
| Jan Stovicek           | jan stovicek                     |      0.68 |       1    |        0 |      0.5 | fecha    |
| Filip Vecheta          | filip vecheta                    |      0.7  |       1    |        0 |      1   | fecha    |
| Dimitrios Theodoridis  | dimitris theodoridis             |      0.75 |       0.9  |        1 |      0   | fecha    |
| Vidar Ari Jónsson      | viar ari jonsson                 |      0.68 |       0.7  |        1 |      0   | fecha    |
| Musa Barrow            | musa barrow                      |      0.72 |       1    |        0 |      0.5 | fecha    |
| Vikentiy Voloshyn      | vikentii voloshyn                |      0.74 |       0.8  |        1 |      0   | fecha    |
| Andy Carroll           | andrew thomas carroll            |      0.72 |       0.77 |        1 |      0   | fecha    |
| Robin Wendin Thomasson | mats robin wendin thomasson      |      0.72 |       0.95 |        1 |      0   | fecha    |
| Stepan Sebrle          | stepan sebrle                    |      0.67 |       1    |        0 |      0.5 | fecha    |
| Kaiser                 | juan carlos lazaro cervera       |      0.66 |       0.75 |        1 |      0   | fecha    |
| Ju-yeong Park          | ju yeong park                    |      0.7  |       1    |        0 |      1   | fecha    |
| Jiri Pavlenka          | jiri pavlenka                    |      0.65 |       1    |        0 |      0   | fecha    |
| Radek Vítek            | radek vitek                      |      0.73 |       1    |        0 |      0.5 | fecha    |
| Mattie Pollock         | matthew william pollock          |      0.72 |       0.76 |        1 |      0   | fecha    |
| Maiken González        | mayken eduardo gonzalez aldazoro |      0.72 |       0.63 |        1 |      0.5 | fecha    |
| Stefan Gudelj          | stefan gudelj                    |      0.65 |       1    |        0 |      0   | fecha    |
| Walter González        | walter rodrigo gonzalez sosa     |      0.72 |       0.95 |        1 |      0   | fecha    |
| Tolaji Bola            | tolaji adeyinka osegie bola      |      0.74 |       0.95 |        1 |      0   | fecha    |
| Kyu-hyun Park          | kyu hyun park                    |      0.65 |       1    |        0 |      0   | fecha    |