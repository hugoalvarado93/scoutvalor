import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useIdioma } from '../i18n.jsx';
import { cargar, cargarJugadores, dinero, fecha, miles, paisTxt, posTxt } from '../datos.js';
import { Escudo, Foto } from '../components/Insignias.jsx';
import MapaMundi, { tono } from '../components/MapaMundi.jsx';

function Movimiento({ m, clubes, idioma, t }) {
  const club = clubes[m.cl];
  const sube = m.v1 >= m.v0;
  const factor = m.v0 > 0 ? m.v1 / m.v0 : 0;
  const etiqueta = sube ? (factor >= 3 ? `×${Math.round(factor)}` : `+${Math.round(m.pct)}%`) : `−${Math.abs(Math.round(m.pct))}%`;
  return (
    <Link to={`/jugador/${m.id}`} className="tarjeta mov">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <Foto af={m.af} tam={44} />
        <div style={{ minWidth: 0 }}>
          <div style={{ fontWeight: 700, fontSize: 16 }}>{m.n}</div>
          <div className="club-linea" style={{ fontSize: 13, color: 'var(--tenue)', marginTop: 2 }}>
            <Escudo club={club} tam={18} />{club ? club.n : ''} · {posTxt(m.p, idioma)}{m.e ? ` · ${t('anios', { n: Math.floor(m.e) })}` : ''}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 8 }}>
        <div style={{ fontSize: 14, color: 'var(--tenue)' }}>{dinero(m.v0)} → <strong style={{ color: 'var(--tinta)', fontSize: 18, fontFamily: 'var(--display)' }}>{dinero(m.v1)}</strong></div>
        <span className={`var ${sube ? 'sube' : 'baja'}`}>{etiqueta}</span>
      </div>
    </Link>
  );
}

