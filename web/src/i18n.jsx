import { createContext, useContext, useEffect, useState, useCallback } from 'react';

const T = {
  es: {
    inicio: 'Inicio', radar: 'Radar', equipos: 'Equipos', simulador: 'Simulador', metodologia: 'Metodología',
    buscar: 'Buscar jugador', idioma: 'Idioma',
    heroTitulo: 'Encuentra el talento que el mercado todavía no ve.',
    heroTexto: 'Un portal abierto de scouting con datos: valor de mercado, rendimiento y jugadores infravalorados en {ligas} ligas, actualizado cada semana.',
    datosAl: 'Datos al {f} · próxima actualización {p}',
    abrirRadar: 'Abrir el radar', buscarReemplazos: 'Buscar reemplazos para mi equipo',
    jugadoresActivos: 'Jugadores activos', ligas: 'Ligas', equiposN: 'Equipos', actualizacion: 'Actualización', semanal: 'Semanal',
    exploraPais: 'Explora por país', exploraPaisTxt: 'Haz clic en un país para abrir el radar ya filtrado.',
    nacionalidad: 'Nacionalidad', ligaDelPais: 'Liga del país', jugadoresPorNac: 'Jugadores activos por nacionalidad',
    jugadoresPorLiga: 'Jugadores activos en ligas del país', masJugadores: 'Más jugadores', abrirRadarFlecha: 'Abrir radar →',
    jugadoresN: '{n} jugadores',
    cambiosTitulo: 'Cambios radicales de valor', cambiosTxt: 'Mayores movimientos en la última actualización de Transfermarkt ({f}).',
    suben: 'Suben', bajan: 'Bajan', verTodos: 'Ver radar',
    radarSemana: 'Radar de la semana', ventanaContratos: 'Ventana de contratos', vencenAntes: 'Contratos que vencen antes de julio 2027',
    jugadoresNegociables: '{n} jugadores con valor estimado', inspirado: 'Inspirado en el modelo del Brighton',
    metodoTxt: 'Cómo combinamos fuentes y modelos de minería de datos',
    moduloA: 'Módulo A', radarTitulo: 'Radar de infravalorados',
    radarTxt: 'Jugadores cuyo valor de mercado está por debajo de lo que estima el modelo para su edad, rendimiento, liga y trayectoria.',
    modoRadar: 'Radar (con valor estimado)', modoTodos: 'Todos los jugadores',
    todasLigas: 'Todas las ligas', otraLiga: 'Otra liga…', buscador: 'Buscador', limpiar: 'Limpiar',
    edad: 'Edad', minima: 'Mínima', maxima: 'Máxima', posicion: 'Posición', paisesEsp: 'Países específicos',
    paisesPh: 'Ej. Uruguay, Colombia', contratoAntes: 'Contrato vence antes de', cualquierFecha: 'Cualquier fecha',
    valorMax: 'Valor de mercado máximo', sinLimite: 'Sin límite', pie: 'Pie hábil', cualquiera: 'Cualquiera',
    derecho: 'Derecho', izquierdo: 'Izquierdo', ambos: 'Ambos', otras: 'Otras',
    coinciden: '{n} jugadores coinciden', ordenar: 'Ordenar por', ordBrecha: 'Brecha de valor', ordValor: 'Valor de mercado',
    ordEstimado: 'Valor estimado', ordEdad: 'Edad (menor primero)', ordMinutos: 'Minutos jugados',
    jugador: 'Jugador', pos: 'Pos', nac: 'Nac', contrato: 'Contrato', valorMercado: 'Valor mercado', valorEstimado: 'Valor estimado',
    brecha: 'Brecha', sinDato: 'Sin dato', quitarFiltro: 'Quitar filtro', anterior: 'Anterior', siguiente: 'Siguiente',
    pagina: 'Página {p} de {t}', cargando: 'Cargando datos…', sinResultados: 'Ningún jugador coincide con estos filtros.',
    comoLeer: 'Cómo leer la brecha',
    comoLeerTxt: 'Brecha = (valor estimado − valor de mercado) ÷ valor de mercado. El valor estimado sale de un modelo de gradient boosting entrenado con edad, minutos, estadísticas por 90, fuerza de la liga y del club, contrato y trayectoria. Cada jugador lo valora un modelo que no lo vio al entrenar. Es una señal para priorizar, no un precio.',
    fuentes: 'Fuentes', soloConMinutos: 'Solo aparecen jugadores con al menos 900 minutos en sus dos últimas temporadas.',
    perfil: 'Perfil', simularFichaje: 'Simular fichaje', fotoFuente: 'Foto · API-Football',
    contratoHasta: 'Contrato hasta {c}', anios: '{n} años', valorHistorico: 'Valor de mercado', maxHistorico: 'Máximo histórico {v}',
    porElModelo: 'Valor estimado por el modelo', sinEstimacion: 'Sin estimación (menos de 450 min)',
    goles: 'Goles', asistencias: 'Asist.', minutos: 'Minutos', calificacion: 'Calificación', pj: 'PJ', titular: 'Titular',
    pasesClave: 'Pases clave', entradas: 'Entradas', intercepciones: 'Intercep.', temporada: 'Temporada', club: 'Club',
    estadisticas: 'Estadísticas por temporada', totales: 'Totales', por90: 'Por 90 min', historialClubes: 'Historial de clubes',
    traspaso: 'Traspaso', libre: 'Libre o no publicado', prestamo: 'Préstamo', sinTraspasos: 'Sin traspasos registrados.',
    sinTemporadas: 'Sin estadísticas de API-Football vinculadas a este jugador.',
    noticias: 'Noticias y contexto fuera de la cancha', noticiasPronto: 'Titulares de medios verificados enlazados a la nota original. Esta sección se activa con la próxima actualización semanal.',
    ultimas2: 'Últimas 2 temporadas', noEncontrado: 'Jugador no encontrado.',
    pronto: 'Próximamente', prontoEquipos: 'Reemplazos por equipo: el XI de cada club y el mejor reemplazo por posición según similitud, adaptación y asequibilidad.',
    prontoSimulador: 'Simulador de fichaje: probabilidad de que un traspaso funcione, aprendida de miles de traspasos reales.',
    prontoMetodologia: 'Metodología: fuentes, vinculación de jugadores y modelos de minería de datos.',
    prontoNoEncontrado: 'Esta página no existe.', volverInicio: 'Volver al inicio',
    pieFuentes: 'Fuentes: Transfermarkt (CC0) · API-Football · StatsBomb Open Data · football-data.co.uk',
    pieProyecto: 'Proyecto de Minería de Datos Aplicada · UANL FACPYA',
  },
  en: {
    inicio: 'Home', radar: 'Radar', equipos: 'Teams', simulador: 'Simulator', metodologia: 'Methodology',
    buscar: 'Search player', idioma: 'Language',
    heroTitulo: 'Find the talent the market hasn’t spotted yet.',
    heroTexto: 'An open, data-driven scouting portal: market value, performance and undervalued players across {ligas} leagues, updated every week.',
    datosAl: 'Data as of {f} · next update {p}',
    abrirRadar: 'Open the radar', buscarReemplazos: 'Find replacements for my team',
    jugadoresActivos: 'Active players', ligas: 'Leagues', equiposN: 'Teams', actualizacion: 'Updates', semanal: 'Weekly',
    exploraPais: 'Explore by country', exploraPaisTxt: 'Click a country to open the radar already filtered.',
    nacionalidad: 'Nationality', ligaDelPais: 'Country’s league', jugadoresPorNac: 'Active players by nationality',
    jugadoresPorLiga: 'Active players in the country’s leagues', masJugadores: 'Most players', abrirRadarFlecha: 'Open radar →',
    jugadoresN: '{n} players',
    cambiosTitulo: 'Biggest value swings', cambiosTxt: 'Largest moves in the latest Transfermarkt update ({f}).',
    suben: 'Rising', bajan: 'Falling', verTodos: 'View radar',
    radarSemana: 'Radar of the week', ventanaContratos: 'Contract window', vencenAntes: 'Contracts expiring before July 2027',
    jugadoresNegociables: '{n} players with an estimated value', inspirado: 'Inspired by Brighton’s model',
    metodoTxt: 'How we combine sources and data-mining models',
    moduloA: 'Module A', radarTitulo: 'Undervalued radar',
    radarTxt: 'Players whose market value sits below what the model estimates for their age, performance, league and trajectory.',
    modoRadar: 'Radar (with estimated value)', modoTodos: 'All players',
    todasLigas: 'All leagues', otraLiga: 'Other league…', buscador: 'Search', limpiar: 'Clear',
    edad: 'Age', minima: 'Min', maxima: 'Max', posicion: 'Position', paisesEsp: 'Specific countries',
    paisesPh: 'e.g. Uruguay, Colombia', contratoAntes: 'Contract ends before', cualquierFecha: 'Any date',
    valorMax: 'Max market value', sinLimite: 'No limit', pie: 'Preferred foot', cualquiera: 'Any',
    derecho: 'Right', izquierdo: 'Left', ambos: 'Both', otras: 'Other',
    coinciden: '{n} players match', ordenar: 'Sort by', ordBrecha: 'Value gap', ordValor: 'Market value',
    ordEstimado: 'Estimated value', ordEdad: 'Age (youngest first)', ordMinutos: 'Minutes played',
    jugador: 'Player', pos: 'Pos', nac: 'Nat', contrato: 'Contract', valorMercado: 'Market value', valorEstimado: 'Estimated value',
    brecha: 'Gap', sinDato: 'No data', quitarFiltro: 'Remove filter', anterior: 'Previous', siguiente: 'Next',
    pagina: 'Page {p} of {t}', cargando: 'Loading data…', sinResultados: 'No players match these filters.',
    comoLeer: 'How to read the gap',
    comoLeerTxt: 'Gap = (estimated value − market value) ÷ market value. The estimate comes from a gradient boosting model trained on age, minutes, per-90 stats, league and club strength, contract and trajectory. Each player is valued by a model that did not see him in training. It is a signal for prioritising, not a price.',
    fuentes: 'Sources', soloConMinutos: 'Only players with at least 900 minutes over their last two seasons are shown.',
    perfil: 'Profile', simularFichaje: 'Simulate transfer', fotoFuente: 'Photo · API-Football',
    contratoHasta: 'Contract until {c}', anios: '{n} years', valorHistorico: 'Market value', maxHistorico: 'All-time high {v}',
    porElModelo: 'Model’s estimated value', sinEstimacion: 'No estimate (under 450 min)',
    goles: 'Goals', asistencias: 'Ast.', minutos: 'Minutes', calificacion: 'Rating', pj: 'Apps', titular: 'Starts',
    pasesClave: 'Key passes', entradas: 'Tackles', intercepciones: 'Interc.', temporada: 'Season', club: 'Club',
    estadisticas: 'Stats by season', totales: 'Totals', por90: 'Per 90', historialClubes: 'Club history',
    traspaso: 'Transfer', libre: 'Free or undisclosed', prestamo: 'Loan', sinTraspasos: 'No transfers on record.',
    sinTemporadas: 'No API-Football stats linked to this player.',
    noticias: 'Off-pitch news and context', noticiasPronto: 'Headlines from verified outlets linked to the original story. This section goes live with the next weekly update.',
    ultimas2: 'Last 2 seasons', noEncontrado: 'Player not found.',
    pronto: 'Coming soon', prontoEquipos: 'Team replacements: each club’s XI and the best replacement per position by similarity, adaptability and affordability.',
    prontoSimulador: 'Transfer simulator: the probability that a move works out, learned from thousands of real transfers.',
    prontoMetodologia: 'Methodology: sources, player linking and data-mining models.',
    prontoNoEncontrado: 'This page does not exist.', volverInicio: 'Back to home',
    pieFuentes: 'Sources: Transfermarkt (CC0) · API-Football · StatsBomb Open Data · football-data.co.uk',
    pieProyecto: 'Applied Data Mining project · UANL FACPYA',
  },
};

const Ctx = createContext(null);

function leerGuardado() {
  try { return localStorage.getItem('sv-idioma'); } catch { return null; }
}

export function IdiomaProvider({ children }) {
  const [idioma, setIdioma] = useState(() => leerGuardado() || 'es');
  useEffect(() => {
    try { localStorage.setItem('sv-idioma', idioma); } catch { /* sin almacenamiento */ }
    document.documentElement.lang = idioma;
  }, [idioma]);
  const t = useCallback((clave, vars) => {
    let s = (T[idioma] && T[idioma][clave]) || T.es[clave] || clave;
    if (vars) Object.entries(vars).forEach(([k, v]) => { s = s.replace(`{${k}}`, v); });
    return s;
  }, [idioma]);
  return <Ctx.Provider value={{ idioma, setIdioma, t }}>{children}</Ctx.Provider>;
}

export function useIdioma() {
  return useContext(Ctx);
}
