# Reporte de cobertura de datos


## Transfermarkt: tablas y esquemas

### appearances (1,894,350 filas)

`appearance_id` VARCHAR, `game_id` INTEGER, `player_id` INTEGER, `player_club_id` INTEGER, `player_current_club_id` VARCHAR, `date` DATE, `player_name` VARCHAR, `competition_id` VARCHAR, `yellow_cards` INTEGER, `red_cards` INTEGER, `goals` INTEGER, `assists` INTEGER, `minutes_played` INTEGER

### club_games (177,916 filas)

`game_id` VARCHAR, `club_id` INTEGER, `own_goals` INTEGER, `own_position` INTEGER, `own_manager_name` VARCHAR, `opponent_id` INTEGER, `opponent_goals` INTEGER, `opponent_position` INTEGER, `opponent_manager_name` VARCHAR, `hosting` VARCHAR, `is_win` INTEGER

### clubs (796 filas)

`club_id` VARCHAR, `club_code` VARCHAR, `name` VARCHAR, `domestic_competition_id` VARCHAR, `total_market_value` FLOAT, `squad_size` INTEGER, `average_age` FLOAT, `foreigners_number` INTEGER, `foreigners_percentage` FLOAT, `national_team_players` INTEGER, `stadium_name` VARCHAR, `stadium_seats` INTEGER, `net_transfer_record` VARCHAR, `coach_name` VARCHAR, `last_season` VARCHAR, `filename` VARCHAR, `url` VARCHAR

### competitions (65 filas)

`competition_id` VARCHAR, `competition_code` VARCHAR, `name` VARCHAR, `sub_type` VARCHAR, `type` VARCHAR, `country_id` INTEGER, `country_name` VARCHAR, `domestic_league_code` VARCHAR, `confederation` VARCHAR, `total_clubs` INTEGER, `url` VARCHAR

### countries (124 filas)

`country_id` VARCHAR, `country_name` VARCHAR, `country_code` VARCHAR, `confederation` VARCHAR, `total_clubs` INTEGER, `total_players` INTEGER, `average_age` FLOAT, `url` VARCHAR

### game_events (1,274,469 filas)

`game_event_id` VARCHAR, `date` DATE, `game_id` VARCHAR, `minute` INTEGER, `type` VARCHAR, `club_id` INTEGER, `club_name` VARCHAR, `player_id` INTEGER, `description` VARCHAR, `player_in_id` INTEGER, `player_assist_id` INTEGER

### game_lineups (3,179,016 filas)

`game_lineups_id` VARCHAR, `date` DATE, `game_id` INTEGER, `player_id` INTEGER, `club_id` INTEGER, `player_name` VARCHAR, `type` VARCHAR, `position` VARCHAR, `number` VARCHAR, `team_captain` INTEGER

### games (88,958 filas)

`game_id` VARCHAR, `competition_id` VARCHAR, `season` VARCHAR, `round` VARCHAR, `date` DATE, `home_club_id` INTEGER, `away_club_id` INTEGER, `home_club_goals` INTEGER, `away_club_goals` INTEGER, `home_club_position` INTEGER, `away_club_position` INTEGER, `home_club_manager_name` VARCHAR, `away_club_manager_name` VARCHAR, `stadium` VARCHAR, `attendance` INTEGER, `referee` VARCHAR, `url` VARCHAR, `home_club_formation` VARCHAR, `away_club_formation` VARCHAR, `home_club_name` VARCHAR, `away_club_name` VARCHAR, `aggregate` VARCHAR, `competition_type` VARCHAR

### national_teams (124 filas)

`national_team_id` VARCHAR, `name` VARCHAR, `team_code` VARCHAR, `country_id` VARCHAR, `country_name` VARCHAR, `country_code` VARCHAR, `confederation` VARCHAR, `team_image_url` VARCHAR, `squad_size` INTEGER, `average_age` FLOAT, `foreigners_number` INTEGER, `foreigners_percentage` FLOAT, `total_market_value` INTEGER, `coach_name` VARCHAR, `fifa_ranking` INTEGER, `last_season` VARCHAR, `url` VARCHAR

### player_valuations (656,301 filas)