export default function Inicio() {
  const { t, idioma } = useIdioma();
  const navegar = useNavigate();
  const [resumen, setResumen] = useState(null);
  const [paises, setPaises] = useState([]);
  const [mov, setMov] = useState(null);
  const [clubes, setClubes] = useState({});
  const [jug, setJug] = useState(null);
  const [modo, setModo] = useState('nac');
  const [verBajan, setVerBajan] = useState(false);

  useEffect(() => {
    cargar('resumen.json').then(setResumen);
    cargar('paises.json').then(setPaises);
    cargar('movimientos.json').then(setMov);
    cargar('clubes.json').then(setClubes);
    cargarJugadores().then(setJug);
  }, []);

  const afPorId = useMemo(() => {
    const m = {};
    (jug || []).forEach((j) => { m[j.id] = j.af; });
    return m;
  }, [jug]);

  const destacado = useMemo(() => {
    if (!jug) return null;
    return jug.filter((j) => j.r && (j.v || 0) >= 1e6 && j.b !== null).sort((a, b) => b.b - a.b)[0] || null;
  }, [jug]);
  const vencen = useMemo(() => (jug ? jug.filter((j) => j.r && j.ct && j.ct < '2027-07').length : null), [jug]);

  const top = useMemo(() => [...paises].sort((a, b) => (modo === 'liga' ? b.liga - a.liga : b.nac - a.nac)).slice(0, 5), [paises, modo]);

  const elegirPais = (lista) => {
    const p = new URLSearchParams();
    p.set(modo === 'liga' ? 'paisLiga' : 'nac', lista.join(','));
    navegar(`/radar?${p.toString()}`);
  };

  const lista = mov ? (verBajan ? mov.bajan : mov.suben).slice(0, 6).map((m) => ({ ...m, af: afPorId[m.id] })) : [];

  return (
    <>
      <section className="heroe">
        <div className="contenedor">
          <div style={{ flex: '1 1 560px', maxWidth: 760 }}>
            {resumen && <p className="sello" style={{ margin: 0 }}>{t('datosAl', { f: fecha(resumen.fecha_datos, idioma), p: fecha(resumen.proxima, idioma) })}</p>}
            <h1>{t('heroTitulo')}</h1>
            <p className="lead">{t('heroTexto', { ligas: resumen ? resumen.ligas : 47 })}</p>
            <div className="acciones">
              <Link to="/radar" className="boton">{t('abrirRadar')}</Link>
              <Link to="/equipos" className="boton fantasma">{t('buscarReemplazos')}</Link>
            </div>
          </div>
          <dl className="cifras">
            <div><dt>{t('jugadoresActivos')}</dt><dd>{resumen ? miles(resumen.jugadores) : '—'}</dd></div>
            <div><dt>{t('ligas')}</dt><dd>{resumen ? resumen.ligas : '—'}</dd></div>
            <div><dt>{t('equiposN')}</dt><dd>{resumen ? miles(resumen.equipos) : '—'}</dd></div>
            <div><dt>{t('actualizacion')}</dt><dd>{t('semanal')}</dd></div>
          </dl>
        </div>
      </section>

      <main className="contenedor" style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
        <section aria-labelledby="mapa-t" className="tarjeta" style={{ padding: 28 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: 16 }}>
            <div>
              <h2 id="mapa-t" className="seccion">{t('exploraPais')}</h2>
              <p className="subtitulo" style={{ marginTop: 6, fontSize: 15 }}>{t('exploraPaisTxt')}</p>
            </div>
            <div className="alternador" role="group">
              <button type="button" aria-pressed={modo === 'nac'} onClick={() => setModo('nac')}>{t('nacionalidad')}</button>
              <button type="button" aria-pressed={modo === 'liga'} onClick={() => setModo('liga')}>{t('ligaDelPais')}</button>
            </div>
          </div>
          <div className="fila-flex" style={{ marginTop: 20 }}>
            <div style={{ flex: '999 1 640px', minWidth: 0 }}>
              <MapaMundi paises={paises} modo={modo} alElegir={elegirPais} />
            </div>
            <div style={{ flex: '1 1 220px', display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <h3 style={{ margin: '0 0 10px', fontSize: 13, fontWeight: 600, color: 'var(--tenue)' }}>{modo === 'liga' ? t('jugadoresPorLiga') : t('jugadoresPorNac')}</h3>
                <ul className="leyenda">
                  {[[800, '800+'], [500, '500 – 799'], [300, '300 – 499'], [150, '150 – 299'], [50, '50 – 149'], [1, '1 – 49']].map(([n, l]) => (
                    <li key={l}><i style={{ background: tono(n) }} />{l}</li>
                  ))}
                </ul>
              </div>
              <div style={{ borderTop: '1px solid var(--linea)', paddingTop: 16 }}>
                <h3 style={{ margin: '0 0 10px', fontSize: 13, fontWeight: 600, color: 'var(--tenue)' }}>{t('masJugadores')}</h3>
                <ol style={{ margin: 0, paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6, fontSize: 14 }}>
                  {top.map((p) => (
                    <li key={p.pais}><button type="button" className="boton-texto" style={{ height: 'auto', padding: 0, fontSize: 14 }} onClick={() => elegirPais([p.pais])}>{paisTxt(p.pais, idioma)}</button> · {miles(modo === 'liga' ? p.liga : p.nac)}</li>
                  ))}
                </ol>
              </div>
            </div>
          </div>
        </section>

        <section aria-labelledby="cambios-t">
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: 12 }}>
            <div>
              <h2 id="cambios-t" className="seccion">{t('cambiosTitulo')}</h2>
              {mov && <p className="subtitulo" style={{ marginTop: 6, fontSize: 15 }}>{t('cambiosTxt', { f: fecha(String(mov.fecha).slice(0, 10), idioma) })}</p>}
            </div>
            <div className="alternador" role="group">
              <button type="button" aria-pressed={!verBajan} onClick={() => setVerBajan(false)}>{t('suben')}</button>
              <button type="button" aria-pressed={verBajan} onClick={() => setVerBajan(true)}>{t('bajan')}</button>
            </div>
          </div>
          <div className="rejilla-mov" style={{ marginTop: 16 }}>
            {lista.map((m) => <Movimiento key={m.id} m={m} clubes={clubes} idioma={idioma} t={t} />)}
          </div>
        </section>

        <section style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
          <Link to={destacado ? `/jugador/${destacado.id}` : '/radar'} className="tarjeta" style={{ flex: '1 1 300px', padding: 22, textDecoration: 'none', color: 'var(--tinta)' }}>
            <p className="sobretitulo" style={{ margin: 0 }}>{t('radarSemana')}</p>
            {destacado && <>
              <p style={{ margin: '10px 0 0', fontFamily: 'var(--display)', fontSize: 22, fontWeight: 800 }}>{destacado.n}</p>
              <p className="club-linea" style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--tenue)' }}>
                <Escudo club={clubes[destacado.cl]} tam={18} />{clubes[destacado.cl]?.n} · {dinero(destacado.v)} → {dinero(destacado.ve)} · +{destacado.b}%
              </p>
            </>}
          </Link>
          <Link to="/radar?contrato=2027-07" className="tarjeta" style={{ flex: '1 1 300px', padding: 22, textDecoration: 'none', color: 'var(--tinta)' }}>
            <p className="sobretitulo" style={{ margin: 0 }}>{t('ventanaContratos')}</p>
            <p style={{ margin: '10px 0 0', fontFamily: 'var(--display)', fontSize: 22, fontWeight: 800 }}>{vencen !== null ? miles(vencen) : '—'}</p>
            <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--tenue)' }}>{t('vencenAntes')}</p>
          </Link>
          <Link to="/metodologia" style={{ flex: '1 1 300px', padding: 22, borderRadius: 12, background: 'var(--noche)', textDecoration: 'none', color: '#fff' }}>
            <p style={{ margin: 0, fontSize: 12, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#A8E6C6' }}>{t('metodologia')}</p>
            <p style={{ margin: '10px 0 0', fontFamily: 'var(--display)', fontSize: 22, fontWeight: 800 }}>{t('inspirado')}</p>
            <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--noche-tenue)' }}>{t('metodoTxt')}</p>
          </Link>
        </section>
      </main>
    </>
  );
}
