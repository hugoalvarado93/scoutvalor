// Graficas SVG ligeras para la pagina de Metodologia.
// Colores por rol (tokens CSS validados para tema claro y oscuro): --g-pos, --g-neg, --g-neutro, --g-ref.
// Cada grafica trae etiquetas directas, tooltip nativo (<title>) y una tabla de datos plegable.
import { useIdioma } from '../i18n.jsx';

function TablaDatos({ columnas, filas }) {
  const { t } = useIdioma();
  return (
    <details className="ver-datos">
      <summary>{t('verDatos')}</summary>
      <div className="tabla-caja">
        <table className="tabla" style={{ fontSize: 13 }}>
          <thead><tr>{columnas.map((c) => <th key={c} scope="col">{c}</th>)}</tr></thead>
          <tbody>{filas.map((f, i) => <tr key={i}>{f.map((v, j) => <td key={j}>{v}</td>)}</tr>)}</tbody>
        </table>
      </div>
    </details>
  );
}

// Barras horizontales de una sola serie (magnitud), etiqueta de valor al final de cada barra.
export function BarrasH({ datos, formato = (v) => v, max, etiquetaValor = 'Valor', etiquetaCat = '', ancho = 640, alto: altoBarra = 22, colorDe }) {
  const m = max ?? Math.max(...datos.map((d) => d[1]), 0.0001);
  const iz = 168, de = 64, sep = 8;
  const H = datos.length * (altoBarra + sep) + 8;
  const w = ancho - iz - de;
  return (
    <figure className="grafica">
      <svg viewBox={`0 0 ${ancho} ${H}`} role="img" aria-label={datos.map((d) => `${d[0]}: ${formato(d[1])}`).join('; ')}>
        {datos.map(([k, v], i) => {
          const y = 4 + i * (altoBarra + sep);
          const bw = Math.max(2, (Math.max(0, v) / m) * w);
          return (
            <g key={k}>
              <title>{`${k}: ${formato(v)}`}</title>
              <text x={iz - 10} y={y + altoBarra / 2 + 4} textAnchor="end" className="g-txt">{k}</text>
              <rect x={iz} y={y} width={w} height={altoBarra} rx="4" className="g-pista" />
              <rect x={iz} y={y} width={bw} height={altoBarra} rx="4" style={{ fill: colorDe ? colorDe(k, v) : 'var(--g-pos)' }} />
              <text x={iz + bw + 8} y={y + altoBarra / 2 + 4} className="g-txt g-fuerte">{formato(v)}</text>
            </g>
          );
        })}
      </svg>
      <TablaDatos columnas={[etiquetaCat, etiquetaValor]} filas={datos.map(([k, v]) => [k, formato(v)])} />
    </figure>
  );
}

// Barras divergentes alrededor de cero (polaridad): verde a la derecha, naranja a la izquierda, signo explicito.
export function Divergente({ datos, formato = (v) => v.toFixed(2), etiquetaCat = '', etiquetaValor = '' }) {
  const ancho = 680, iz = 230, de = 24, alto = 20, sep = 8;
  const m = Math.max(...datos.map((d) => Math.abs(d[1])), 0.0001);
  const H = datos.length * (alto + sep) + 8;
  const mitad = iz + (ancho - iz - de) / 2;
  const media = (ancho - iz - de) / 2 - 44;
  return (
    <figure className="grafica">
      <svg viewBox={`0 0 ${ancho} ${H}`} role="img" aria-label={datos.map((d) => `${d[0]}: ${formato(d[1])}`).join('; ')}>
        <line x1={mitad} x2={mitad} y1="0" y2={H} className="g-eje" />
        {datos.map(([k, v], i) => {
          const y = 4 + i * (alto + sep);
          const bw = Math.max(2, (Math.abs(v) / m) * media);
          const pos = v >= 0;
          return (
            <g key={k}>
              <title>{`${k}: ${v >= 0 ? '+' : '−'}${formato(Math.abs(v))}`}</title>
              <text x={iz - 10} y={y + alto / 2 + 4} textAnchor="end" className="g-txt">{k}</text>
              <rect x={pos ? mitad + 1 : mitad - 1 - bw} y={y} width={bw} height={alto} rx="4" style={{ fill: pos ? 'var(--g-pos)' : 'var(--g-neg)' }} />
              <text x={pos ? mitad + bw + 8 : mitad - bw - 8} y={y + alto / 2 + 4} textAnchor={pos ? 'start' : 'end'} className="g-txt g-fuerte">
                {v >= 0 ? '+' : '−'}{formato(Math.abs(v))}
              </text>
            </g>
          );
        })}
      </svg>
      <TablaDatos columnas={[etiquetaCat, etiquetaValor]} filas={datos.map(([k, v]) => [k, `${v >= 0 ? '+' : '−'}${formato(Math.abs(v))}`])} />
    </figure>
  );
}

