import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useIdioma } from '../i18n.jsx';
import { cargar, cargarDetalle, cargarJugadores, dinero, fecha, mesAnio, miles, paisTxt, posTxt } from '../datos.js';
import { Escudo, Foto, LogoLiga } from '../components/Insignias.jsx';

function GraficaValor({ puntos, traspasos, idioma }) {
  if (!puntos || puntos.length < 2) return null;
  const W = 680, H = 240, iz = 48, de = 16, ar = 16, ab = 40;
  const t0 = new Date(puntos[0][0]).getTime();
  const t1 = new Date(puntos[puntos.length - 1][0]).getTime();
  const vmax = Math.max(...puntos.map((p) => p[1])) * 1.1 || 1;
  const x = (f) => iz + ((new Date(f).getTime() - t0) / Math.max(1, t1 - t0)) * (W - iz - de);
  const y = (v) => H - ab - (v / vmax) * (H - ar - ab);
  const linea = puntos.map((p) => `${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ');
  const marcas = [0, 0.33, 0.66, 1].map((k) => vmax / 1.1 * k);
  const anioIni = new Date(puntos[0][0]).getFullYear();
  const anioFin = new Date(puntos[puntos.length - 1][0]).getFullYear();
  const anios = [];
  for (let a = anioIni + 1; a <= anioFin; a++) anios.push(a);
  const paso = Math.ceil(anios.length / 8) || 1;
  const tr = (traspasos || []).filter((r) => { const tt = new Date(r.f).getTime(); return tt >= t0 && tt <= t1 && r.fee > 0; });
  const ultimo = puntos[puntos.length - 1];
  return (
    <svg role="img" aria-label={`Valor de mercado de ${dinero(puntos[0][1])} a ${dinero(ultimo[1])}`} viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto' }}>
      {marcas.map((m) => (
        <g key={m}>
          <line x1={iz} x2={W - de} y1={y(m)} y2={y(m)} style={{ stroke: m === 0 ? 'var(--linea)' : 'var(--linea-suave)' }} />
          <text x={iz - 8} y={y(m) + 4} textAnchor="end" fontSize="11" style={{ fill: 'var(--tenue)' }}>{dinero(Math.round(m))}</text>
        </g>
      ))}
      {anios.filter((_, i) => i % paso === 0).map((a) => (
        <text key={a} x={x(`${a}-01-01`)} y={H - 14} textAnchor="middle" fontSize="11" style={{ fill: 'var(--tenue)' }}>{a}</text>
      ))}
      {tr.map((r) => (
        <g key={r.f}>
          <line x1={x(r.f)} x2={x(r.f)} y1={ar} y2={H - ab} style={{ stroke: 'var(--naranja)' }} strokeDasharray="4 4" />
          <text x={x(r.f) - 4} y={ar + 10} textAnchor="end" fontSize="11" style={{ fill: 'var(--naranja-osc)' }}>{r.a} · {dinero(r.fee)}</text>
        </g>
      ))}
      <polyline points={linea} fill="none" style={{ stroke: 'var(--marca)' }} strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={x(ultimo[0])} cy={y(ultimo[1])} r="5" style={{ fill: 'var(--marca)' }} />
    </svg>
  );
}

export default function Jugador() {
  const { id } = useParams();
  const { t, idioma } = useIdioma();
  const [base, setBase] = useState(undefined);
  const [det, setDet] = useState(null);
  const [clubes, setClubes] = useState({});
  const [ligas, setLigas] = useState([]);
  const [por90, setPor90] = useState(false);

  useEffect(() => {
    setBase(undefined); setDet(null);
    cargarJugadores().then((js) => setBase(js.find((j) => String(j.id) === String(id)) || null));
    cargarDetalle(id).then(setDet);
    cargar('clubes.json').then(setClubes);
    cargar('ligas.json').then(setLigas);
  }, [id]);

  const ligaPorId = useMemo(() => Object.fromEntries(ligas.map((l) => [l.id, l])), [ligas]);
  const ligaPorAf = useMemo(() => Object.fromEntries(ligas.filter((l) => l.af).map((l) => [l.af, l])), [ligas]);
  const clubPorNombre = useMemo(() => {
    const m = {};
    Object.entries(clubes).forEach(([k, c]) => { m[k] = c; });
    return m;
  }, [clubes]);

  if (base === undefined) return <main className="contenedor"><div className="cargando">{t('cargando')}</div></main>;
  if (base === null) return <main className="contenedor"><div className="cargando">{t('noEncontrado')} <Link to="/radar">{t('radar')}</Link></div></main>;

  const club = clubes[base.cl];
  const liga = ligaPorId[base.lg];
  const vh = det?.vh || [];
  const vmax = vh.length ? Math.max(...vh.map((v) => v[1])) : base.vmax;
  const temporadas = (det?.ts || []).filter((s) => (s.minutos || 0) > 0);
  const traspasos = det?.tr || [];

  const val = (s, k) => {
    const v = s[k];
    if (v === null || v === undefined) return '—';
    if (!por90 || ['partidos', 'titularidades', 'minutos', 'calificacion'].includes(k)) return k === 'calificacion' ? Number(v).toFixed(2) : miles(Math.round(v));
    if (!s.minutos) return '—';
    return (v / (s.minutos / 90)).toFixed(2);
  };

  return (
    <main className="contenedor" style={{ display: 'flex', flexDirection: 'column', gap: 20, paddingTop: 24 }}>
      <nav aria-label="Ruta" className="club-linea" style={{ fontSize: 13, color: 'var(--tenue)', flexWrap: 'wrap' }}>
        <Link to="/radar">{t('radar')}</Link> /
        {liga && <><LogoLiga liga={liga} tam={18} /><Link to={`/radar?liga=${liga.id}`}>{liga.nombre}</Link> /</>}
        {club && <><Escudo club={club} tam={18} />{club.n} /</>} <span>{base.n}</span>
      </nav>

      <section className="tarjeta cabecera-jugador">
        <figure style={{ margin: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
          <Foto af={base.af} tam={112} nombre={base.n} />
          <figcaption className="nota" style={{ fontSize: 11 }}>{t('fotoFuente')}</figcaption>
        </figure>
        <div style={{ flex: '1 1 360px' }}>
          <h1>{base.n}</h1>
          <p className="meta-jugador">
            {posTxt(base.p, idioma)} ·
            {club && <span className="club-linea" style={{ color: 'var(--tinta)', fontWeight: 600 }}><Escudo club={club} tam={24} />{club.n}</span>}
            {liga && <span className="club-linea"><LogoLiga liga={liga} tam={24} />{liga.nombre}</span>}
            · {paisTxt(base.nac, idioma)}{base.e ? ` · ${t('anios', { n: Math.floor(base.e) })}` : ''}
          </p>
          <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            <span className="etiqueta">{base.ct ? t('contratoHasta', { c: mesAnio(base.ct, idioma) }) : `${t('contrato')}: ${t('sinDato')}`}</span>
            {base.h && <span className="etiqueta">{base.h} cm</span>}
            {base.pie && <span className="etiqueta">{t('pie')}: {t(base.pie === 'right' ? 'derecho' : base.pie === 'left' ? 'izquierdo' : 'ambos')}</span>}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <Link to={`/simulador?j=${base.id}`} className="boton">{t('simularFichaje')}</Link>
        </div>
      </section>

      <section className="rejilla-kpi">
        <div className="tarjeta relleno kpi"><p className="k-etq">{t('valorMercado')}</p><p className="k-val">{dinero(base.v)}</p><p className="k-sub">{t('maxHistorico', { v: dinero(vmax) })}</p></div>
        <div className="tarjeta relleno kpi"><p className="k-etq">{t('porElModelo')}</p><p className="k-val">{base.ve ? dinero(base.ve) : '—'}</p>
          <p className="k-sub" style={{ color: base.b === null ? 'var(--tenue)' : base.b >= 0 ? 'var(--marca)' : 'var(--naranja-osc)', fontWeight: 600 }}>
            {base.b === null ? t('sinEstimacion') : `${t('brecha')} ${base.b >= 0 ? '+' : '−'}${Math.abs(base.b)}%`}</p></div>
        <div className="tarjeta relleno kpi"><p className="k-etq">{t('goles')} / {t('asistencias')} · {t('ultimas2')}</p><p className="k-val">{base.g ?? '—'} / {base.a ?? '—'}</p><p className="k-sub">{base.min ? `${miles(base.min)} min` : ''}</p></div>
        <div className="tarjeta relleno kpi"><p className="k-etq">{t('calificacion')} · {t('ultimas2')}</p><p className="k-val">{base.cal ? base.cal.toFixed(2) : '—'}</p><p className="k-sub">API-Football</p></div>
      </section>

      <div className="fila-flex" style={{ gap: 20, alignItems: 'stretch' }}>
        <section className="tarjeta relleno" style={{ flex: '3 1 560px', minWidth: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 8 }}>
            <h2 className="tarjeta-t">{t('valorHistorico')}</h2>
            {vh.length > 0 && <span className="nota">Transfermarkt · {fecha(vh[0][0], idioma)} – {fecha(vh[vh.length - 1][0], idioma)}</span>}
          </div>
          <div style={{ marginTop: 12 }}>{det ? <GraficaValor puntos={vh} traspasos={traspasos} idioma={idioma} /> : <div className="cargando">{t('cargando')}</div>}</div>
        </section>

        <section className="tarjeta relleno" style={{ flex: '2 1 360px', minWidth: 0 }}>
          <h2 className="tarjeta-t">{t('historialClubes')}</h2>
          {traspasos.length === 0 ? <p className="nota">{t('sinTraspasos')}</p> : (
            <ol className="linea-tiempo">
              {traspasos.map((r, i) => {
                const c = r.ai ? clubPorNombre[r.ai] : null;
                const actual = i === 0;
                const fee = r.fee > 0 ? `${t('traspaso')} · ${dinero(r.fee)}` : t('libre');
                return (
                  <li key={`${r.f}-${i}`}>
                    <div className="eje">
                      {c ? <Escudo club={c} tam={32} /> : <span className="escudo" aria-hidden="true" style={{ width: 32, height: 32, fontSize: 9, background: actual ? 'var(--marca)' : undefined, color: actual ? '#fff' : undefined }}>{(r.a || '?').slice(0, 3).toUpperCase()}</span>}
                      <i />
                    </div>
                    <div className="cuerpo">
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' }}>
                        <strong style={{ fontSize: 15 }}>{c ? c.n : r.a}</strong>
                        <span className="nota" style={{ fontSize: 13 }}>{fecha(r.f, idioma)}</span>
                      </div>
                      <div className="nota" style={{ fontSize: 13, marginTop: 2 }}>{t('club')}: {r.de} → {r.a} · {fee}</div>
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
        </section>
      </div>

      <section className="tarjeta">
        <div style={{ padding: '18px 20px 6px', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
          <h2 className="tarjeta-t">{t('estadisticas')}</h2>
          <div className="alternador" role="group">
            <button type="button" aria-pressed={!por90} onClick={() => setPor90(false)}>{t('totales')}</button>
            <button type="button" aria-pressed={por90} onClick={() => setPor90(true)}>{t('por90')}</button>
          </div>
        </div>
        {temporadas.length === 0 ? <p className="nota" style={{ padding: '0 20px 20px' }}>{t('sinTemporadas')}</p> : (
          <div className="tabla-caja">
            <table className="tabla" style={{ minWidth: 980 }}>
              <thead>
                <tr>
                  <th scope="col">{t('temporada')}</th>
                  <th scope="col">{t('club')}</th>
                  <th scope="col" className="der">{t('pj')}</th>
                  <th scope="col" className="der">{t('titular')}</th>
                  <th scope="col" className="der">{t('minutos')}</th>
                  <th scope="col" className="der">{t('goles')}</th>
                  <th scope="col" className="der">{t('asistencias')}</th>
                  <th scope="col" className="der">{t('pasesClave')}</th>
                  <th scope="col" className="der">{t('entradas')}</th>
                  <th scope="col" className="der">{t('intercepciones')}</th>
                  <th scope="col" className="der">{t('calificacion')}</th>
                </tr>
              </thead>
              <tbody>
                {temporadas.map((s, i) => {
                  const lg = ligaPorAf[s.api_liga];
                  return (
                    <tr key={`${s.temporada}-${s.api_equipo}-${i}`}>
                      <th scope="row" style={{ textAlign: 'left', fontWeight: 600, textTransform: 'none', letterSpacing: 0, color: 'var(--tinta)', fontSize: 14, borderBottom: '1px solid var(--linea-suave)' }}>{s.temporada}</th>
                      <td>
                        <span className="club-linea">
                          <Escudo club={{ af: s.api_equipo, c: (s.equipo || '?').slice(0, 3).toUpperCase() }} tam={22} />{s.equipo}
                          {lg && <span className="club-linea nota" style={{ fontSize: 12 }}><LogoLiga liga={lg} tam={16} />{lg.nombre}</span>}
                        </span>
                      </td>
                      <td className="der">{val(s, 'partidos')}</td>
                      <td className="der">{val(s, 'titularidades')}</td>
                      <td className="der">{val(s, 'minutos')}</td>
                      <td className="der" style={{ fontWeight: 700 }}>{val(s, 'goles')}</td>
                      <td className="der">{val(s, 'asistencias')}</td>
                      <td className="der">{val(s, 'pases_clave')}</td>
                      <td className="der">{val(s, 'entradas')}</td>
                      <td className="der">{val(s, 'intercepciones')}</td>
                      <td className="der" style={{ fontWeight: 600 }}>{val(s, 'calificacion')}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        <p className="nota" style={{ padding: '10px 20px 16px', margin: 0 }}>API-Football</p>
      </section>

      <section className="tarjeta relleno" aria-labelledby="news-t">
        <h2 id="news-t" className="tarjeta-t">{t('noticias')}</h2>
        <p className="nota" style={{ fontSize: 14, marginTop: 6 }}>{t('noticiasPronto')}</p>
      </section>
    </main>
  );
}
