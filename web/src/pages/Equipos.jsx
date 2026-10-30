import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useIdioma } from '../i18n.jsx';
import { cargar, dinero, mesAnio, paisTxt, posTxt } from '../datos.js';
import { cargarContexto, probabilidad, COMPAT } from '../modelo.js';
import { Escudo, Foto, LogoLiga } from '../components/Insignias.jsx';
import { Autocompletar, normalizar, opcionClub } from '../components/Selectores.jsx';

const HOY = new Date();
function mesesHasta(ct) {
  if (!ct) return null;
  const [a, m] = ct.split('-').map(Number);
  return (a - HOY.getFullYear()) * 12 + (m - 1 - HOY.getMonth());
}
function necesidad(j) {
  if (!j) return 'Alta';
  const meses = mesesHasta(j.ct);
  if ((j.e || 0) >= 32 || (meses !== null && meses <= 12)) return 'Alta';
  if ((j.e || 0) >= 29 || meses === null || meses <= 24) return 'Media';
  return 'Baja';
}
const NEC = { Alta: { bg: 'var(--naranja-tinte)', ink: 'var(--naranja-osc)' }, Media: { bg: 'var(--linea-suave)', ink: 'var(--tinta)' }, Baja: { bg: 'var(--marca-tinte)', ink: 'var(--marca-osc)' } };

function asequibilidad(v, ref, ct) {
  if (!v) return 50;
  const r = ref > 0 ? ref : 5e6;
  let s;
  if (v <= 0.5 * r) s = 100;
  else if (v >= 2 * r) s = 0;
  else s = 100 * (1 - Math.log(v / (0.5 * r)) / Math.log(4));
  const meses = mesesHasta(ct);
  if (meses !== null && meses <= 12) s += 15;
  return Math.max(0, Math.min(100, Math.round(s)));
}

const PESOS0 = { sim: 35, adapt: 30, aseq: 20, cal: 15 };