`player_id` INTEGER, `date` DATE, `market_value_in_eur` INTEGER, `current_club_name` VARCHAR, `current_club_id` INTEGER, `player_club_domestic_competition_id` VARCHAR

### players (50,149 filas)

`player_id` INTEGER, `first_name` VARCHAR, `last_name` VARCHAR, `name` VARCHAR, `last_season` VARCHAR, `current_club_id` VARCHAR, `player_code` VARCHAR, `country_of_birth` VARCHAR, `city_of_birth` VARCHAR, `country_of_citizenship` VARCHAR, `date_of_birth` TIMESTAMP, `sub_position` VARCHAR, `position` VARCHAR, `foot` VARCHAR, `height_in_cm` INTEGER, `contract_expiration_date` TIMESTAMP, `agent_name` VARCHAR, `image_url` VARCHAR, `international_caps` INTEGER, `international_goals` INTEGER, `current_national_team_id` VARCHAR, `url` VARCHAR, `current_club_domestic_competition_id` VARCHAR, `current_club_name` VARCHAR, `market_value_in_eur` INTEGER, `highest_market_value_in_eur` INTEGER

### transfers (175,165 filas)

`player_id` INTEGER, `transfer_date` DATE, `transfer_season` VARCHAR, `from_club_id` INTEGER, `to_club_id` INTEGER, `from_club_name` VARCHAR, `to_club_name` VARCHAR, `transfer_fee` DECIMAL(18,3), `market_value_in_eur` DECIMAL(18,3), `player_name` VARCHAR

### version (1 filas)

`commit_hash` VARCHAR


## Transfermarkt: cobertura de jugadores por liga (jugadores activos ultima temporada)

| liga   | nombre                        |   jugadores |   pct_valor |   pct_contrato |   pct_subposicion |   pct_nacimiento |   valor_total_meur |
|:-------|:------------------------------|------------:|------------:|---------------:|------------------:|-----------------:|-------------------:|
| nan    | nan                           |        2986 |        73.5 |           64.7 |              98.2 |              100 |               1185 |
| ARG1   | torneo-apertura               |         954 |        93.9 |           98.4 |              99.9 |              100 |               1007 |
| MLS1   | major-league-soccer           |         856 |        92.8 |           99.8 |             100   |              100 |               1344 |
| GB1    | premier-league                |         826 |        83.8 |           84.7 |             100   |              100 |              12804 |
| IT1    | serie-a                       |         770 |        81.3 |           84   |             100   |              100 |               5420 |
| ES1    | laliga                        |         748 |        79.5 |           91.7 |             100   |              100 |               5515 |
| JAP1   | j1-league                     |         740 |        85.5 |           69.1 |              97.6 |              100 |                301 |
| TR1    | super-lig                     |         726 |        75.2 |           76   |              99.2 |              100 |               1375 |
| BRA1   | campeonato-brasileiro-serie-a |         706 |        90.2 |           98.3 |             100   |              100 |               2002 |
| MEX1   | liga-mx-clausura              |         674 |        73.6 |           45.4 |              92.9 |              100 |               1027 |
| FR1    | ligue-1                       |         673 |        79.8 |           82.3 |              99.9 |              100 |               4913 |
| NL1    | eredivisie                    |         645 |        82.6 |           84.3 |              99.4 |              100 |               1414 |
| SER1   | super-liga-srbije             |         636 |        74.5 |           67   |             100   |              100 |                377 |
| RO1    | superliga                     |         630 |        75.6 |           53.8 |              99.5 |              100 |                287 |
| SA1    | saudi-pro-league              |         616 |        82.8 |           57.6 |              96.9 |              100 |               1025 |
| PL1    | pko-bp-ekstraklasa            |         615 |        82.4 |           87.3 |             100   |              100 |                422 |
| TS1    | chance-liga                   |         615 |        76.9 |           56.4 |              99.8 |              100 |                470 |
| PO1    | liga-portugal                 |         615 |        87.8 |           89.8 |              99.8 |              100 |               1955 |
| UKR1   | premier-liga                  |         610 |        79.5 |           85.9 |              99.7 |              100 |                519 |
| L1     | bundesliga                    |         610 |        92.1 |           80   |             100   |              100 |               5167 |
| BE1    | jupiler-pro-league            |         567 |        89.4 |           87.1 |              98.9 |              100 |               1332 |
| RU1    | premier-liga                  |         560 |        87.1 |           91.6 |             100   |              100 |               1039 |
| COL1   | nan                           |         550 |        92.7 |           61.3 |              97.6 |              100 |                197 |
| GR1    | super-league-1                |         515 |        87.4 |           78.3 |              99.2 |              100 |                563 |
| SE1    | allsvenskan                   |         457 |        85.3 |           93   |              97.4 |              100 |                245 |
| SC1    | scottish-premiership          |         453 |        84.8 |           71.1 |              99.3 |              100 |                415 |
| RSK1   | k-league-1                    |         452 |        83.8 |           27   |              92.7 |              100 |                121 |
| C1     | super-league                  |         435 |        79.8 |           84.6 |             100   |              100 |                421 |
| NO1    | eliteserien                   |         424 |        91.3 |           97.6 |              99.3 |              100 |                376 |
| KR1    | supersport-hnl                |         421 |        73.6 |           91   |              96.9 |              100 |                246 |
| AUS1   | a-league-men                  |         411 |        84.9 |           73.7 |              98.8 |              100 |                115 |
| A1     | bundesliga                    |         400 |        88.8 |           74.3 |              99.5 |              100 |                479 |
| DK1    | superliga                     |         396 |        86.4 |           88.9 |              99.7 |              100 |                474 |