// Dispersion valor real vs estimado (escala logaritmica en euros) con la diagonal de acierto perfecto.
export function Dispersion({ puntos, etiquetaX, etiquetaY }) {
  const { t } = useIdioma();
  const W = 520, H = 440, iz = 64, ab = 48, ar = 14, de = 16;
  const lo = Math.log(1e5), hi = Math.log(2e8);
  const sx = (v) => iz + ((v - lo) / (hi - lo)) * (W - iz - de);
  const sy = (v) => H - ab - ((v - lo) / (hi - lo)) * (H - ab - ar);
  const marcas = [1e5, 1e6, 1e7, 1e8];
  const fmt = (v) => (v >= 1e6 ? `€${v / 1e6}M` : `€${v / 1e3}K`);
  const dentro = puntos.filter(([a, b]) => a >= lo && a <= hi && b >= lo && b <= hi);
  return (
    <figure className="grafica">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${etiquetaX} vs ${etiquetaY}: ${dentro.length} ${t('jugadoresMuestra')}`}>
        {marcas.map((m) => (
          <g key={m}>
            <line x1={sx(Math.log(m))} x2={sx(Math.log(m))} y1={ar} y2={H - ab} className="g-rejilla" />
            <line x1={iz} x2={W - de} y1={sy(Math.log(m))} y2={sy(Math.log(m))} className="g-rejilla" />
            <text x={sx(Math.log(m))} y={H - ab + 18} textAnchor="middle" className="g-txt">{fmt(m)}</text>
            <text x={iz - 8} y={sy(Math.log(m)) + 4} textAnchor="end" className="g-txt">{fmt(m)}</text>
          </g>
        ))}
        <line x1={sx(lo)} y1={sy(lo)} x2={sx(hi)} y2={sy(hi)} className="g-diagonal" />
        <text x={sx(Math.log(9e7))} y={sy(Math.log(9e7)) - 10} textAnchor="end" className="g-txt">{t('aciertoPerfecto')}</text>
        {dentro.map(([a, b], i) => (
          <circle key={i} cx={sx(a)} cy={sy(b)} r="4" className="g-punto"><title>{`${fmt(Math.round(Math.exp(a)))} → ${fmt(Math.round(Math.exp(b)))}`}</title></circle>
        ))}
        <text x={(iz + W - de) / 2} y={H - 8} textAnchor="middle" className="g-txt g-fuerte">{etiquetaX}</text>
        <text x={14} y={(ar + H - ab) / 2} textAnchor="middle" transform={`rotate(-90 14 ${(ar + H - ab) / 2})`} className="g-txt g-fuerte">{etiquetaY}</text>
      </svg>
      <figcaption className="nota">{t('dispersionNota', { n: dentro.length })}</figcaption>
    </figure>
  );
}

// Calibracion: probabilidad media predicha (anillo) vs tasa real (punto) por decil.
export function Calibracion({ datos }) {
  const { t } = useIdioma();
  const W = 640, H = 300, iz = 52, ab = 44, ar = 16, de = 16;
  const max = Math.min(1, Math.ceil(Math.max(...datos.flatMap((d) => [d[0], d[1]])) * 10) / 10 + 0.05);
  const paso = (W - iz - de) / datos.length;
  const sx = (i) => iz + paso * i + paso / 2;
  const sy = (v) => H - ab - (v / max) * (H - ab - ar);
  const marcas = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6].filter((m) => m <= max);
  return (
    <figure className="grafica">
      <div className="leyenda-g">
        <span><i className="mk-anillo" />{t('predicho')}</span>
        <span><i className="mk-punto" />{t('real')}</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={datos.map((d, i) => `${t('decil')} ${i + 1}: ${Math.round(d[0] * 100)}% / ${Math.round(d[1] * 100)}%`).join('; ')}>
        {marcas.map((m) => (
          <g key={m}>
            <line x1={iz} x2={W - de} y1={sy(m)} y2={sy(m)} className="g-rejilla" />
            <text x={iz - 8} y={sy(m) + 4} textAnchor="end" className="g-txt">{Math.round(m * 100)}%</text>
          </g>
        ))}
        {datos.map(([p, r, n], i) => (
          <g key={i}>
            <title>{`${t('decil')} ${i + 1}: ${t('predicho')} ${(p * 100).toFixed(1)}% · ${t('real')} ${(r * 100).toFixed(1)}% · n=${n}`}</title>
            <line x1={sx(i)} x2={sx(i)} y1={sy(p)} y2={sy(r)} className="g-union" />
            <circle cx={sx(i)} cy={sy(p)} r="6" className="g-anillo" />
            <circle cx={sx(i)} cy={sy(r)} r="5" className="g-lleno" />
            <text x={sx(i)} y={H - ab + 18} textAnchor="middle" className="g-txt">{i + 1}</text>
          </g>
        ))}
        <text x={(iz + W - de) / 2} y={H - 6} textAnchor="middle" className="g-txt g-fuerte">{t('decilRiesgo')}</text>
      </svg>
      <TablaDatos columnas={[t('decil'), t('predicho'), t('real'), 'n']}
        filas={datos.map(([p, r, n], i) => [i + 1, `${(p * 100).toFixed(1)}%`, `${(r * 100).toFixed(1)}%`, n.toLocaleString('en-US')])} />
    </figure>
  );
}

// Barra apilada de proporciones (pesos de un puntaje): separacion de 2 px y etiqueta con % debajo de cada parte.
export function Proporciones({ partes }) {
  const total = partes.reduce((a, p) => a + p.v, 0) || 1;
  return (
    <div className="proporciones" role="img" aria-label={partes.map((p) => `${p.k}: ${Math.round((p.v / total) * 100)}%`).join('; ')}>
      <div className="prop-barra">
        {partes.map((p) => <div key={p.k} style={{ flex: p.v, background: p.color }} title={`${p.k}: ${Math.round((p.v / total) * 100)}%`} />)}
      </div>
      <div className="prop-etiquetas">
        {partes.map((p) => <span key={p.k} style={{ flex: p.v }}><strong>{Math.round((p.v / total) * 100)}%</strong>{p.k}</span>)}
      </div>
    </div>
  );
}