export default function Equipos() {
  const { t, idioma } = useIdioma();
  const [params, setParams] = useSearchParams();
  const [ctx, setCtx] = useState(null);
  const [xi, setXi] = useState(null);
  const [perf, setPerf] = useState(null);
  const [sel, setSel] = useState(10);
  const [pesos, setPesos] = useState(PESOS0);

  useEffect(() => {
    cargarContexto().then(setCtx);
    cargar('xi.json').then(setXi);
    cargar('perfiles.json').then((p) => {
      const m = {};
      p.id.forEach((id, i) => { m[id] = { z: p.z[i], q: p.q[i] }; });
      setPerf(m);
    });
  }, []);

  const clubId = Number(params.get('c')) || 2407;
  const opcClub = useMemo(() => {
    if (!ctx || !xi) return [];
    return Object.entries(ctx.clubes).filter(([id]) => xi[id])
      .map(([id, c]) => ({ ...c, id: Number(id), _n: normalizar(c.n), ligaNombre: ctx.ligaPorId[c.l]?.nombre }));
  }, [ctx, xi]);

  const equipo = xi && xi[clubId];
  const slots = equipo ? equipo.s : [];
  const slot = slots[sel] || slots[0];
  const titular = slot && ctx ? ctx.jugPorId[slot[3]] : null;

  const candidatos = useMemo(() => {
    if (!ctx || !perf || !slot) return [];
    const puesto = slot[0];
    const permitidos = new Set(COMPAT[puesto] || [puesto]);
    const zt = titular && perf[titular.id] ? perf[titular.id].z : null;
    const ref = ctx.clubesCtx[clubId]?.ref || 0;
    const suma = pesos.sim + pesos.adapt + pesos.aseq + pesos.cal || 1;
    const lista = [];
    for (const j of ctx.jugadores) {
      if (!permitidos.has(j.p) || Number(j.cl) === clubId || !perf[j.id] || !j.v || (j.e || 99) > 32) continue;
      const pf = perf[j.id];
      let sim;
      if (zt) {
        let d = 0;
        for (let i = 0; i < zt.length; i++) d += (zt[i] - pf.z[i]) ** 2;
        sim = Math.round(100 * Math.exp(-Math.sqrt(d) / 4));
      } else sim = pf.q;
      const p = probabilidad(j, clubId, ctx);
      const adapt = Math.round(Math.min(100, (p / 0.6) * 100));
      const aseq = asequibilidad(j.v, ref, j.ct);
      const total = (pesos.sim * sim + pesos.adapt * adapt + pesos.aseq * aseq + pesos.cal * pf.q) / suma;
      lista.push({ j, sim, p, adapt, aseq, cal: pf.q, total });
    }
    return lista.sort((a, b) => b.total - a.total).slice(0, 8);
  }, [ctx, perf, slot, titular, clubId, pesos]);

  if (!ctx || !xi) return <main className="contenedor"><div className="cargando">{t('cargando')}</div></main>;

  const club = ctx.clubes[clubId];
  const liga = club ? ctx.ligaPorId[club.l] : null;
  const elegirClub = (o) => { setParams({ c: o.id }, { replace: true }); setSel(10); };

  return (
    <main className="contenedor" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16 }}>
        <div>
          <p className="sobretitulo">{t('moduloB')}</p>
          <h1 className="titulo">{t('equiposTitulo')}</h1>
          <p className="subtitulo">{t('equiposTxt')}</p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', minWidth: 300, flex: '0 1 420px' }}>
          <Escudo club={club} tam={44} />
          <Autocompletar id="eq-club" etiqueta={t('equipo')} placeholder={t('buscarClub')} opciones={opcClub}
            valor={club ? `${club.n} · ${liga?.nombre || ''}` : ''} render={opcionClub} alElegir={elegirClub} />
        </div>
      </div>

      {!equipo ? <div className="tarjeta cargando">{t('sinXi')}</div> : (
        <div className="fila-flex" style={{ gap: 24 }}>
          <section aria-label={t('alineacion')} style={{ flex: '1 1 500px', maxWidth: 600, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 8 }}>
              <h2 className="tarjeta-t" style={{ fontSize: 20 }}>{t('xiRef')} · {equipo.f}</h2>
              <span className="nota">{t('xiNota')}</span>
            </div>
            <div className="cancha">
              <div className="cancha-lineas" aria-hidden="true">
                <i className="c-borde" /><i className="c-medio" /><i className="c-circulo" /><i className="c-area-a" /><i className="c-area-b" />
              </div>
              {slots.map(([puesto, x, y, pid], i) => {
                const j = ctx.jugPorId[pid];
                const activo = i === sel;
                return (
                  <button key={i} type="button" className={`ficha${activo ? ' activa' : ''}`} style={{ left: `${x}%`, top: `${y}%` }}
                    aria-pressed={activo} aria-label={`${posTxt(puesto, idioma)}: ${j ? j.n : t('vacante')}`} onClick={() => setSel(i)}>
                    <Foto af={j?.af} tam={44} />
                    <span className="ficha-pos">{posTxt(puesto, idioma)}</span>
                    <span className="ficha-nombre">{j ? j.n.split(' ').slice(-1)[0] : t('vacante')}</span>
                  </button>
                );
              })}
            </div>

            <div className="tarjeta tabla-caja">
              <table className="tabla" style={{ minWidth: 480, fontSize: 13 }}>
                <caption style={{ textAlign: 'left', padding: '14px 16px 4px', fontFamily: 'var(--display)', fontSize: 15, fontWeight: 700 }}>{t('necesidadPos')}</caption>
                <thead><tr><th scope="col">{t('pos')}</th><th scope="col">{t('titularCol')}</th><th scope="col" className="der">{t('edad')}</th><th scope="col">{t('contrato')}</th><th scope="col">{t('necesidad')}</th></tr></thead>
                <tbody>
                  {slots.map(([puesto, , , pid], i) => {
                    const j = ctx.jugPorId[pid];
                    const n = necesidad(j);
                    return (
                      <tr key={i} onClick={() => setSel(i)} style={{ cursor: 'pointer', background: i === sel ? 'var(--fila-hover)' : undefined }}>
                        <td style={{ fontWeight: 600 }}>{posTxt(puesto, idioma)}</td>
                        <td>{j ? <Link to={`/jugador/${j.id}`} style={{ color: 'var(--tinta)', textDecoration: 'none' }}>{j.n}</Link> : '—'}</td>
                        <td className="der">{j?.e ? Math.floor(j.e) : '—'}</td>
                        <td>{j?.ct ? mesAnio(j.ct, idioma) : <span className="sin-dato">{t('sinDato')}</span>}</td>
                        <td><span style={{ display: 'inline-block', padding: '3px 10px', borderRadius: 999, fontSize: 12, fontWeight: 700, background: NEC[n].bg, color: NEC[n].ink }}>{t(`nec${n}`)}</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              <p className="nota" style={{ margin: 0, padding: '10px 16px 14px' }}>{t('necesidadNota')}</p>
            </div>
          </section>

          <section aria-label={t('reemplazos')} className="principal" style={{ flex: '999 1 520px', gap: 14 }}>
            <div className="tarjeta relleno">
              <p className="nota" style={{ margin: 0, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{t('posSeleccionada')}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginTop: 6 }}>
                <h2 style={{ margin: 0, fontFamily: 'var(--display)', fontSize: 26, fontWeight: 800 }}>{t(`puesto_${slot[0]}`)}</h2>
                <span style={{ padding: '4px 12px', borderRadius: 999, fontSize: 13, fontWeight: 700, background: NEC[necesidad(titular)].bg, color: NEC[necesidad(titular)].ink }}>{t('necesidad')} {t(`nec${necesidad(titular)}`).toLowerCase()}</span>
              </div>
              <p style={{ margin: '8px 0 0', fontSize: 14, color: 'var(--tenue)' }}>
                {titular ? <>{t('titularCol')}: <Link to={`/jugador/${titular.id}`} style={{ fontWeight: 700, color: 'var(--tinta)' }}>{titular.n}</Link> · {t('anios', { n: Math.floor(titular.e || 0) })} · {paisTxt(titular.nac, idioma)} · {dinero(titular.v)}{perf && !perf[titular.id] ? ` · ${t('sinPerfil')}` : ''}</> : t('vacante')}
              </p>
              <fieldset style={{ border: 0, margin: '14px 0 0', padding: 0, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12 }}>
                <legend className="nota" style={{ marginBottom: 8, fontWeight: 600 }}>{t('pesos')}</legend>
                {[['sim', 'similitud'], ['adapt', 'adaptacion'], ['aseq', 'asequibilidad'], ['cal', 'calidad']].map(([k, et]) => (
                  <label key={k} className="campo" style={{ fontWeight: 500 }}>
                    <span style={{ display: 'flex', justifyContent: 'space-between' }}>{t(et)}<strong style={{ color: 'var(--tinta)' }}>{pesos[k]}</strong></span>
                    <input type="range" min="0" max="100" step="5" value={pesos[k]} onChange={(e) => setPesos({ ...pesos, [k]: Number(e.target.value) })} style={{ height: 24, padding: 0, border: 0, accentColor: 'var(--marca)' }} />
                  </label>
                ))}
              </fieldset>
            </div>

            {!perf ? <div className="tarjeta cargando">{t('cargando')}</div> : candidatos.map((c, i) => {
              const cl = ctx.clubes[c.j.cl];
              const lg = ctx.ligaPorId[c.j.lg];
              return (
                <article key={c.j.id} className="tarjeta" style={{ padding: '16px 20px', display: 'flex', flexWrap: 'wrap', gap: 18, alignItems: 'center', borderColor: i === 0 ? 'var(--marca)' : undefined }}>
                  <div style={{ width: 60, textAlign: 'center' }}>
                    <div style={{ fontFamily: 'var(--display)', fontSize: 32, fontWeight: 800, lineHeight: 1, color: c.total >= 60 ? 'var(--marca)' : 'var(--tenue)' }}>{Math.round(c.total)}</div>
                    <div className="nota" style={{ fontSize: 11, marginTop: 4 }}>{t('puntaje')}</div>
                  </div>
                  <Foto af={c.j.af} tam={48} />
                  <div style={{ flex: '1 1 200px', minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}><span className="nota">#{i + 1}</span><Link to={`/jugador/${c.j.id}`} style={{ fontSize: 17, fontWeight: 700, color: 'var(--tinta)', textDecoration: 'none' }}>{c.j.n}</Link></div>
                    <div className="club-linea nota" style={{ fontSize: 13, marginTop: 4, flexWrap: 'wrap' }}><Escudo club={cl} tam={20} />{cl?.n} · <LogoLiga liga={lg} tam={18} />{lg?.nombre}</div>
                    <div style={{ fontSize: 13, marginTop: 6 }}>{posTxt(c.j.p, idioma)} · {t('anios', { n: Math.floor(c.j.e) })} · {paisTxt(c.j.nac, idioma)} · {dinero(c.j.v)} · {c.j.ct ? mesAnio(c.j.ct, idioma) : t('sinDato')}</div>
                    <Link to={`/simulador?j=${c.j.id}&c=${clubId}`} style={{ display: 'inline-block', marginTop: 6, fontSize: 13, fontWeight: 600 }}>{t('verSimulacion', { p: Math.round(c.p * 100) })}</Link>
                  </div>
                  <div style={{ flex: '1 1 220px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {[['similitud', c.sim], ['adaptacion', c.adapt], ['asequibilidad', c.aseq], ['calidad', c.cal]].map(([k, v]) => (
                      <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12 }}>
                        <span style={{ width: 92, color: 'var(--tenue)' }}>{t(k)}</span>
                        <div className="barra"><div style={{ width: `${v}%`, background: v < 40 ? 'var(--naranja)' : 'var(--marca)' }} /></div>
                        <span style={{ width: 26, textAlign: 'right', fontWeight: 700 }}>{v}</span>
                      </div>
                    ))}
                  </div>
                </article>
              );
            })}
            <p className="nota">{t('reemplazosNota')}</p>
          </section>
        </div>
      )}
    </main>
  );
}