## Transfermarkt: frescura por tabla

| tabla             | desde      | hasta      |
|:------------------|:-----------|:-----------|
| games             | 2006-06-09 | 2026-07-06 |
| appearances       | 2012-07-03 | 2026-06-28 |
| player_valuations | 2000-01-20 | 2026-06-12 |
| transfers         | 1993-07-01 | 2030-06-30 |


## Transfermarkt: partidos y alineaciones por liga y temporada (ultimas 4)

Error: Binder Error: No function matches the given name and argument types '-(VARCHAR, INTEGER_LITERAL)'. You might need to add explicit type casts.
	Candidate functions:
	"-"(x TINYINT, /) -> TINYINT
	"-"("left" TINYINT, "right" TINYINT, /) -> TINYINT
	"-"(x SMALLINT, /) -> SMALLINT
	"-"("left" SMALLINT, "right" SMALLINT, /) -> SMALLINT
	"-"(x INTEGER, /) -> INTEGER
	"-"("left" INTEGER, "right" INTEGER, /) -> INTEGER
	"-"(x BIGINT, /) -> BIGINT
	"-"("left" BIGINT, "right" BIGINT, /) -> BIGINT
	"-"(x HUGEINT, /) -> HUGEINT
	"-"("left" HUGEINT, "right" HUGEINT, /) -> HUGEINT
	"-"(x FLOAT, /) -> FLOAT
	"-"("left" FLOAT, "right" FLOAT, /) -> FLOAT
	"-"(x DOUBLE, /) -> DOUBLE
	"-"("left" DOUBLE, "right" DOUBLE, /) -> DOUBLE
	"-"(x DECIMAL, /) -> DECIMAL
	"-"("left" DECIMAL, "right" DECIMAL, /) -> DECIMAL
	"-"(x UTINYINT, /) -> UTINYINT
	"-"("left" UTINYINT, "right" UTINYINT, /) -> UTINYINT
	"-"(x USMALLINT, /) -> USMALLINT
	"-"("left" USMALLINT, "right" USMALLINT, /) -> USMALLINT
	"-"(x UINTEGER, /) -> UINTEGER
	"-"("left" UINTEGER, "right" UINTEGER, /) -> UINTEGER
	"-"(x UBIGINT, /) -> UBIGINT
	"-"("left" UBIGINT, "right" UBIGINT, /) -> UBIGINT
	"-"(x UHUGEINT, /) -> UHUGEINT
	"-"("left" UHUGEINT, "right" UHUGEINT, /) -> UHUGEINT
	"-"(x BIGNUM, /) -> BIGNUM
	"-"("left" BIGNUM, "right" BIGNUM, /) -> BIGNUM
	"-"("left" DATE, "right" DATE, /) -> BIGINT
	"-"("left" DATE, "right" INTEGER, /) -> DATE
	"-"("left" TIMESTAMP, "right" TIMESTAMP, /) -> INTERVAL
	"-"("left" INTERVAL, "right" INTERVAL, /) -> INTERVAL
	"-"("left" DATE, "right" INTERVAL, /) -> TIMESTAMP
	"-"("left" TIME, "right" INTERVAL, /) -> TIME
	"-"("left" TIMESTAMP, "right" INTERVAL, /) -> TIMESTAMP
	"-"("left" TIME WITH TIME ZONE, "right" INTERVAL, /) -> TIME WITH TIME ZONE
	"-"(x INTERVAL, /) -> INTERVAL
	"-"("left" TIMESTAMP WITH TIME ZONE, "right" INTERVAL, /) -> TIMESTAMP WITH TIME ZONE
	"-"("left" TIMESTAMP WITH TIME ZONE, "right" TIMESTAMP WITH TIME ZONE, /) -> INTERVAL


