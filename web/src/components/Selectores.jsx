import { useMemo, useState } from 'react';
import { dinero } from '../datos.js';
import { Escudo, Foto } from './Insignias.jsx';

export function normalizar(s) {
  return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

// Campo con autocompletado para elegir un jugador o un club.
export function Autocompletar({ etiqueta, placeholder, opciones, valor, alElegir, render, id }) {
  const [q, setQ] = useState('');
  const [abierto, setAbierto] = useState(false);
  const res = useMemo(() => {
    const k = normalizar(q.trim());
    if (k.length < 2) return [];
    return opciones.filter((o) => o._n.includes(k)).slice(0, 8);
  }, [q, opciones]);
  return (
    <div style={{ position: 'relative', flex: '1 1 280px' }}>
      <label className="campo" htmlFor={id}>{etiqueta}</label>
      <input id={id} type="search" className="entrada" placeholder={placeholder}
        value={abierto ? q : (valor || '')} onFocus={() => { setQ(''); setAbierto(true); }}
        onChange={(e) => setQ(e.target.value)} onBlur={() => setTimeout(() => setAbierto(false), 150)}
        onKeyDown={(e) => { if (e.key === 'Enter' && res[0]) { alElegir(res[0]); setAbierto(false); e.target.blur(); } }} />
      {abierto && res.length > 0 && (
        <ul className="sugerencias" style={{ left: 0, right: 'auto', width: '100%' }}>
          {res.map((o) => (
            <li key={o.id}>
              <button type="button" className="sug-boton" onMouseDown={(e) => e.preventDefault()} onClick={() => { alElegir(o); setAbierto(false); }}>
                {render(o)}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function opcionJugador(clubes) {
  return (o) => (
    <>
      <Foto af={o.af} tam={32} />
      <span><strong>{o.n}</strong><small>{clubes[o.cl]?.n || ''} · {dinero(o.v)}</small></span>
    </>
  );
}

export function opcionClub(o) {
  return (
    <>
      <Escudo club={o} tam={28} />
      <span><strong>{o.n}</strong><small>{o.ligaNombre || ''}</small></span>
    </>
  );
}
