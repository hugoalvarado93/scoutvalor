import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useIdioma } from '../i18n.jsx';
import { dinero, mesAnio, miles, paisTxt, posTxt } from '../datos.js';
import { cargarContexto, explicar } from '../modelo.js';
import { Escudo, Foto, LogoLiga } from '../components/Insignias.jsx';
import { Autocompletar, normalizar, opcionClub, opcionJugador } from '../components/Selectores.jsx';

function Anillo({ p }) {
  const c = 2 * Math.PI * 54;
  return (
    <svg role="img" aria-label={`${Math.round(p * 100)}%`} width="180" height="180" viewBox="0 0 140 140">
      <circle cx="70" cy="70" r="54" fill="none" strokeWidth="14" style={{ stroke: 'var(--linea-suave)' }} />
      <circle cx="70" cy="70" r="54" fill="none" strokeWidth="14" strokeLinecap="round" strokeDasharray={`${c * p} ${c}`}
        transform="rotate(-90 70 70)" style={{ stroke: 'var(--marca)' }} />
      <text x="70" y="79" textAnchor="middle" fontSize="30" fontWeight="800" style={{ fill: 'var(--tinta)', fontFamily: 'var(--display)' }}>{Math.round(p * 100)}%</text>
    </svg>
  );
}

export default function Simulador() {
  const { t, idioma } = useIdioma();
  const [params, setParams] = useSearchParams();
  const [ctx, setCtx] = useState(null);

  useEffect(() => { cargarContexto().then(setCtx); }, []);

  const opcJug = useMemo(() => (ctx ? ctx.jugadores.filter((j) => j.v).map((j) => ({ ...j, _n: normalizar(j.n) })).sort((a, b) => b.v - a.v) : []), [ctx]);
  const opcClub = useMemo(() => {
    if (!ctx) return [];
    return Object.entries(ctx.clubes).filter(([id]) => ctx.clubesCtx[id])
      .map(([id, c]) => ({ ...c, id: Number(id), _n: normalizar(c.n), ligaNombre: ctx.ligaPorId[c.l]?.nombre }));
  }, [ctx]);

  if (!ctx) return <main className="contenedor"><div className="cargando">{t('cargando')}</div></main>;

  const porDefecto = opcJug.find((j) => j.n === 'Milton Delgado') || opcJug[0];
  const j = ctx.jugPorId[params.get('j')] || porDefecto;
  const destId = Number(params.get('c')) || 2407;
  const dest = ctx.clubes[destId];
  const ligaD = dest ? ctx.ligaPorId[dest.l] : null;
  const ligaO = ctx.ligaPorId[j.lg];
  const clubO = ctx.clubes[j.cl];
  const monto = Number(params.get('m') ?? 1);
  const r = explicar(j, destId, ctx, monto);
  const max = Math.max(5, ...r.factores.map((f) => Math.abs(f.pp)));
  const par = ctx.pares[`${j.lg}>${dest?.l}`];
  const serie = par ? Object.entries(par[2]).sort() : [];
  const smax = Math.max(1, ...serie.map(([, n]) => n));

  const entrada = (f) => {
    const i = r.info;
    switch (f.id) {
      case 'minutos': return i.minutos ? t('fMinutos', { n: miles(i.minutos) }) : t('fSinMinutos');
      case 'movimiento': return i.local ? t('fLocal') : i.idioma ? t('fIdioma') : i.conf ? t('fConf') : t('fOtro');
      case 'edad': return t('anios', { n: Math.floor(j.e || 0) });
      case 'valor': return `${t('valorMercado')} ${dinero(j.v)} · ${t('fMonto', { m: monto ? dinero((j.v || 0) * monto) : t('montoLibre') })}`;
      case 'liga': return `${ligaO?.nombre || '—'} → ${ligaD?.nombre || '—'}`;
      case 'club': return `${clubO?.n || '—'} → ${dest?.n || '—'}`;
      case 'compatriotas': return t('fCompatriotas', { n: i.compatriotas, p: paisTxt(j.nac, idioma) });
      case 'competencia': return t('fCompetencia', { n: i.competencia });
      case 'posicion': return posTxt(j.p, idioma);
      default: return '';
    }
  };

  return (
    <main className="contenedor" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <p className="sobretitulo">{t('moduloC')}</p>
        <h1 className="titulo">{t('simulador')}</h1>
        <p className="subtitulo">{t('simTxt', { n: miles(ctx.modelo.n) })}</p>
      </div>

      <div className="tarjeta relleno" style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end' }}>
        <Escudo club={clubO} tam={44} />
        <Autocompletar id="sim-jugador" etiqueta={t('jugador')} placeholder={t('buscar')} opciones={opcJug} valor={`${j.n} · ${clubO?.n || ''}`}
          render={opcionJugador(ctx.clubes)} alElegir={(o) => setParams({ j: o.id, c: destId, m: monto }, { replace: true })} />
        <svg width="28" height="44" viewBox="0 0 28 44" aria-hidden="true"><path d="M4 22 H22 M16 15 L23 22 L16 29" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ stroke: 'var(--tenue)' }} /></svg>
        <Escudo club={dest} tam={44} />
        <Autocompletar id="sim-club" etiqueta={t('clubDestino')} placeholder={t('buscarClub')} opciones={opcClub} valor={dest ? `${dest.n} · ${ligaD?.nombre || ''}` : ''}
          render={opcionClub} alElegir={(o) => setParams({ j: j.id, c: o.id, m: monto }, { replace: true })} />
        <label className="campo" style={{ flex: '0 1 220px' }}>{t('montoTraspaso')}
          <select className="entrada" value={monto} onChange={(e) => setParams({ j: j.id, c: destId, m: e.target.value }, { replace: true })}>
            <option value="0">{t('montoLibre')}</option>
            <option value="0.5">{t('montoMitad')} · {dinero((j.v || 0) * 0.5)}</option>
            <option value="1">{t('montoValor')} · {dinero(j.v)}</option>
            <option value="1.5">{t('montoPrima')} · {dinero((j.v || 0) * 1.5)}</option>
          </select>
        </label>
      </div>

      <div className="fila-flex" style={{ gap: 20, alignItems: 'stretch' }}>
        <section className="tarjeta relleno" style={{ flex: '1 1 320px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 12 }}>
          <h2 className="tarjeta-t" style={{ alignSelf: 'flex-start' }}>{t('probExito')}</h2>
          <Anillo p={r.p} />
          <p style={{ margin: 0, fontSize: 14, color: 'var(--tenue)', maxWidth: 320 }}>{t('defExito')}</p>
          <p style={{ margin: 0, fontSize: 13, color: 'var(--tenue)' }}>{t('tasaBase')}: <strong style={{ color: 'var(--tinta)' }}>{Math.round(ctx.modelo.tasa_base * 100)}%</strong> · AUC {ctx.modelo.auc}</p>
        </section>

        <section className="tarjeta relleno" style={{ flex: '2 1 560px', minWidth: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 8 }}>
            <h2 className="tarjeta-t">{t('queMueve')}</h2>
            <span className="nota">{t('puntosVsPromedio')}</span>
          </div>
          <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {r.factores.map((f) => {
              const w = `${Math.min(100, (Math.abs(f.pp) / max) * 100)}%`;
              return (
                <div key={f.id} style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 14, flexWrap: 'wrap' }}>
                  <div style={{ flex: '1 1 240px', minWidth: 0 }}><div style={{ fontWeight: 600 }}>{t(`fac_${f.id}`)}</div><div className="nota">{entrada(f)}</div></div>
                  <div style={{ flex: '1 1 220px', display: 'flex', alignItems: 'center' }}>
                    <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end', height: 14 }}>{f.pp < 0 && <div style={{ height: 14, width: w, borderRadius: '4px 0 0 4px', background: 'var(--naranja)' }} />}</div>
                    <div style={{ width: 2, height: 22, background: 'var(--tinta)' }} />
                    <div style={{ flex: 1, display: 'flex', height: 14 }}>{f.pp > 0 && <div style={{ height: 14, width: w, borderRadius: '0 4px 4px 0', background: 'var(--marca)' }} />}</div>
                  </div>
                  <span style={{ width: 52, textAlign: 'right', fontWeight: 700, color: f.pp < 0 ? 'var(--naranja-osc)' : 'var(--marca)' }}>{f.pp >= 0 ? '+' : '−'}{Math.abs(f.pp).toFixed(1)}</span>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      <div className="fila-flex" style={{ gap: 20, alignItems: 'stretch' }}>
        <section className="tarjeta relleno" style={{ flex: '1 1 420px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <Foto af={j.af} tam={56} nombre={j.n} />
            <div>
              <h2 className="tarjeta-t"><Link to={`/jugador/${j.id}`} style={{ color: 'var(--tinta)', textDecoration: 'none' }}>{j.n}</Link></h2>
              <p className="club-linea nota" style={{ margin: '4px 0 0', fontSize: 14, flexWrap: 'wrap' }}>
                {posTxt(j.p, idioma)} · <Escudo club={clubO} tam={20} />{clubO?.n} · <LogoLiga liga={ligaO} tam={20} />{ligaO?.nombre}
              </p>
            </div>
          </div>
          <dl style={{ margin: '16px 0 0', display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 14 }}>
            {[[t('edad'), j.e ? Math.floor(j.e) : '—'], [t('nac'), paisTxt(j.nac, idioma)], [t('valorMercado'), dinero(j.v)],
              [t('contrato'), j.ct ? mesAnio(j.ct, idioma) : t('sinDato')], [t('minutos'), r.info.minutos ? miles(r.info.minutos) : '—'], [t('calificacion'), j.cal ? j.cal.toFixed(2) : '—']].map(([k, v]) => (
              <div key={k}><dt className="nota">{k}</dt><dd style={{ margin: '2px 0 0', fontFamily: 'var(--display)', fontSize: 20, fontWeight: 800 }}>{v}</dd></div>
            ))}
          </dl>
        </section>

        <section className="tarjeta relleno" style={{ flex: '1 1 420px' }}>
          <h2 className="tarjeta-t">{t('comparables')}</h2>
          {par ? (
            <>
              <p className="club-linea" style={{ margin: '6px 0 0', fontSize: 14, color: 'var(--tenue)', flexWrap: 'wrap' }}>
                <strong style={{ color: 'var(--tinta)' }}>{t('traspasosN', { n: par[0] })}</strong> <LogoLiga liga={ligaO} tam={20} />{ligaO?.nombre} → <LogoLiga liga={ligaD} tam={20} />{ligaD?.nombre} {t('desde2017')}
              </p>
              {par[1] !== null && <p style={{ margin: '6px 0 0', fontSize: 14 }}>{t('tasaPar', { p: Math.round(par[1] * 100) })}</p>}
              <div role="img" aria-label={serie.map(([s, n]) => `${s}: ${n}`).join(', ')} style={{ marginTop: 16, height: 140, display: 'flex', alignItems: 'flex-end', gap: 10 }}>
                {serie.map(([s, n]) => (
                  <div key={s} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                    <span style={{ fontSize: 12, fontWeight: 700 }}>{n}</span>
                    <div style={{ width: '100%', maxWidth: 44, height: `${(n / smax) * 90}px`, borderRadius: '6px 6px 0 0', background: 'var(--m4)' }} />
                    <span className="nota">{s.slice(2)}</span>
                  </div>
                ))}
              </div>
            </>
          ) : <p className="nota" style={{ fontSize: 14 }}>{t('sinComparables')}</p>}
        </section>
      </div>
      <p className="nota">{t('simNota')}</p>
    </main>
  );
}