LINE 6:     WHERE g.season >= (SELECT MAX(season) - 3 FROM games)
                                                       ^

## Transfermarkt: traspasos con monto por temporada

| transfer_season   |   traspasos |   con_monto |
|:------------------|------------:|------------:|
| 99/00             |          32 |           0 |
| 98/99             |          24 |           0 |
| 97/98             |           9 |           1 |
| 96/97             |           6 |           0 |
| 95/96             |           4 |           0 |
| 94/95             |           4 |           0 |
| 93/94             |           2 |           0 |
| 27/28             |          13 |           0 |
| 26/27             |        1706 |         157 |
| 25/26             |       15676 |        2367 |
| 24/25             |       16686 |        2284 |
| 23/24             |       17379 |        2083 |


## Transfermarkt: muestra Liga MX (10 jugadores mas valiosos)

| name                | current_club_name     | sub_position       | date_of_birth       | country_of_citizenship   |   market_value_in_eur | contract_expiration_date   |
|:--------------------|:----------------------|:-------------------|:--------------------|:-------------------------|----------------------:|:---------------------------|
| Armando González    | Deportivo Guadalajara | Centre-Forward     | 2003-04-20 00:00:00 | Mexico                   |              15000000 | 2029-12-31 00:00:00        |
| Germán Berterame    | CF Monterrey          | Centre-Forward     | 1998-11-13 00:00:00 | Mexico                   |              12000000 | 2029-06-30 00:00:00        |
| Érik Lira           | CD Cruz Azul          | Defensive Midfield | 2000-05-08 00:00:00 | Mexico                   |              12000000 | 2029-06-30 00:00:00        |
| Allan Saint-Maximin | CF América            | Left Winger        | 1997-03-12 00:00:00 | France                   |              10000000 | NaT                        |
| Gilberto Mora       | Club Tijuana          | Attacking Midfield | 2008-10-14 00:00:00 | Mexico                   |              10000000 | 2029-06-30 00:00:00        |
| Álex Zendejas       | CF América            | Right Winger       | 1998-02-07 00:00:00 | United States            |              10000000 | 2027-06-30 00:00:00        |
| Marcel Ruiz         | Deportivo Toluca      | Central Midfield   | 2000-10-26 00:00:00 | Mexico                   |              10000000 | 2027-06-30 00:00:00        |
| José Paradela       | CD Cruz Azul          | Central Midfield   | 1998-12-15 00:00:00 | Argentina                |               9000000 | 2029-06-30 00:00:00        |
| Juan Brunetta       | Tigres UANL           | Attacking Midfield | 1997-05-12 00:00:00 | Argentina                |               9000000 | 2027-12-31 00:00:00        |
| Brian Rodríguez     | CF América            | Left Winger        | 2000-05-20 00:00:00 | Uruguay                  |               8000000 | 2029-06-30 00:00:00        |


## StatsBomb Open Data: competiciones gratuitas

