import { useMemo, useRef, useState } from 'react';
import { geoNaturalEarth1, geoPath } from 'd3-geo';
import { feature } from 'topojson-client';
import mundo from 'world-atlas/countries-110m.json';
import { paisTxt, miles } from '../datos.js';
import { useIdioma } from '../i18n.jsx';

// Nombre de pais en Transfermarkt -> nombre en Natural Earth (world-atlas 110m)
const ALIAS = {
  'United States': 'United States of America', 'Korea, South': 'South Korea', 'Korea, North': 'North Korea',
  "Cote d'Ivoire": "Côte d'Ivoire", 'Bosnia-Herzegovina': 'Bosnia and Herz.', 'DR Congo': 'Dem. Rep. Congo',
  'Czech Republic': 'Czechia', 'Türkiye': 'Turkey', 'North Macedonia': 'Macedonia', 'Central African Republic': 'Central African Rep.',
  'Equatorial Guinea': 'Eq. Guinea', 'Dominican Republic': 'Dominican Rep.', England: 'United Kingdom', Scotland: 'United Kingdom',
  Wales: 'United Kingdom', 'Northern Ireland': 'United Kingdom', Eswatini: 'eSwatini', 'Chinese Taipei': 'Taiwan',
  'The Gambia': 'Gambia', 'South Sudan': 'S. Sudan', 'Solomon Islands': 'Solomon Is.',
};

const ANCHO = 960;
const ALTO = 500;

export function tono(n) {
  if (n >= 800) return 'var(--m6)';
  if (n >= 500) return 'var(--m5)';
  if (n >= 300) return 'var(--m4)';
  if (n >= 150) return 'var(--m3)';
  if (n >= 50) return 'var(--m2)';
  if (n > 0) return 'var(--m1)';
  return 'var(--m0)';
}

export default function MapaMundi({ paises, modo, alElegir }) {
  const { idioma, t } = useIdioma();
  const caja = useRef(null);
  const [tip, setTip] = useState(null);

  const { formas, porNe } = useMemo(() => {
    const geo = feature(mundo, mundo.objects.countries).features.filter((f) => f.properties.name !== 'Antarctica');
    const proy = geoNaturalEarth1().fitSize([ANCHO, ALTO], { type: 'FeatureCollection', features: geo });
    const ruta = geoPath(proy);
    const agg = {};
    for (const p of paises || []) {
      const ne = ALIAS[p.pais] || p.pais;
      const n = modo === 'liga' ? p.liga : p.nac;
      if (!agg[ne]) agg[ne] = { n: 0, tm: [] };
      agg[ne].n += n;
      if (n > 0) agg[ne].tm.push(p.pais);
    }
    return { formas: geo.map((f) => ({ nombre: f.properties.name, d: ruta(f), id: f.id })), porNe: agg };
  }, [paises, modo]);

  const mover = (e, info) => {
    const r = caja.current.getBoundingClientRect();
    setTip({ x: e.clientX - r.left + 14, y: e.clientY - r.top + 14, ...info });
  };

  return (
    <div className="mapa-caja" ref={caja} onMouseLeave={() => setTip(null)}>
      <svg viewBox={`0 0 ${ANCHO} ${ALTO}`} role="group" aria-label={t('exploraPais')}>
        {formas.map((f) => {
          const a = porNe[f.nombre];
          const n = a ? a.n : 0;
          const etiqueta = a && a.tm.length ? a.tm.map((x) => paisTxt(x, idioma)).join(', ') : f.nombre;
          const activo = n > 0;
          return (
            <path key={f.id || f.nombre} d={f.d} style={{ fill: tono(n) }} className={activo ? 'activo' : ''}
              tabIndex={activo ? 0 : -1} role={activo ? 'link' : undefined}
              aria-label={activo ? `${etiqueta}: ${t('jugadoresN', { n: miles(n) })}` : undefined}
              onMouseMove={activo ? (e) => mover(e, { etiqueta, n }) : undefined}
              onClick={activo ? () => alElegir(a.tm) : undefined}
              onKeyDown={activo ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); alElegir(a.tm); } } : undefined} />
          );
        })}
      </svg>
      {tip && (
        <div className="mapa-tip" style={{ left: Math.min(tip.x, (caja.current?.clientWidth || 600) - 200), top: tip.y }}>
          <strong>{tip.etiqueta}</strong>
          {t('jugadoresN', { n: miles(tip.n) })}<br /><span>{t('abrirRadarFlecha')}</span>
        </div>
      )}
    </div>
  );
}
