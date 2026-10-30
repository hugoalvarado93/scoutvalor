import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useEffect, useMemo, useState } from 'react';
import { useIdioma } from '../i18n.jsx';
import { cargarJugadores, cargar, dinero } from '../datos.js';
import { Foto } from './Insignias.jsx';

function normalizar(s) {
  return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

function Buscador() {
  const { t } = useIdioma();
  const navegar = useNavigate();
  const [q, setQ] = useState('');
  const [jug, setJug] = useState(null);
  const [clubes, setClubes] = useState({});
  const [abierto, setAbierto] = useState(false);

  const preparar = () => {
    if (!jug) {
      cargarJugadores().then((j) => setJug(j.map((x) => ({ ...x, _n: normalizar(x.n) }))));
      cargar('clubes.json').then(setClubes);
    }
  };
  const res = useMemo(() => {
    const k = normalizar(q.trim());
    if (!jug || k.length < 2) return [];
    return jug.filter((x) => x._n.includes(k)).sort((a, b) => (b.v || 0) - (a.v || 0)).slice(0, 8);
  }, [q, jug]);

  return (
    <div className="buscador-global">
      <label>
        <span className="solo-lector">{t('buscar')}</span>
        <input type="search" placeholder={t('buscar')} value={q} onFocus={() => { preparar(); setAbierto(true); }}
          onChange={(e) => { setQ(e.target.value); setAbierto(true); }}
          onBlur={() => setTimeout(() => setAbierto(false), 150)}
          onKeyDown={(e) => { if (e.key === 'Enter' && res[0]) { navegar(`/jugador/${res[0].id}`); setQ(''); setAbierto(false); } }} />
      </label>
      {abierto && res.length > 0 && (
        <ul className="sugerencias">
          {res.map((x) => (
            <li key={x.id}>
              <Link to={`/jugador/${x.id}`} onClick={() => { setQ(''); setAbierto(false); }}>
                <Foto af={x.af} tam={32} />
                <span><strong>{x.n}</strong><small>{clubes[x.cl]?.n || ''} · {dinero(x.v)}</small></span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function leerTema() {
  try { const g = localStorage.getItem('sv-tema'); if (g) return g; } catch { /* sin almacenamiento */ }
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'oscuro' : 'claro';
}

function BotonTema() {
  const { t } = useIdioma();
  const [tema, setTema] = useState(leerTema);
  useEffect(() => {
    document.documentElement.dataset.tema = tema;
    try { localStorage.setItem('sv-tema', tema); } catch { /* sin almacenamiento */ }
  }, [tema]);
  const oscuro = tema === 'oscuro';
  return (
    <button type="button" className="tema" onClick={() => setTema(oscuro ? 'claro' : 'oscuro')}
      aria-label={oscuro ? t('temaClaro') : t('temaOscuro')} title={oscuro ? t('temaClaro') : t('temaOscuro')}>
      {oscuro ? (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.5" /><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8" /></svg>
      ) : (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 10.7 10.7z" /></svg>
      )}
    </button>
  );
}

export default function Encabezado() {
  const { t, idioma, setIdioma } = useIdioma();
  return (
    <header className="encabezado">
      <div className="contenedor">
        <Link to="/" className="marca">
          <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="12" fill="none" stroke="#5FD39A" strokeWidth="2" /><path d="M7 18 L12 13 L15 16 L21 9" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /></svg>
          <span>ScoutValor</span>
        </Link>
        <nav className="nav" aria-label="Principal">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'activo' : '')}>{t('inicio')}</NavLink>
          <NavLink to="/radar" className={({ isActive }) => (isActive ? 'activo' : '')}>{t('radar')}</NavLink>
          <NavLink to="/equipos" className={({ isActive }) => (isActive ? 'activo' : '')}>{t('equipos')}</NavLink>
          <NavLink to="/simulador" className={({ isActive }) => (isActive ? 'activo' : '')}>{t('simulador')}</NavLink>
          <NavLink to="/metodologia" className={({ isActive }) => (isActive ? 'activo' : '')}>{t('metodologia')}</NavLink>
        </nav>
        <div className="encabezado-der">
          <Buscador />
          <BotonTema />
          <div className="idioma" role="group" aria-label={t('idioma')}>
            <button type="button" aria-pressed={idioma === 'es'} onClick={() => setIdioma('es')}>ES</button>
            <button type="button" aria-pressed={idioma === 'en'} onClick={() => setIdioma('en')}>EN</button>
          </div>
        </div>
      </div>
    </header>
  );
}