| competition_name        | season_name   | competition_gender   | country_name              |
|:------------------------|:--------------|:---------------------|:--------------------------|
| FA Women's Super League | 2018/2019     | female               | England                   |
| FA Women's Super League | 2019/2020     | female               | England                   |
| FA Women's Super League | 2020/2021     | female               | England                   |
| FA Women's Super League | 2023/2024     | female               | England                   |
| Frauen Bundesliga       | 2023/2024     | female               | Germany                   |
| Liga F                  | 2023/2024     | female               | Spain                     |
| NWSL                    | 2018          | female               | United States of America  |
| NWSL                    | 2023          | female               | United States of America  |
| Serie A Women           | 2023/2024     | female               | Italy                     |
| UEFA Women's Euro       | 2022          | female               | Europe                    |
| UEFA Women's Euro       | 2025          | female               | Europe                    |
| Women's World Cup       | 2019          | female               | International             |
| Women's World Cup       | 2023          | female               | International             |
| 1. Bundesliga           | 2015/2016     | male                 | Germany                   |
| 1. Bundesliga           | 2023/2024     | male                 | Germany                   |
| African Cup of Nations  | 2023          | male                 | Africa                    |
| Champions League        | 1970/1971     | male                 | Europe                    |
| Champions League        | 1971/1972     | male                 | Europe                    |
| Champions League        | 1972/1973     | male                 | Europe                    |
| Champions League        | 1999/2000     | male                 | Europe                    |
| Champions League        | 2003/2004     | male                 | Europe                    |
| Champions League        | 2004/2005     | male                 | Europe                    |
| Champions League        | 2006/2007     | male                 | Europe                    |
| Champions League        | 2008/2009     | male                 | Europe                    |
| Champions League        | 2009/2010     | male                 | Europe                    |
| Champions League        | 2010/2011     | male                 | Europe                    |
| Champions League        | 2011/2012     | male                 | Europe                    |
| Champions League        | 2012/2013     | male                 | Europe                    |
| Champions League        | 2013/2014     | male                 | Europe                    |
| Champions League        | 2014/2015     | male                 | Europe                    |
| Champions League        | 2015/2016     | male                 | Europe                    |
| Champions League        | 2016/2017     | male                 | Europe                    |
| Champions League        | 2017/2018     | male                 | Europe                    |
| Champions League        | 2018/2019     | male                 | Europe                    |
| Copa America            | 2024          | male                 | South America             |
| Copa del Rey            | 1977/1978     | male                 | Spain                     |
| Copa del Rey            | 1982/1983     | male                 | Spain                     |
| Copa del Rey            | 1983/1984     | male                 | Spain                     |
| FIFA U20 World Cup      | 1979          | male                 | International             |
| FIFA World Cup          | 1958          | male                 | International             |
| FIFA World Cup          | 1962          | male                 | International             |
| FIFA World Cup          | 1970          | male                 | International             |
| FIFA World Cup          | 1974          | male                 | International             |
| FIFA World Cup          | 1986          | male                 | International             |
| FIFA World Cup          | 1990          | male                 | International             |
| FIFA World Cup          | 2018          | male                 | International             |
| FIFA World Cup          | 2022          | male                 | International             |
| Indian Super league     | 2021/2022     | male                 | India                     |
| La Liga                 | 1973/1974     | male                 | Spain                     |
| La Liga                 | 2004/2005     | male                 | Spain                     |
| La Liga                 | 2005/2006     | male                 | Spain                     |
| La Liga                 | 2006/2007     | male                 | Spain                     |
| La Liga                 | 2007/2008     | male                 | Spain                     |
| La Liga                 | 2008/2009     | male                 | Spain                     |
| La Liga                 | 2009/2010     | male                 | Spain                     |
| La Liga                 | 2010/2011     | male                 | Spain                     |
| La Liga                 | 2011/2012     | male                 | Spain                     |
| La Liga                 | 2012/2013     | male                 | Spain                     |
| La Liga                 | 2013/2014     | male                 | Spain                     |
| La Liga                 | 2014/2015     | male                 | Spain                     |
| La Liga                 | 2015/2016     | male                 | Spain                     |
| La Liga                 | 2016/2017     | male                 | Spain                     |
| La Liga                 | 2017/2018     | male                 | Spain                     |
| La Liga                 | 2018/2019     | male                 | Spain                     |
| La Liga                 | 2019/2020     | male                 | Spain                     |
| La Liga                 | 2020/2021     | male                 | Spain                     |
| Liga Profesional        | 1981          | male                 | Argentina                 |
| Liga Profesional        | 1997/1998     | male                 | Argentina                 |
| Ligue 1                 | 2015/2016     | male                 | France                    |
| Ligue 1                 | 2021/2022     | male                 | France                    |
| Ligue 1                 | 2022/2023     | male                 | France                    |
| Major League Soccer     | 2023          | male                 | United States of America  |
| North American League   | 1977          | male                 | North and Central America |
| Premier League          | 2003/2004     | male                 | England                   |
| Premier League          | 2015/2016     | male                 | England                   |
| Serie A                 | 1986/1987     | male                 | Italy                     |
| Serie A                 | 2015/2016     | male                 | Italy                     |
| UEFA Euro               | 2020          | male                 | Europe                    |
| UEFA Euro               | 2024          | male                 | Europe                    |
| UEFA Europa League      | 1988/1989     | male                 | Europe                    |


