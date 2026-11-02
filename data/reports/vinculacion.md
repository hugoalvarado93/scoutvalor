# Vinculacion Transfermarkt <-> API-Football

- Jugadores Transfermarkt: 50,149
- Jugadores API-Football: 53,622
- Vinculados: 29,053 (fecha: 28,705, nombre: 348)

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
|         72 |        2008 |            22.6 |
|        128 |        1699 |            64.2 |
|        239 |        1645 |            44.8 |
|        253 |        1636 |            66.3 |
|         40 |        1622 |            51.2 |
|        203 |        1592 |            85.7 |
|        141 |        1538 |            42.8 |
|        136 |        1519 |            46.7 |
|         89 |        1356 |            41.1 |
|        307 |        1327 |            57.3 |
|         71 |        1305 |            62.9 |
|        283 |        1299 |            62.3 |
|        106 |        1289 |            65.2 |
|        286 |        1266 |            64.3 |
|         62 |        1227 |            42.8 |
|         98 |        1207 |            65.5 |
|        265 |        1165 |             9.2 |
|        242 |        1149 |             7   |
|         95 |        1087 |            46.7 |
|         79 |        1085 |            47.3 |
|        281 |        1080 |            10.6 |
|        345 |        1063 |            68.6 |
|        333 |        1059 |            81.3 |
|        113 |        1046 |            64.5 |
|        235 |        1034 |            84.4 |
|        103 |        1001 |            55   |
|        292 |         995 |            53.4 |
|        197 |         987 |            85.2 |
|        135 |         983 |            81.5 |
|        144 |         966 |            80.8 |
|        262 |         949 |            71   |
|        270 |         934 |             7.7 |
|         94 |         912 |            81.1 |
|        140 |         902 |            78.8 |
|         39 |         876 |            89   |
|        210 |         836 |            59.7 |
|        179 |         835 |            87.4 |
|         88 |         812 |            79.9 |
|         61 |         809 |            79.1 |
|        263 |         804 |             2.6 |
|        207 |         709 |            65.2 |
|        218 |         703 |            66.6 |
|         78 |         692 |            84   |
|        250 |         666 |             3   |
|        119 |         655 |            83.4 |
|        188 |         635 |            72   |
|        252 |         509 |            13.8 |
|       1032 |          41 |             7.3 |
|        268 |           8 |            75   |

## Distribucion de puntajes

| puntaje     |   pares |
|:------------|--------:|
| (0.6, 0.7]  |     364 |
| (0.7, 0.8]  |    2134 |
| (0.8, 0.9]  |    6038 |
| (0.9, 1.01] |   20517 |

## Muestra para revision manual (zona dudosa 0.62-0.75)

| nombre_tm           | nombre_af                   |   puntaje |   s_nombre |   s_pais |   s_club | metodo   |
|:--------------------|:----------------------------|----------:|-----------:|---------:|---------:|:---------|
| Dusan Ristic        | dusan ristic                |      0.75 |       1    |        0 |      1   | fecha    |
| Theo Folgado        | theo mickael kevin folgado  |      0.72 |       0.95 |        0 |      1   | fecha    |
| Djuro-Giulio Djekic | uro giulio ekic             |      0.73 |       0.6  |        1 |      1   | fecha    |
| Sergiy Buletsa      | serhii buletsa              |      0.72 |       0.76 |        1 |      0   | fecha    |
| Dario Naamo         | dario naamo                 |      0.72 |       1    |        0 |      0.5 | fecha    |
| Khoder Kaddour      | khoder kaddour              |      0.68 |       1    |        0 |      0.5 | fecha    |
| Daniel Kerl         | daniel kerl                 |      0.68 |       1    |        0 |      0.5 | fecha    |
| Vojtech Novak       | vojtech novak               |      0.7  |       1    |        0 |      1   | fecha    |
| Bogdan Panchyshyn   | bohdan panchyshyn           |      0.75 |       0.81 |        1 |      0   | fecha    |
| Formose Mendy       | formose jean pierre mendy   |      0.65 |       1    |        0 |      0   | fecha    |
| Pavel Moulis        | pavel moulis                |      0.72 |       1    |        0 |      0.5 | fecha    |
| Will Alves          | william thomas alves        |      0.74 |       0.71 |        1 |      1   | fecha    |
| Vladyslav Pryimak   | vladyslav pryymak           |      0.72 |       0.64 |        1 |      0.5 | fecha    |
| Vasilios Gordeziani | vasilios gordeziani         |      0.65 |       1    |        0 |      0   | fecha    |
| Zak Vyner           | zachary george onyego vyner |      0.66 |       0.84 |        1 |      0   | fecha    |
| Abdihakim Ali       | abdihakin abdulkadir ali    |      0.68 |       0.68 |        1 |      0   | fecha    |
| Stjepan Radeljic    | stjepan radeljic            |      0.7  |       1    |        0 |      1   | fecha    |
| Viktor Baier        | viktor baier                |      0.67 |       1    |        0 |      0.5 | fecha    |
| Dan Kohout          | dan kohout                  |      0.73 |       1    |        0 |      0.5 | fecha    |
| Vladan Novevski     | vladan valda novevski       |      0.72 |       0.95 |        0 |      1   | fecha    |
| Ajak Riak           | ajak chol riak              |      0.72 |       0.95 |        0 |      1   | fecha    |
| Lukas Schweighofer  | lukas schweighofer          |      0.68 |       1    |        0 |      0.5 | fecha    |
| Sergiy Sten         | serhii sten                 |      0.68 |       0.51 |        1 |      1   | fecha    |
| Ayrton Mboko        | ayrton junior mboko sambeya |      0.74 |       0.95 |        1 |      0   | fecha    |
| Chu-young Park      | chu young park              |      0.65 |       1    |        0 |      0   | fecha    |