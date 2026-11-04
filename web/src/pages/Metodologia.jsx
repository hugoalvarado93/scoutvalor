import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useIdioma } from '../i18n.jsx';
import { cargar, fecha, miles } from '../datos.js';
import { BarrasH, Calibracion, Dispersion, Divergente, Proporciones } from '../components/Graficas.jsx';

const NOMBRES_LIGA = {
  GB1: 'Premier League', ES1: 'LaLiga', IT1: 'Serie A', L1: 'Bundesliga', FR1: 'Ligue 1', NL1: 'Eredivisie', PO1: 'Primeira Liga',
  BE1: 'Jupiler Pro League', TR1: 'Süper Lig', GR1: 'Super League Grecia', SC1: 'Scottish Premiership', RU1: 'Liga Premier Rusia',
  UKR1: 'Liga Premier Ucrania', DK1: 'Superliga Dinamarca', A1: 'Bundesliga Austria', C1: 'Super League Suiza', PL1: 'Ekstraklasa',
  SE1: 'Allsvenskan', NO1: 'Eliteserien', TS1: 'Chance Liga', KR1: 'HNL', SER1: 'Superliga Serbia', RO1: 'Superliga Rumania',
  BRA1: 'Brasileirão', ARG1: 'Liga Profesional', MLS1: 'MLS', MEX1: 'Liga MX', COL1: 'Liga BetPlay', SA1: 'Saudi Pro League',
  JAP1: 'J1 League', RSK1: 'K League 1', AUS1: 'A-League',
};

