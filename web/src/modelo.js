// Inferencia del modulo C (regresion logistica exportada por scripts/60_modulos_bc.py) en el navegador.
import { cargar, cargarJugadores } from './datos.js';

export const GRUPO = { POR: 'POR', DFC: 'DEF', LI: 'DEF', LD: 'DEF', MCD: 'MED', MC: 'MED', MCO: 'MED', MI: 'MED', MD: 'MED', EI: 'DEL', ED: 'DEL', SD: 'DEL', DC: 'DEL' };
export const COMPAT = {
  POR: ['POR'], LI: ['LI', 'MI'], LD: ['LD', 'MD'], DFC: ['DFC'], MCD: ['MCD', 'MC'], MC: ['MC', 'MCD', 'MCO'],
  MCO: ['MCO', 'MC', 'SD'], MI: ['MI', 'EI'], MD: ['MD', 'ED'], EI: ['EI', 'MI', 'ED'], ED: ['ED', 'MD', 'EI'], DC: ['DC', 'SD'],
};

let ctxPromesa = null;
export function cargarContexto() {
  if (!ctxPromesa) {
    ctxPromesa = Promise.all([
      cargar('modelo_c.json'), cargar('clubes_ctx.json'), cargar('ligas_ctx.json'), cargar('min_ult.json'),
      cargar('clubes.json'), cargar('ligas.json'), cargarJugadores(), cargar('pares_ligas.json'),
    ]).then(([modelo, clubesCtx, ligasCtx, minUlt, clubes, ligas, jugadores, pares]) => ({
      modelo, clubesCtx, ligasCtx, minUlt, clubes, ligas, jugadores, pares,
      ligaPorId: Object.fromEntries(ligas.map((l) => [l.id, l])),
      jugPorId: Object.fromEntries(jugadores.map((j) => [j.id, j])),
    }));
  }
  return ctxPromesa;
}

// Variables de un jugador hacia un club destino; mismas definiciones que en el entrenamiento.
export function variables(j, destId, ctx, factorMonto = 1) {
  const { modelo, clubesCtx, ligasCtx, minUlt } = ctx;
  const dest = clubesCtx[destId] || {};
  const orig = clubesCtx[j.cl] || {};
  const e = j.e ?? 26;
  const v = Math.max(j.v || 25000, 25000);
  const m = minUlt[j.id];
  const fLd = ligasCtx[dest.lg] ?? modelo.piso_liga;
  const fLo = ligasCtx[j.lg] ?? modelo.piso_liga;
  const fCd = dest.f ?? modelo.piso_club;
  const fCo = orig.f ?? modelo.piso_club;
  const paisD = dest.pais;
  const paisO = orig.pais ?? ctx.ligaPorId[j.lg]?.pais;
  const local = paisO && paisO === paisD;
  const idi = modelo.idioma[j.nac] && modelo.idioma[j.nac] === modelo.idioma[paisD];
  const cnf = modelo.conf[j.nac] && modelo.conf[j.nac] === modelo.conf[paisD];
  const mismoClub = Number(j.cl) === Number(destId);
  const compat = Math.max(0, ((dest.nac || {})[j.nac] || 0) - (mismoClub ? 1 : 0));
  const g = GRUPO[j.p] || 'MED';
  const competencia = (dest.comp || {})[g] || 0;
  const x = {
    edad: e, edad2: (e - 26) ** 2, log_valor: Math.log(v), log_fee: Math.log1p((j.v || 0) * factorMonto),
    min_antes: m ? m / 1000 : 0, sin_min_antes: m ? 0 : 1,
    f_liga_dest: fLd, f_liga_orig: fLo, d_liga: fLd - fLo, f_club_dest: fCd, f_club_orig: fCo, d_club: fCd - fCo,
    mov_local: local ? 1 : 0, mov_idioma: !local && idi ? 1 : 0, mov_conf: !local && !idi && cnf ? 1 : 0,
    compatriotas: Math.min(compat, 5), competencia: Math.min(competencia, 4),
    g_POR: g === 'POR' ? 1 : 0, g_DEF: g === 'DEF' ? 1 : 0, g_MED: g === 'MED' ? 1 : 0, g_DEL: g === 'DEL' ? 1 : 0,
  };
  const info = { minutos: m || null, compatriotas: compat, competencia, local, idioma: !!idi, conf: !!cnf, paisD, paisO, fLd, fLo, fCd, fCo };
  return { x, info };
}

function sigmoide(z) { return 1 / (1 + Math.exp(-z)); }

function logit(zs, modelo) {
  let s = modelo.intercepto;
  for (let i = 0; i < zs.length; i++) s += modelo.coef[i] * zs[i];
  return s;
}

function estandarizar(x, modelo) {
  return modelo.feats.map((f, i) => {
    const val = Number.isFinite(x[f]) ? x[f] : modelo.mediana[i];
    return (val - modelo.media[i]) / modelo.desv[i];
  });
}

export function probabilidad(j, destId, ctx, factorMonto = 1) {
  const { x } = variables(j, destId, ctx, factorMonto);
  return sigmoide(logit(estandarizar(x, ctx.modelo), ctx.modelo));
}

export const FACTORES = [
  { id: 'minutos', feats: ['min_antes', 'sin_min_antes'] },
  { id: 'movimiento', feats: ['mov_local', 'mov_idioma', 'mov_conf'] },
  { id: 'edad', feats: ['edad', 'edad2'] },
  { id: 'valor', feats: ['log_valor', 'log_fee'] },
  { id: 'liga', feats: ['f_liga_dest', 'f_liga_orig', 'd_liga'] },
  { id: 'club', feats: ['f_club_dest', 'f_club_orig', 'd_club'] },
  { id: 'compatriotas', feats: ['compatriotas'] },
  { id: 'competencia', feats: ['competencia'] },
  { id: 'posicion', feats: ['g_POR', 'g_DEF', 'g_MED', 'g_DEL'] },
];

// Probabilidad y aporte de cada factor: diferencia (en puntos porcentuales) contra el mismo
// fichaje con ese factor en su valor promedio historico.
export function explicar(j, destId, ctx, factorMonto = 1) {
  const { modelo } = ctx;
  const { x, info } = variables(j, destId, ctx, factorMonto);
  const z = estandarizar(x, modelo);
  const p = sigmoide(logit(z, modelo));
  const factores = FACTORES.map((f) => {
    const zz = z.slice();
    modelo.feats.forEach((nombre, i) => { if (f.feats.includes(nombre)) zz[i] = 0; });
    return { ...f, pp: (p - sigmoide(logit(zz, modelo))) * 100 };
  }).sort((a, b) => Math.abs(b.pp) - Math.abs(a.pp));
  return { p, factores, info };
}