## football-data.co.uk: archivos y columnas de momios

| archivo       |   filas |   temporadas |   cols_momios |
|:--------------|--------:|-------------:|--------------:|
| 2526/B1.csv   |     311 |            1 |            48 |
| 2526/D1.csv   |     306 |            1 |            48 |
| 2526/E0.csv   |     380 |            1 |            48 |
| 2526/E1.csv   |     552 |            1 |            48 |
| 2526/F1.csv   |     306 |            1 |            48 |
| 2526/G1.csv   |     236 |            1 |            48 |
| 2526/I1.csv   |     380 |            1 |            48 |
| 2526/N1.csv   |     306 |            1 |            48 |
| 2526/P1.csv   |     306 |            1 |            48 |
| 2526/SC0.csv  |     228 |            1 |            48 |
| 2526/SP1.csv  |     380 |            1 |            48 |
| 2526/T1.csv   |     306 |            1 |            48 |
| extra/ARG.csv |    6444 |           16 |            12 |
| extra/AUT.csv |    2698 |           15 |            12 |
| extra/BRA.csv |    5639 |           15 |            12 |
| extra/DNK.csv |    3024 |           15 |            12 |
| extra/JPN.csv |    4643 |           15 |            12 |
| extra/MEX.csv |    4779 |           15 |            12 |
| extra/NOR.csv |    3574 |           15 |            12 |
| extra/POL.csv |    4188 |           15 |            12 |
| extra/RUS.csv |    3416 |           15 |             9 |
| extra/SWE.csv |    3584 |           15 |            12 |
| extra/SWZ.csv |    2741 |           15 |            12 |
| extra/USA.csv |    6282 |           15 |            12 |


## API-Football: diagnostico

```json
{
  "archivo": "jugadores_liga_mx_2025.json",
  "resultados": 0,
  "errores": {
    "plan": "Free plans do not have access to this season, try from 2022 to 2024."
  }
}
```
```json
{
  "archivo": "liga_mx.json",
  "resultados": 1,
  "errores": [],
  "temporadas": [
    {
      "anio": 2023,
      "actual": false,
      "jugadores": true,
      "stats_jugador": true
    },
    {
      "anio": 2024,
      "actual": false,
      "jugadores": true,
      "stats_jugador": true
    },
    {
      "anio": 2025,
      "actual": false,
      "jugadores": true,
      "stats_jugador": true
    },
    {
      "anio": 2026,
      "actual": true,
      "jugadores": true,
      "stats_jugador": true
    }
  ]
}
```
```json
{
  "archivo": "premier.json",
  "resultados": 1,
  "errores": [],
  "temporadas": [
    {
      "anio": 2023,
      "actual": false,
      "jugadores": true,
      "stats_jugador": true
    },
    {
      "anio": 2024,
      "actual": false,
      "jugadores": true,
      "stats_jugador": true
    },
    {
      "anio": 2025,
      "actual": false,
      "jugadores": true,
      "stats_jugador": true
    },
    {
      "anio": 2026,
      "actual": true,
      "jugadores": true,
      "stats_jugador": true
    }
  ]
}
```
```json
{
  "archivo": "status.json",
  "resultados": 0,
  "errores": [],
  "plan": "Free",
  "limite_diario": 100
}
```