const C = {
  es: {
    titulo: 'Metodología',
    intro: 'Cómo pasamos de cuatro fuentes públicas a un radar de jugadores infravalorados, un simulador de fichajes y un buscador de reemplazos. Todo el proceso corre solo cada semana y cada cifra de esta página sale de la corrida más reciente.',
    indice: 'En esta página',
    secciones: ['El flujo de datos', 'Fuentes', 'Limpieza', 'Vinculación', 'Módulo A · Valor', 'Módulo C · Fichajes', 'Módulo B · Reemplazos', 'Limitaciones', 'Glosario'],
    tiles: ['Fuentes de datos', 'Jugadores vinculados entre fuentes', 'Traspasos analizados', 'Actualización'],
    cadaLunes: 'Cada lunes',
    flujoTxt: 'Seis etapas, de los datos crudos a lo que ves en el portal. Las etapas 2 a 5 corren en servidores de GitHub; el portal se publica en Cloudflare.',
    pasos: [
      ['Fuentes', 'Transfermarkt, API-Football, StatsBomb y football-data.co.uk', 'Datos públicos'],
      ['Ingesta', 'Descarga automática y control de cobertura por liga y temporada', 'Python · GitHub Actions'],
      ['Limpieza y vinculación', 'Normaliza nombres, países y clubes; une al mismo jugador entre fuentes', 'pandas · scikit-learn'],
      ['Modelos', 'Valor estimado (A), éxito de fichajes (C) y perfiles para reemplazos (B)', 'Gradient boosting · regresión logística'],
      ['Exportación', 'Convierte los resultados en archivos JSON compactos', 'Archivos estáticos'],
      ['Portal', 'React lee los archivos y calcula filtros y simulaciones en tu navegador', 'Cloudflare Pages'],
    ],
    ciclo: 'Ciclo semanal', cicloPasos: ['Lunes 3:17 am · descarga de API-Football', 'Vinculación y reentrenamiento de modelos', 'Publicación automática del portal'],
    fuentesTxt: 'Ninguna fuente basta por sí sola: Transfermarkt sabe cuánto vale y cuánto costó un jugador; API-Football sabe cómo juega hoy. Las combinamos.',
    fuentesTarjetas: [
      ['Transfermarkt', 'Valor de mercado, contratos, historial de traspasos y minutos por partido.', 'Conjunto de datos abierto (CC0), corte de junio 2026', 'tm'],
      ['API-Football', 'Estadísticas por jugador y temporada, plantillas 2026-27, fotos y escudos.', 'Plan de pago, actualización semanal', 'af'],
      ['StatsBomb Open Data', 'Eventos de torneos de selecciones (Copa América, Eurocopa, Mundial).', 'Gratuito con atribución', null],
      ['football-data.co.uk', 'Resultados y momios de apuestas para estimar la fuerza de las ligas.', 'Gratuito con atribución', null],
    ],
    filasTm: { players: 'jugadores', player_valuations: 'valuaciones históricas', transfers: 'traspasos', appearances: 'apariciones en partido' },
    filasAf: { jugadores_temporada: 'registros jugador-temporada', plantillas_actuales: 'jugadores en plantillas actuales', equipos: 'equipos' },
    matrizTitulo: 'Qué aporta cada fuente',
    matrizFilas: ['Valor de mercado', 'Contratos', 'Historial de traspasos', 'Minutos por partido', 'Estadísticas por 90 min', 'Plantillas 2026-27', 'Fotos y escudos', 'Fuerza de las ligas'],
    matriz: [[1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [1, 0, 0, 1]],
    limpiezaTxt: 'Antes de cruzar fuentes hay que hablar el mismo idioma. Estas son las reglas que aplicamos:',
    limpieza: [
      ['Nombres', 'Se quitan acentos, guiones y mayúsculas: «André-Pierre Gignac» y «andre pierre gignac» quedan iguales.'],
      ['Países', 'Cada fuente escribe distinto («USA», «United States», «Korea Republic»). Un diccionario los unifica.'],
      ['Confederaciones', 'Transfermarkt junta a todo el continente americano; separamos CONMEBOL (10 países) de CONCACAF.'],
      ['Clubes', 'Se eliminan prefijos como FC, CF, Club o Deportivo para comparar «CF Monterrey» con «Monterrey».'],
      ['Club actual', 'Transfermarkt se congeló en julio de 2026; si hay un traspaso posterior registrado, manda sobre el club guardado.'],
      ['Valores faltantes', 'Un contrato sin dato se muestra como «Sin dato», nunca se inventa. Los modelos manejan los vacíos de forma explícita.'],
    ],
    vincTxt: 'El mismo jugador aparece con nombres distintos en cada fuente. Para unirlos usamos una técnica de minería de datos llamada vinculación de registros (record linkage).',
    vincPasos: [
      ['Bloqueo', 'Solo se comparan jugadores nacidos el mismo día. Así pasamos de miles de millones de pares posibles a unos cuantos miles.'],
      ['Puntaje', 'Cada par candidato recibe una calificación de 0 a 1 combinando cuatro criterios.'],
      ['Asignación uno a uno', 'De mayor a menor puntaje, cada jugador se queda con un solo par; se acepta si supera {u}.'],
      ['Segunda pasada', 'Quien no tiene fecha de nacimiento entra si su nombre es casi idéntico y coinciden país y club.'],
    ],
    pesosTitulo: 'Cómo se calcula el puntaje', pesosNombres: ['Nombre', 'Nacionalidad', 'Club', 'Estatura'],
    ejemplosTitulo: 'Ejemplos reales', ejCols: ['Transfermarkt', 'API-Football', 'Nombre', 'País', 'Club', 'Estatura', 'Puntaje'],
    vincResultado: 'De {a} jugadores activos, {b} quedaron vinculados ({p}).',
    coberturaTitulo: 'Porcentaje de jugadores activos vinculados, por liga',
    coberturaNota: 'Las ligas con alfabetos distintos (Corea, Japón, Ucrania) vinculan menos porque los nombres se transliteran de forma diferente.',
    bandasTitulo: 'Confianza de los pares aceptados', liga: 'Liga', pct: '% vinculado', banda: 'Puntaje', pares: 'Pares',
    aTxt: 'Estimamos cuánto «debería» valer cada jugador según lo que hace en la cancha y su contexto, y lo comparamos con su valor de mercado.',
    aPasos: [
      ['Universo', 'Jugadores activos con valor de mercado y al menos 450 minutos en sus dos últimas temporadas.'],
      ['Variables', 'Edad, liga, club, contrato, selección, trayectoria de valor y rendimiento por 90 minutos.'],
      ['Modelo', 'Gradient boosting: cientos de árboles de decisión pequeños, cada uno corrige los errores del anterior.'],
      ['Validación cruzada', 'Los jugadores se dividen en 5 grupos; cada grupo se valora con un modelo entrenado con los otros 4.'],
      ['Brecha', '(valor estimado − valor de mercado) ÷ valor de mercado. Al radar solo entran jugadores con 900+ minutos.'],
    ],
    cvTitulo: 'Validación cruzada de 5 particiones', cvEntrena: 'Entrena', cvValora: 'Valora', ronda: 'Ronda',
    cvNota: 'Ningún jugador es valorado por un modelo que lo haya visto: por eso la brecha no está inflada.',
    r2: 'R² fuera de muestra', r2Base: 'Línea base (solo liga)', mae: 'Error mediano', enTope: 'En el tope de ×3',
    r2Exp: 'Explica {p} de las diferencias de valor entre jugadores.', baseExp: 'Lo que explica saber solo la liga.', maeExp: 'La mitad de las estimaciones fallan por menos.', topeExp: 'Estimaciones recortadas para evitar extremos.',
    importanciaTitulo: 'Qué pesa más en el valor estimado', importanciaNota: 'Importancia por permutación: cuánto empeora el R² si se revuelven al azar las variables de ese grupo.',
    dispersionTitulo: 'Valor real contra valor estimado', valorReal: 'Valor de mercado real', valorEst: 'Valor estimado',
    cTxt: 'Para cada traspaso histórico preguntamos: ¿funcionó? Con miles de respuestas, el modelo aprende qué tienen en común los fichajes que salieron bien.',
    etiquetaTitulo: 'Cómo se define un fichaje exitoso',
    linea: ['Traspaso', 'Primera temporada completa en el club', 'Fin de temporada'],
    condiciones: ['≥ 1,500 minutos de liga', 'Valor de mercado ≥ 90% del valor al fichar'],
    tasaBase: 'Tasa base: solo {p} de los traspasos cumplen ambas condiciones.',
    cVars: 'Variables: edad, valor y monto, minutos de la temporada previa, nivel de liga y club (origen y destino), tipo de movimiento (mismo país, mismo idioma, misma confederación), compatriotas en la plantilla, competencia en su posición y posición.',
    aucLr: 'Regresión logística (publicada)', aucGb: 'Gradient boosting (referencia)', aucExp: 'AUC: probabilidad de que el modelo califique más alto a un fichaje exitoso que a uno fallido (0.5 = azar, 1 = perfecto).',
    porQueLr: 'Publicamos la regresión logística aunque el gradient boosting acierta un poco más: es interpretable, permite mostrar cuánto aporta cada factor y corre en tu navegador.',
    calTitulo: '¿Las probabilidades son confiables? Calibración por deciles', calNota: 'Los traspasos se ordenan por probabilidad predicha y se dividen en 10 grupos iguales. Si el anillo y el punto coinciden, cuando el modelo dice 30% ocurre cerca de 30%.',
    coefTitulo: 'Qué asocia el modelo con el éxito', coefNota: 'Coeficientes estandarizados: verde aumenta la probabilidad, naranja la reduce. Es correlación, no causalidad.',
    hallazgo: 'Hallazgo: una vez que se toman en cuenta la edad, los minutos, el monto y el nivel del club, compartir idioma o confederación casi no cambia la probabilidad. Lo que más pesa es cuánto se pagó y cuánto jugaba antes.',
    bTxt: 'Para cada club armamos su XI de referencia y, por cada puesto, buscamos el mejor reemplazo combinando cuatro criterios que puedes reponderar en la página.',
    xiRegla: 'XI de referencia: la formación más usada en sus últimos 15 partidos y, para cada puesto, el jugador del plantel actual con más minutos en una posición compatible.',
    pesosB: ['Similitud', 'Adaptación', 'Asequibilidad', 'Calidad'],
    bCriterios: [
      ['Similitud', 'Perfil estadístico por 90 minutos (goles, asistencias, pases clave, tiros, regates, entradas, intercepciones, duelos, calificación, atajadas) estandarizado dentro de su grupo de posición. Más cerca del titular = más similar.'],
      ['Adaptación', 'La probabilidad del modelo de fichajes (módulo C) para ese jugador en ese club.'],
      ['Asequibilidad', 'Su valor contra el percentil 90 de lo que el club ha pagado por un fichaje. Un contrato que vence en 12 meses o menos suma puntos.'],
      ['Calidad', 'Percentil de su calificación de API-Football frente a jugadores de su misma posición.'],
    ],
    bFiltro: 'Por defecto se excluyen jugadores mayores de 32 años, con menos de 900 minutos o con un valor mayor a 2.5 veces lo que el club suele pagar.',
    limitaciones: [
      ['Transfermarkt está congelado', 'El conjunto abierto dejó de actualizarse en julio de 2026. Las plantillas y estadísticas actuales vienen de API-Football, pero valores y contratos tienen ese corte.'],
      ['Sin minutos de Liga MX ni Argentina', 'Transfermarkt no publica minutos por partido de esas ligas, así que el modelo de fichajes aprende sobre todo de movimientos europeos.'],
      ['El valor de mercado es una estimación', 'Transfermarkt lo calcula con su comunidad; no es un precio de venta. «Infravalorado» significa «respecto a Transfermarkt».'],
      ['Correlación, no causalidad', 'Los modelos describen qué fichajes funcionaron en el pasado. No garantizan resultados ni capturan lesiones, vestidor o estilo del entrenador.'],
      ['Contratos incompletos', 'En Liga MX solo hay fecha de contrato para cerca de la mitad de los jugadores.'],
      ['Imágenes de terceros', 'Fotos y escudos vienen de API-Football y pertenecen a sus titulares; se usan solo para identificar.'],
    ],
    glosario: [
      ['Por 90 minutos', 'Una estadística dividida entre los minutos jugados y multiplicada por 90, para comparar a titulares con suplentes.'],
      ['Vinculación de registros', 'Técnica para identificar el mismo objeto (aquí, un jugador) en dos bases de datos sin un identificador común.'],
      ['Gradient boosting', 'Modelo que suma muchos árboles de decisión pequeños, cada uno corrigiendo los errores del anterior.'],
      ['Regresión logística', 'Modelo que convierte una suma ponderada de variables en una probabilidad entre 0 y 1.'],
      ['Validación cruzada', 'Evaluar un modelo con datos que no vio al entrenar, rotando qué parte se usa para probar.'],
      ['R²', 'Proporción de la variación que el modelo explica (0 = nada, 1 = todo).'],
      ['AUC', 'Capacidad de un modelo para ordenar casos positivos por encima de negativos (0.5 = azar).'],
      ['Calibración', 'Qué tanto coinciden las probabilidades predichas con lo que realmente ocurre.'],
      ['Estandarizar (z)', 'Restar el promedio y dividir entre la desviación estándar, para comparar variables con escalas distintas.'],
    ],
    inspirado: 'Inspirado en el modelo de reclutamiento del Brighton & Hove Albion: usar datos para encontrar talento que el mercado todavía no ve, y verificar después con ojos de scout.',
    actualizado: 'Cifras de la corrida del {f}.', ir: 'Ir al radar',
  },
  en: {
    titulo: 'Methodology',
    intro: 'How we go from four public sources to an undervalued-player radar, a transfer simulator and a replacement finder. The whole process runs on its own every week, and every figure on this page comes from the latest run.',
    indice: 'On this page',
    secciones: ['Data flow', 'Sources', 'Cleaning', 'Linking', 'Module A · Value', 'Module C · Transfers', 'Module B · Replacements', 'Limitations', 'Glossary'],
    tiles: ['Data sources', 'Players linked across sources', 'Transfers analysed', 'Updates'],
    cadaLunes: 'Every Monday',
    flujoTxt: 'Six stages, from raw data to what you see on the portal. Stages 2 to 5 run on GitHub servers; the portal is published on Cloudflare.',
    pasos: [
      ['Sources', 'Transfermarkt, API-Football, StatsBomb and football-data.co.uk', 'Public data'],
      ['Ingestion', 'Automatic download and coverage checks by league and season', 'Python · GitHub Actions'],
      ['Cleaning & linking', 'Normalises names, countries and clubs; joins the same player across sources', 'pandas · scikit-learn'],
      ['Models', 'Estimated value (A), transfer success (C) and profiles for replacements (B)', 'Gradient boosting · logistic regression'],
      ['Export', 'Turns results into compact JSON files', 'Static files'],
      ['Portal', 'React reads the files and computes filters and simulations in your browser', 'Cloudflare Pages'],
    ],
    ciclo: 'Weekly cycle', cicloPasos: ['Monday 3:17 am · API-Football download', 'Linking and model retraining', 'Automatic portal publishing'],
    fuentesTxt: 'No single source is enough: Transfermarkt knows what a player is worth and what he cost; API-Football knows how he plays today. We combine them.',
    fuentesTarjetas: [
      ['Transfermarkt', 'Market value, contracts, transfer history and per-match minutes.', 'Open dataset (CC0), June 2026 cut-off', 'tm'],
      ['API-Football', 'Player stats by season, 2026-27 squads, photos and crests.', 'Paid plan, weekly updates', 'af'],
      ['StatsBomb Open Data', 'Event data from national-team tournaments (Copa América, Euro, World Cup).', 'Free with attribution', null],
      ['football-data.co.uk', 'Results and betting odds to estimate league strength.', 'Free with attribution', null],
    ],
    filasTm: { players: 'players', player_valuations: 'historical valuations', transfers: 'transfers', appearances: 'match appearances' },
    filasAf: { jugadores_temporada: 'player-season records', plantillas_actuales: 'players in current squads', equipos: 'teams' },
    matrizTitulo: 'What each source contributes',
    matrizFilas: ['Market value', 'Contracts', 'Transfer history', 'Per-match minutes', 'Per-90 stats', '2026-27 squads', 'Photos and crests', 'League strength'],
    matriz: [[1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [1, 0, 0, 1]],
    limpiezaTxt: 'Before crossing sources they need to speak the same language. These are the rules we apply:',
    limpieza: [
      ['Names', 'Accents, hyphens and capitals are removed: “André-Pierre Gignac” and “andre pierre gignac” become identical.'],
      ['Countries', 'Each source spells them differently (“USA”, “United States”, “Korea Republic”). A dictionary unifies them.'],
      ['Confederations', 'Transfermarkt lumps the whole Americas together; we split CONMEBOL (10 countries) from CONCACAF.'],
      ['Clubs', 'Prefixes such as FC, CF, Club or Deportivo are dropped to compare “CF Monterrey” with “Monterrey”.'],
      ['Current club', 'Transfermarkt froze in July 2026; when a later transfer is recorded, it overrides the stored club.'],
      ['Missing values', 'A missing contract is shown as “No data”, never invented. Models handle gaps explicitly.'],
    ],
    vincTxt: 'The same player appears under different names in each source. To join them we use a data-mining technique called record linkage.',
    vincPasos: [
      ['Blocking', 'Only players born on the same day are compared. That takes us from billions of possible pairs to a few thousand.'],
      ['Scoring', 'Each candidate pair gets a 0-to-1 score combining four criteria.'],
      ['One-to-one assignment', 'From highest to lowest score, each player keeps a single pair; it is accepted above {u}.'],
      ['Second pass', 'Players without a birth date get in if their name is near-identical and country and club match.'],
    ],
    pesosTitulo: 'How the score is computed', pesosNombres: ['Name', 'Nationality', 'Club', 'Height'],
    ejemplosTitulo: 'Real examples', ejCols: ['Transfermarkt', 'API-Football', 'Name', 'Country', 'Club', 'Height', 'Score'],
    vincResultado: 'Of {a} active players, {b} were linked ({p}).',
    coberturaTitulo: 'Share of active players linked, by league',
    coberturaNota: 'Leagues with other alphabets (Korea, Japan, Ukraine) link less because names are transliterated differently.',
    bandasTitulo: 'Confidence of accepted pairs', liga: 'League', pct: '% linked', banda: 'Score', pares: 'Pairs',
    aTxt: 'We estimate what each player “should” be worth given what he does on the pitch and his context, and compare it with his market value.',
    aPasos: [
      ['Universe', 'Active players with a market value and at least 450 minutes over their last two seasons.'],
      ['Variables', 'Age, league, club, contract, national team, value trajectory and per-90 performance.'],
      ['Model', 'Gradient boosting: hundreds of small decision trees, each one correcting the errors of the previous.'],
      ['Cross-validation', 'Players are split into 5 groups; each group is valued by a model trained on the other 4.'],
      ['Gap', '(estimated value − market value) ÷ market value. Only players with 900+ minutes enter the radar.'],
    ],
    cvTitulo: '5-fold cross-validation', cvEntrena: 'Train', cvValora: 'Value', ronda: 'Round',
    cvNota: 'No player is valued by a model that has seen him: that is why the gap is not inflated.',
    r2: 'Out-of-sample R²', r2Base: 'Baseline (league only)', mae: 'Median error', enTope: 'At the ×3 cap',
    r2Exp: 'Explains {p} of the value differences between players.', baseExp: 'What knowing only the league explains.', maeExp: 'Half of the estimates miss by less.', topeExp: 'Estimates capped to avoid extremes.',
    importanciaTitulo: 'What drives the estimated value', importanciaNota: 'Permutation importance: how much R² drops when that group of variables is randomly shuffled.',
    dispersionTitulo: 'Actual versus estimated value', valorReal: 'Actual market value', valorEst: 'Estimated value',
    cTxt: 'For every historical transfer we ask: did it work? With thousands of answers, the model learns what successful signings have in common.',
    etiquetaTitulo: 'How a successful signing is defined',
    linea: ['Transfer', 'First full season at the club', 'End of season'],
    condiciones: ['≥ 1,500 league minutes', 'Market value ≥ 90% of value at signing'],
    tasaBase: 'Base rate: only {p} of transfers meet both conditions.',
    cVars: 'Variables: age, value and fee, minutes the previous season, league and club level (origin and destination), type of move (same country, same language, same confederation), compatriots in the squad, competition for his position, and position.',
    aucLr: 'Logistic regression (published)', aucGb: 'Gradient boosting (reference)', aucExp: 'AUC: the chance the model scores a successful signing above a failed one (0.5 = chance, 1 = perfect).',
    porQueLr: 'We publish the logistic regression even though gradient boosting is slightly more accurate: it is interpretable, lets us show how much each factor contributes, and runs in your browser.',
    calTitulo: 'Are the probabilities reliable? Calibration by decile', calNota: 'Transfers are sorted by predicted probability and split into 10 equal groups. When ring and dot meet, a 30% prediction happens about 30% of the time.',
    coefTitulo: 'What the model associates with success', coefNota: 'Standardised coefficients: green raises the probability, orange lowers it. Correlation, not causation.',
    hallazgo: 'Finding: once age, minutes, fee and club level are accounted for, sharing a language or confederation barely changes the probability. What matters most is how much was paid and how much he played before.',
    bTxt: 'For every club we build a reference XI and, for each position, look for the best replacement by combining four criteria you can re-weight on the page.',
    xiRegla: 'Reference XI: the most used formation in the last 15 matches and, for each position, the current squad player with the most minutes in a compatible position.',
    pesosB: ['Similarity', 'Adaptability', 'Affordability', 'Quality'],
    bCriterios: [
      ['Similarity', 'Per-90 statistical profile (goals, assists, key passes, shots, dribbles, tackles, interceptions, duels, rating, saves) standardised within his position group. Closer to the starter = more similar.'],
      ['Adaptability', 'The transfer model (module C) probability for that player at that club.'],
      ['Affordability', 'His value versus the 90th percentile of what the club has paid for a signing. A contract ending within 12 months adds points.'],
      ['Quality', 'Percentile of his API-Football rating among players in the same position.'],
    ],
    bFiltro: 'By default we exclude players over 32, with fewer than 900 minutes or valued above 2.5 times what the club usually pays.',
    limitaciones: [
      ['Transfermarkt is frozen', 'The open dataset stopped updating in July 2026. Current squads and stats come from API-Football, but values and contracts carry that cut-off.'],
      ['No minutes for Liga MX or Argentina', 'Transfermarkt does not publish per-match minutes for those leagues, so the transfer model learns mostly from European moves.'],
      ['Market value is an estimate', 'Transfermarkt computes it with its community; it is not a sale price. “Undervalued” means “relative to Transfermarkt”.'],
      ['Correlation, not causation', 'The models describe which signings worked in the past. They guarantee nothing and do not capture injuries, dressing room or coaching style.'],
      ['Incomplete contracts', 'In Liga MX only about half of the players have a contract date.'],
      ['Third-party images', 'Photos and crests come from API-Football and belong to their owners; they are used only for identification.'],
    ],
    glosario: [
      ['Per 90 minutes', 'A stat divided by minutes played and multiplied by 90, to compare starters with substitutes.'],
      ['Record linkage', 'A technique to identify the same object (here, a player) in two databases without a shared identifier.'],
      ['Gradient boosting', 'A model that adds up many small decision trees, each one correcting the errors of the previous.'],
      ['Logistic regression', 'A model that turns a weighted sum of variables into a probability between 0 and 1.'],
      ['Cross-validation', 'Evaluating a model on data it did not see in training, rotating which part is used for testing.'],
      ['R²', 'Share of the variation the model explains (0 = nothing, 1 = everything).'],
      ['AUC', 'A model’s ability to rank positive cases above negative ones (0.5 = chance).'],
      ['Calibration', 'How closely predicted probabilities match what actually happens.'],
      ['Standardise (z)', 'Subtract the mean and divide by the standard deviation, to compare variables on different scales.'],
    ],
    inspirado: 'Inspired by Brighton & Hove Albion’s recruitment model: use data to find talent the market has not spotted yet, then verify it with a scout’s eye.',
    actualizado: 'Figures from the {f} run.', ir: 'Go to the radar',
  },
};

const VARS = {
  es: { edad: 'Edad', edad2: 'Edad lejos de 26 años', log_valor: 'Valor de mercado', log_fee: 'Monto del traspaso', min_antes: 'Minutos temporada previa',
    sin_min_antes: 'Sin minutos registrados', f_liga_dest: 'Nivel de liga destino', f_liga_orig: 'Nivel de liga origen', d_liga: 'Salto de liga',
    f_club_dest: 'Nivel de club destino', f_club_orig: 'Nivel de club origen', d_club: 'Salto de club', mov_local: 'Mismo país',
    mov_idioma: 'Otro país, mismo idioma', mov_conf: 'Otro país, misma confederación', compatriotas: 'Compatriotas en plantilla',
    competencia: 'Competencia en su posición', g_POR: 'Portero', g_DEF: 'Defensa', g_MED: 'Mediocampista', g_DEL: 'Delantero' },
  en: { edad: 'Age', edad2: 'Age away from 26', log_valor: 'Market value', log_fee: 'Transfer fee', min_antes: 'Minutes previous season',
    sin_min_antes: 'No minutes on record', f_liga_dest: 'Destination league level', f_liga_orig: 'Origin league level', d_liga: 'League step',
    f_club_dest: 'Destination club level', f_club_orig: 'Origin club level', d_club: 'Club step', mov_local: 'Same country',
    mov_idioma: 'Another country, same language', mov_conf: 'Another country, same confederation', compatriotas: 'Compatriots in squad',
    competencia: 'Competition for his position', g_POR: 'Goalkeeper', g_DEF: 'Defender', g_MED: 'Midfielder', g_DEL: 'Forward' },
};

const IMP_EN = { Edad: 'Age', Liga: 'League', Club: 'Club', 'Trayectoria de valor': 'Value trajectory', Contrato: 'Contract',
  'Selección nacional': 'National team', 'Minutos y titularidad': 'Minutes and starts', 'Calificación': 'Rating',
  'Producción ofensiva': 'Attacking output', 'Producción defensiva': 'Defensive output', 'Físico y posición': 'Physique and position' };

const pct = (v, d = 1) => `${(v * 100).toFixed(d)}%`;

function Seccion({ id, num, titulo, children }) {
  return (
    <section id={id} className="met-seccion" aria-labelledby={`${id}-t`}>
      <p className="met-num">{String(num).padStart(2, '0')}</p>
      <h2 id={`${id}-t`} className="seccion">{titulo}</h2>
      {children}
    </section>
  );
}

function Pasos({ items, ordenada = true }) {
  const Etq = ordenada ? 'ol' : 'ul';
  return (
    <Etq className="met-pasos">
      {items.map(([k, v], i) => (
        <li key={k}><span className="met-paso-n" aria-hidden="true">{i + 1}</span><div><strong>{k}</strong><p>{v}</p></div></li>
      ))}
    </Etq>
  );
}

function Tile({ valor, etiqueta, sub }) {
  return (
    <div className="tarjeta relleno kpi">
      <p className="k-etq">{etiqueta}</p>
      <p className="k-val">{valor}</p>
      {sub && <p className="k-sub">{sub}</p>}
    </div>
  );
}

export default function Metodologia() {
  const { idioma } = useIdioma();
  const c = C[idioma] || C.es;
  const [m, setM] = useState(null);
  useEffect(() => { cargar('metodologia.json').then(setM).catch(() => setM({})); }, []);

  const ids = ['flujo', 'fuentes', 'limpieza', 'vinculacion', 'modulo-a', 'modulo-c', 'modulo-b', 'limitaciones', 'glosario'];
  const v = m?.vinculacion;
  const a = m?.valor;
  const f = m?.fichajes;
  const fu = m?.fuentes || {};
  const nombreLiga = (k) => NOMBRES_LIGA[k] || k;

  return (
    <main className="contenedor met">
      <header className="met-cabecera">
        <h1 className="titulo">{c.titulo}</h1>
        <p className="subtitulo" style={{ maxWidth: 820, fontSize: 18 }}>{c.intro}</p>
        {m?.resumen && <p className="nota" style={{ marginTop: 10 }}>{c.actualizado.replace('{f}', fecha(m.resumen.fecha_datos, idioma))}</p>}
      </header>

      <section className="rejilla-kpi" style={{ marginTop: 24 }}>
        <Tile etiqueta={c.tiles[0]} valor="4" sub="Transfermarkt · API-Football · StatsBomb · football-data" />
        <Tile etiqueta={c.tiles[1]} valor={v ? miles(v.vinculados) : '—'} sub={v ? `${pct(v.activos_vinculados / v.activos)} · ${idioma === 'es' ? 'activos' : 'active'}` : ''} />
        <Tile etiqueta={c.tiles[2]} valor={f?.n ? miles(f.n) : '—'} sub={f?.temporadas ? `${f.temporadas[0]}–${f.temporadas[1]}` : ''} />
        <Tile etiqueta={c.tiles[3]} valor={c.cadaLunes} sub="GitHub Actions → Cloudflare" />
      </section>

      <nav className="met-indice tarjeta" aria-label={c.indice}>
        <strong>{c.indice}</strong>
        <ol>{c.secciones.map((s, i) => <li key={s}><a href={`#${ids[i]}`}>{s}</a></li>)}</ol>
      </nav>

      {/* 1. Flujo */}
      <Seccion id="flujo" num={1} titulo={c.secciones[0]}>
        <p className="met-lead">{c.flujoTxt}</p>
        <ol className="flujo" aria-label={c.secciones[0]}>
          {c.pasos.map(([k, d, h], i) => (
            <li key={k} className={i >= 1 && i <= 4 ? 'en-github' : ''}>
              <span className="flujo-n">{i + 1}</span>
              <strong>{k}</strong>
              <p>{d}</p>
              <small>{h}</small>
            </li>
          ))}
        </ol>
        <div className="ciclo tarjeta">
          <strong>{c.ciclo}</strong>
          <ol>{c.cicloPasos.map((p) => <li key={p}>{p}</li>)}</ol>
        </div>
      </Seccion>

      {/* 2. Fuentes */}
      <Seccion id="fuentes" num={2} titulo={c.secciones[1]}>
        <p className="met-lead">{c.fuentesTxt}</p>
        <div className="met-rejilla-4">
          {c.fuentesTarjetas.map(([n, d, lic, k]) => {
            const filas = k === 'tm' ? c.filasTm : k === 'af' ? c.filasAf : null;
            const datos = k === 'tm' ? fu.transfermarkt : k === 'af' ? fu.api_football : null;
            return (
              <article key={n} className="tarjeta relleno fuente">
                <h3>{n}</h3>
                <p>{d}</p>
                {filas && datos && (
                  <dl>{Object.entries(filas).filter(([t]) => datos[t]).map(([t, et]) => (
                    <div key={t}><dt>{et}</dt><dd>{miles(datos[t])}</dd></div>
                  ))}</dl>
                )}
                <small>{lic}</small>
              </article>
            );
          })}
        </div>
        <div className="tarjeta tabla-caja" style={{ marginTop: 16 }}>
          <table className="tabla matriz">
            <caption>{c.matrizTitulo}</caption>
            <thead><tr><th scope="col" /><th scope="col">Transfermarkt</th><th scope="col">API-Football</th><th scope="col">StatsBomb</th><th scope="col">football-data</th></tr></thead>
            <tbody>
              {c.matrizFilas.map((fila, i) => (
                <tr key={fila}>
                  <th scope="row">{fila}</th>
                  {c.matriz[i].map((x, j) => (
                    <td key={j}>{x ? <span className="marca-si"><svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5 L6.5 12 L13 4.5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /></svg><span className="solo-lector">{idioma === 'es' ? 'sí' : 'yes'}</span></span> : <span className="marca-no" aria-label="no">·</span>}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Seccion>

      {/* 3. Limpieza */}
      <Seccion id="limpieza" num={3} titulo={c.secciones[2]}>
        <p className="met-lead">{c.limpiezaTxt}</p>
        <div className="met-rejilla-3">
          {c.limpieza.map(([k, d]) => <div key={k} className="tarjeta relleno regla"><strong>{k}</strong><p>{d}</p></div>)}
        </div>
      </Seccion>

      {/* 4. Vinculacion */}
      <Seccion id="vinculacion" num={4} titulo={c.secciones[3]}>
        <p className="met-lead">{c.vincTxt}</p>
        <Pasos items={c.vincPasos.map(([k, d]) => [k, d.replace('{u}', v ? v.umbral : '0.62')])} />
        <div className="fila-flex" style={{ gap: 20, marginTop: 20, alignItems: 'stretch' }}>
          <div className="tarjeta relleno" style={{ flex: '1 1 360px' }}>
            <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.pesosTitulo}</h3>
            <Proporciones partes={c.pesosNombres.map((k, i) => ({ k, v: [55, 20, 15, 10][i], color: ['var(--m6)', 'var(--m5)', 'var(--m4)', 'var(--m3)'][i] }))} />
            <p className="nota" style={{ marginTop: 12 }}>{idioma === 'es'
              ? 'Nombre: similitud de fragmentos de 2 a 4 letras (TF-IDF) o de palabras completas, la mayor. País: coincide o no. Club: palabras en común. Estatura: diferencia de hasta 2 cm cuenta completa.'
              : 'Name: similarity of 2-to-4-letter fragments (TF-IDF) or of whole words, whichever is higher. Country: match or not. Club: shared words. Height: up to 2 cm difference counts in full.'}</p>
          </div>
          {v?.ejemplos?.length > 0 && (
            <div className="tarjeta" style={{ flex: '2 1 520px', minWidth: 0 }}>
              <h3 className="tarjeta-t" style={{ fontSize: 16, padding: '18px 20px 0' }}>{c.ejemplosTitulo}</h3>
              <div className="tabla-caja">
                <table className="tabla" style={{ fontSize: 13, minWidth: 620 }}>
                  <thead><tr>{c.ejCols.map((x, i) => <th key={x} scope="col" className={i >= 2 ? 'der' : ''}>{x}</th>)}</tr></thead>
                  <tbody>
                    {v.ejemplos.map((e) => (
                      <tr key={e.tm}>
                        <td style={{ fontWeight: 600 }}>{e.tm}</td>
                        <td style={{ color: 'var(--tenue)' }}>{e.af}</td>
                        {[e.s_nombre, e.s_pais, e.s_club, e.s_altura].map((s, i) => <td key={i} className="der"><span className="mini-barra"><i style={{ width: `${s * 100}%` }} /></span>{s.toFixed(2)}</td>)}
                        <td className="der" style={{ fontWeight: 700, color: 'var(--marca)' }}>{e.puntaje.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
        {v && (
          <>
            <p className="met-destacado">{c.vincResultado.replace('{a}', miles(v.activos)).replace('{b}', miles(v.activos_vinculados)).replace('{p}', pct(v.activos_vinculados / v.activos))}</p>
            <div className="fila-flex" style={{ gap: 20, alignItems: 'flex-start' }}>
              <div className="tarjeta relleno" style={{ flex: '2 1 560px', minWidth: 0 }}>
                <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.coberturaTitulo}</h3>
                <BarrasH datos={v.por_liga.slice(0, 16).map(([k, , p]) => [nombreLiga(k), p])} max={100} formato={(x) => `${x.toFixed(1)}%`}
                  etiquetaCat={c.liga} etiquetaValor={c.pct} />
                <p className="nota">{c.coberturaNota}</p>
              </div>
              <div className="tarjeta relleno" style={{ flex: '1 1 320px', minWidth: 0 }}>
                <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.bandasTitulo}</h3>
                <BarrasH datos={v.bandas.slice().reverse()} formato={(x) => miles(x)} etiquetaCat={c.banda} etiquetaValor={c.pares} ancho={420} />
              </div>
            </div>
          </>
        )}
      </Seccion>

      {/* 5. Modulo A */}
      <Seccion id="modulo-a" num={5} titulo={c.secciones[4]}>
        <p className="met-lead">{c.aTxt}</p>
        <Pasos items={c.aPasos} />
        <div className="tarjeta relleno" style={{ marginTop: 20 }}>
          <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.cvTitulo}</h3>
          <div className="cv" role="img" aria-label={c.cvNota}>
            {[0, 1, 2, 3, 4].map((r) => (
              <div key={r} className="cv-fila">
                <span className="cv-etq">{c.ronda} {r + 1}</span>
                {[0, 1, 2, 3, 4].map((g) => <span key={g} className={g === r ? 'cv-prueba' : 'cv-entrena'}>{g === r ? c.cvValora : c.cvEntrena}</span>)}
              </div>
            ))}
          </div>
          <p className="nota">{c.cvNota}</p>
        </div>
        {a && (
          <>
            <section className="rejilla-kpi" style={{ marginTop: 20 }}>
              <Tile etiqueta={c.r2} valor={a.r2.toFixed(3)} sub={c.r2Exp.replace('{p}', pct(a.r2, 0))} />
              <Tile etiqueta={c.r2Base} valor={a.r2_base.toFixed(3)} sub={c.baseExp} />
              <Tile etiqueta={c.mae} valor={`${a.mae_pct}%`} sub={c.maeExp} />
              <Tile etiqueta={c.enTope} valor={`${a.en_tope}%`} sub={c.topeExp} />
            </section>
            <div className="fila-flex" style={{ gap: 20, marginTop: 20, alignItems: 'flex-start' }}>
              <div className="tarjeta relleno" style={{ flex: '1 1 460px', minWidth: 0 }}>
                <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.importanciaTitulo}</h3>
                <BarrasH datos={a.importancia.map(([k, x]) => [idioma === 'en' ? IMP_EN[k] || k : k, Math.max(0, x)])} formato={(x) => x.toFixed(3)}
                  etiquetaCat={idioma === 'es' ? 'Grupo de variables' : 'Variable group'} etiquetaValor={idioma === 'es' ? 'Caída de R²' : 'R² drop'} ancho={560} />
                <p className="nota">{c.importanciaNota}</p>
              </div>
              <div className="tarjeta relleno" style={{ flex: '1 1 420px', minWidth: 0 }}>
                <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.dispersionTitulo}</h3>
                <Dispersion puntos={a.dispersion} etiquetaX={c.valorReal} etiquetaY={c.valorEst} />
              </div>
            </div>
          </>
        )}
      </Seccion>

      {/* 6. Modulo C */}
      <Seccion id="modulo-c" num={6} titulo={c.secciones[5]}>
        <p className="met-lead">{c.cTxt}</p>
        <div className="tarjeta relleno">
          <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.etiquetaTitulo}</h3>
          <div className="linea-exito" aria-hidden="true">
            <span className="le-hito">{c.linea[0]}</span>
            <span className="le-tramo">{c.linea[1]}</span>
            <span className="le-hito">{c.linea[2]}</span>
          </div>
          <div className="condiciones">
            {c.condiciones.map((x, i) => <span key={x}>{i > 0 && <b>{idioma === 'es' ? 'y' : 'and'}</b>}<em>{x}</em></span>)}
          </div>
          {f?.tasa_base && <p className="met-destacado" style={{ margin: '14px 0 0' }}>{c.tasaBase.replace('{p}', pct(f.tasa_base))}</p>}
          <p className="nota" style={{ marginTop: 10 }}>{c.cVars}</p>
        </div>
        {f?.auc && (
          <>
            <section className="rejilla-kpi" style={{ marginTop: 20 }}>
              <Tile etiqueta={c.aucLr} valor={`AUC ${f.auc}`} sub={`Brier ${f.brier}`} />
              <Tile etiqueta={c.aucGb} valor={`AUC ${f.auc_gb}`} sub={`Brier ${f.brier_gb}`} />
              <Tile etiqueta={idioma === 'es' ? 'Traspasos etiquetados' : 'Labelled transfers'} valor={miles(f.n)} sub={`${f.temporadas[0]}–${f.temporadas[1]}`} />
            </section>
            <p className="nota" style={{ marginTop: 10 }}>{c.aucExp} {c.porQueLr}</p>
            <div className="fila-flex" style={{ gap: 20, marginTop: 20, alignItems: 'flex-start' }}>
              <div className="tarjeta relleno" style={{ flex: '1 1 480px', minWidth: 0 }}>
                <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.calTitulo}</h3>
                <Calibracion datos={f.cal} />
                <p className="nota">{c.calNota}</p>
              </div>
              <div className="tarjeta relleno" style={{ flex: '1 1 480px', minWidth: 0 }}>
                <h3 className="tarjeta-t" style={{ fontSize: 16 }}>{c.coefTitulo}</h3>
                <Divergente datos={f.coef.slice().reverse().map(([k, x]) => [VARS[idioma][k] || k, x])} formato={(x) => x.toFixed(2)}
                  etiquetaCat={idioma === 'es' ? 'Variable' : 'Variable'} etiquetaValor={idioma === 'es' ? 'Coeficiente' : 'Coefficient'} />
                <p className="nota">{c.coefNota}</p>
              </div>
            </div>
            <p className="met-hallazgo">{c.hallazgo}</p>
          </>
        )}
      </Seccion>

      {/* 7. Modulo B */}
      <Seccion id="modulo-b" num={7} titulo={c.secciones[6]}>
        <p className="met-lead">{c.bTxt}</p>
        <div className="tarjeta relleno">
          <Proporciones partes={c.pesosB.map((k, i) => ({ k, v: [35, 30, 20, 15][i], color: ['var(--m6)', 'var(--m5)', 'var(--m4)', 'var(--m3)'][i] }))} />
          <div className="met-rejilla-4" style={{ marginTop: 18 }}>
            {c.bCriterios.map(([k, d]) => <div key={k} className="regla"><strong>{k}</strong><p>{d}</p></div>)}
          </div>
        </div>
        <div className="fila-flex" style={{ gap: 16, marginTop: 16 }}>
          <p className="tarjeta relleno" style={{ flex: '1 1 380px', margin: 0, fontSize: 14, lineHeight: 1.55 }}>{c.xiRegla}</p>
          <p className="tarjeta relleno" style={{ flex: '1 1 380px', margin: 0, fontSize: 14, lineHeight: 1.55 }}>{c.bFiltro}</p>
        </div>
      </Seccion>

      {/* 8. Limitaciones */}
      <Seccion id="limitaciones" num={8} titulo={c.secciones[7]}>
        <div className="met-rejilla-3">
          {c.limitaciones.map(([k, d]) => (
            <div key={k} className="tarjeta relleno regla limite">
              <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3 L22 20 H2 Z" /><path d="M12 10 v4" /><path d="M12 17 v.5" /></svg>
              <strong>{k}</strong><p>{d}</p>
            </div>
          ))}
        </div>
      </Seccion>

      {/* 9. Glosario */}
      <Seccion id="glosario" num={9} titulo={c.secciones[8]}>
        <dl className="glosario">
          {c.glosario.map(([k, d]) => <div key={k}><dt>{k}</dt><dd>{d}</dd></div>)}
        </dl>
      </Seccion>

      <div className="tarjeta relleno inv-tarjeta" style={{ marginTop: 40, display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'center', justifyContent: 'space-between' }}>
        <p style={{ margin: 0, maxWidth: 760, fontSize: 15, lineHeight: 1.5 }}>{c.inspirado}</p>
        <Link to="/radar" className="boton" style={{ background: 'var(--brillo)', color: '#0C1A12' }}>{c.ir}</Link>
      </div>
    </main>
  );
}
