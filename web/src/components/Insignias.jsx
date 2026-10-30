import { useState } from 'react';
import { urlEscudo, urlLiga, urlFoto } from '../datos.js';

// Escudo de club: imagen de API-Football si existe; si no, iniciales.
export function Escudo({ club, tam = 22 }) {
  const [fallo, setFallo] = useState(false);
  const src = club && !fallo ? urlEscudo(club.af) : null;
  return (
    <span className={`escudo${src ? ' con-img' : ''}`} aria-hidden="true"
      style={{ width: tam, height: tam, fontSize: Math.max(7, Math.round(tam * 0.33)) }}>
      {src ? <img src={src} alt="" loading="lazy" onError={() => setFallo(true)} /> : (club ? club.c : '?')}
    </span>
  );
}

export function LogoLiga({ liga, tam = 22, claro = false }) {
  const [fallo, setFallo] = useState(false);
  const src = liga && !fallo ? urlLiga(liga.af) : null;
  const texto = liga ? liga.id.replace(/\d+$/, '').slice(0, 3) : '?';
  return (
    <span className={`logo-liga${src ? ' con-img' : ''}`} aria-hidden="true"
      style={{ width: tam, height: tam, fontSize: Math.max(7, Math.round(tam * 0.32)), ...(claro && !src ? { background: '#fff', color: '#0C1A12' } : {}) }}>
      {src ? <img src={src} alt="" loading="lazy" onError={() => setFallo(true)} /> : texto}
    </span>
  );
}

export function Foto({ af, tam = 40, nombre }) {
  const [fallo, setFallo] = useState(false);
  const src = af && !fallo ? urlFoto(af) : null;
  return (
    <span className="foto" style={{ width: tam, height: tam }} role={nombre ? 'img' : undefined}
      aria-label={nombre ? `Foto de ${nombre}` : undefined} aria-hidden={nombre ? undefined : 'true'}>
      {src ? <img src={src} alt="" loading="lazy" onError={() => setFallo(true)} /> : (
        <svg width={tam * 0.82} height={tam * 0.82} viewBox="0 0 92 92" aria-hidden="true">
          <circle cx="46" cy="34" r="18" fill="#9CC9B0" />
          <path d="M10 92 C14 64 78 64 82 92 Z" fill="#9CC9B0" />
        </svg>
      )}
    </span>
  );
}
