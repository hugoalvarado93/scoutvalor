import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useIdioma } from '../i18n.jsx';
import { cargar, cargarJugadores, dinero, mesAnio, miles, paisTxt, posTxt, POSICIONES, PAISES_ES } from '../datos.js';
import { Escudo, Foto, LogoLiga } from '../components/Insignias.jsx';

const RAPIDAS = ['MEX1', 'ARG1', 'BRA1', 'GB1', 'ES1', 'MLS1'];
const CONFS = ['CONCACAF', 'CONMEBOL', 'UEFA', 'CAF', 'AFC'];
const POR_PAGINA = 50;

function lista(v) { return v ? v.split(',').filter(Boolean) : []; }
function normalizar(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim(); }

export default function Radar() {
  const { t, idioma } = useIdioma();
  const [params, setParams] = useSearchParams();
  const [jug, setJug] = useState(null);
  const [clubes, setClubes] = useState({});
  const [ligas, setLigas] = useState([]);
  const [paisesTxt, setPaisesTxt] = useState(params.get('paises') || '');

  useEffect(() => {
    cargarJugadores().then(setJug);
    cargar('clubes.json').then(setClubes);
    cargar('ligas.json').then(setLigas);
  }, []);

  const p = Object.fromEntries(params.entries());
  const modo = p.modo || 'radar';
  const liga = p.liga || '';
  const pos = lista(p.pos);
  const conf = lista(p.conf);
  const nac = lista(p.nac);
  const paisLiga = lista(p.paisLiga);
  const orden = p.orden || (modo === 'radar' ? 'brecha' : 'valor');
  const pag = Number(p.pag || 1);

  const cambiar = (cambios) => {
    const n = new URLSearchParams(params);
    Object.entries(cambios).forEach(([k, v]) => {
      if (v === '' || v === null || v === undefined || (Array.isArray(v) && !v.length)) n.delete(k);
      else n.set(k, Array.isArray(v) ? v.join(',') : String(v));
    });
    if (!('pag' in cambios)) n.delete('pag');
    setParams(n, { replace: true });
  };
  const alternar = (clave, arr, valor) => cambiar({ [clave]: arr.includes(valor) ? arr.filter((x) => x !== valor) : [...arr, valor] });

  useEffect(() => {
    const id = setTimeout(() => { if ((params.get('paises') || '') !== paisesTxt) cambiar({ paises: paisesTxt }); }, 350);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paisesTxt]);

  const ligaPorId = useMemo(() => Object.fromEntries(ligas.map((l) => [l.id, l])), [ligas]);

  const filtrados = useMemo(() => {
    if (!jug) return [];
    const posSet = new Set(POSICIONES.filter((x) => pos.includes(x.id)).flatMap((x) => x.incluye));
    const nacSet = new Set(nac);
    const textoPaises = lista(p.paises).map(normalizar).filter(Boolean);
    const emin = p.emin ? Number(p.emin) : null;
    const emax = p.emax ? Number(p.emax) : null;
    const vmax = p.vmax ? Number(p.vmax) : null;
    let r = jug.filter((j) => {
      if (modo === 'radar' && !(j.r && j.b !== null)) return false;
      if (liga && j.lg !== liga) return false;
      if (paisLiga.length && !(ligaPorId[j.lg] && paisLiga.includes(ligaPorId[j.lg].pais))) return false;
      if (posSet.size && !posSet.has(j.p)) return false;
      if (nacSet.size && !nacSet.has(j.nac)) return false;
      if (conf.length) {
        const otras = conf.includes('Otras');
        if (!(conf.includes(j.cf) || (otras && !CONFS.includes(j.cf)))) return false;
      }
      if (textoPaises.length) {
        const a = normalizar(j.nac); const b = normalizar(PAISES_ES[j.nac] || '');
        if (!textoPaises.some((x) => a.startsWith(x) || b.startsWith(x))) return false;
      }
      if (emin !== null && !(j.e >= emin)) return false;
      if (emax !== null && !(j.e < emax + 1)) return false;
      if (vmax !== null && !(j.v !== null && j.v <= vmax)) return false;
      if (p.contrato && !(j.ct && j.ct < p.contrato)) return false;
      if (p.pie && j.pie !== p.pie) return false;
      return true;
    });
    const clave = {
      brecha: (j) => -(j.b ?? -9999), valor: (j) => -(j.v ?? -1), estimado: (j) => -(j.ve ?? -1),
      edad: (j) => j.e ?? 99, minutos: (j) => -(j.min ?? -1),
    }[orden] || ((j) => -(j.b ?? -9999));
    r = r.slice().sort((a, b) => clave(a) - clave(b));
    return r;
  }, [jug, modo, liga, p.paises, p.emin, p.emax, p.vmax, p.contrato, p.pie, orden, params, ligaPorId]); // eslint-disable-line react-hooks/exhaustive-deps

  const total = filtrados.length;
  const paginas = Math.max(1, Math.ceil(total / POR_PAGINA));
  const pagina = Math.min(pag, paginas);
  const filas = filtrados.slice((pagina - 1) * POR_PAGINA, pagina * POR_PAGINA);

  const chips = [];
  if (liga) chips.push({ k: 'liga', txt: ligaPorId[liga]?.nombre || liga, quitar: { liga: '' } });
  paisLiga.forEach((x) => chips.push({ k: `pl-${x}`, txt: `${t('ligaDelPais')}: ${paisTxt(x, idioma)}`, quitar: { paisLiga: paisLiga.filter((y) => y !== x) } }));
  nac.forEach((x) => chips.push({ k: `n-${x}`, txt: paisTxt(x, idioma), quitar: { nac: nac.filter((y) => y !== x) } }));
  if (p.emin || p.emax) chips.push({ k: 'edad', txt: `${t('edad')} ${p.emin || '–'}–${p.emax || '–'}`, quitar: { emin: '', emax: '' } });
  pos.forEach((x) => chips.push({ k: `p-${x}`, txt: posTxt(x, idioma), quitar: { pos: pos.filter((y) => y !== x) } }));
  conf.forEach((x) => chips.push({ k: `c-${x}`, txt: x === 'Otras' ? t('otras') : x, quitar: { conf: conf.filter((y) => y !== x) } }));
  if (p.vmax) chips.push({ k: 'vmax', txt: `≤ ${dinero(Number(p.vmax))}`, quitar: { vmax: '' } });
  if (p.contrato) chips.push({ k: 'ct', txt: `${t('contrato')} < ${mesAnio(p.contrato, idioma)}`, quitar: { contrato: '' } });
  if (p.pie) chips.push({ k: 'pie', txt: t(p.pie === 'right' ? 'derecho' : p.pie === 'left' ? 'izquierdo' : 'ambos'), quitar: { pie: '' } });
  if (p.paises) chips.push({ k: 'paises', txt: p.paises, quitar: { paises: '' } });

  const ligasOrdenadas = ligas.filter((l) => l.jugadores > 0);

  return (
    <main className="contenedor">
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16 }}>
        <div>
          <p className="sobretitulo">{t('moduloA')}</p>
          <h1 className="titulo">{t('radarTitulo')}</h1>
          <p className="subtitulo">{t('radarTxt')}</p>
        </div>
        <div className="alternador" role="group">
          <button type="button" aria-pressed={modo === 'radar'} onClick={() => cambiar({ modo: '', orden: '' })}>{t('modoRadar')}</button>
          <button type="button" aria-pressed={modo === 'todos'} onClick={() => cambiar({ modo: 'todos', orden: '' })}>{t('modoTodos')}</button>
        </div>
      </div>

      <div className="pestanas" role="tablist" aria-label={t('ligas')} style={{ marginTop: 24 }}>
        <button type="button" role="tab" className="pestana sin-logo" aria-selected={!liga} onClick={() => cambiar({ liga: '' })}>{t('todasLigas')}</button>
        {RAPIDAS.map((id) => ligaPorId[id] && (
          <button key={id} type="button" role="tab" className="pestana" aria-selected={liga === id} onClick={() => cambiar({ liga: id })}>
            <LogoLiga liga={ligaPorId[id]} tam={28} claro={liga === id} />{ligaPorId[id].nombre}
          </button>
        ))}
        <label className="campo" style={{ flexDirection: 'row', alignItems: 'center' }}>
          <span className="solo-lector">{t('otraLiga')}</span>
          <select value={RAPIDAS.includes(liga) ? '' : liga} onChange={(e) => cambiar({ liga: e.target.value })} style={{ borderRadius: 999, height: 40 }}>
            <option value="">{t('otraLiga')}</option>
            {ligasOrdenadas.map((l) => <option key={l.id} value={l.id}>{l.nombre} · {paisTxt(l.pais, idioma)}</option>)}
          </select>
        </label>
      </div>

      <div className="fila-flex" style={{ marginTop: 24 }}>
        <aside className="tarjeta lateral" aria-label={t('buscador')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 className="tarjeta-t">{t('buscador')}</h2>
            <button type="button" className="boton-texto" onClick={() => { setPaisesTxt(''); setParams(modo === 'todos' ? { modo: 'todos' } : {}, { replace: true }); }}>{t('limpiar')}</button>
          </div>

          <fieldset style={{ border: 0, margin: 0, padding: 0 }}>
            <legend style={{ fontSize: 13, fontWeight: 600, color: 'var(--tenue)', marginBottom: 8 }}>{t('edad')}</legend>
            <div style={{ display: 'flex', gap: 8 }}>
              <label className="campo" style={{ flex: 1, fontSize: 12, fontWeight: 400 }}>{t('minima')}
                <input type="number" min="15" max="45" value={p.emin || ''} onChange={(e) => cambiar({ emin: e.target.value })} />
              </label>
              <label className="campo" style={{ flex: 1, fontSize: 12, fontWeight: 400 }}>{t('maxima')}
                <input type="number" min="15" max="45" value={p.emax || ''} onChange={(e) => cambiar({ emax: e.target.value })} />
              </label>
            </div>
          </fieldset>

          <fieldset style={{ border: 0, margin: 0, padding: 0 }}>
            <legend style={{ fontSize: 13, fontWeight: 600, color: 'var(--tenue)', marginBottom: 8 }}>{t('posicion')}</legend>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {POSICIONES.map((x) => (
                <button key={x.id} type="button" className="chip" aria-pressed={pos.includes(x.id)} onClick={() => alternar('pos', pos, x.id)}>{posTxt(x.id, idioma)}</button>
              ))}
            </div>
          </fieldset>

          <fieldset style={{ border: 0, margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <legend style={{ fontSize: 13, fontWeight: 600, color: 'var(--tenue)', marginBottom: 8 }}>{t('nacionalidad')}</legend>
            {[...CONFS, 'Otras'].map((c) => (
              <label key={c} className="casilla"><input type="checkbox" checked={conf.includes(c)} onChange={() => alternar('conf', conf, c)} />{c === 'Otras' ? t('otras') : c}</label>
            ))}
            <label className="campo" style={{ fontSize: 12, fontWeight: 400, marginTop: 6 }}>{t('paisesEsp')}
              <input type="text" placeholder={t('paisesPh')} value={paisesTxt} onChange={(e) => setPaisesTxt(e.target.value)} />
            </label>
          </fieldset>

          <label className="campo">{t('contratoAntes')}
            <select value={p.contrato || ''} onChange={(e) => cambiar({ contrato: e.target.value })}>
              <option value="">{t('cualquierFecha')}</option>
              {['2027-01', '2027-07', '2028-01', '2028-07'].map((c) => <option key={c} value={c}>{mesAnio(c, idioma)}</option>)}
            </select>
          </label>

          <label className="campo">{t('valorMax')}
            <select value={p.vmax || ''} onChange={(e) => cambiar({ vmax: e.target.value })}>
              <option value="">{t('sinLimite')}</option>
              {[500000, 1000000, 2000000, 5000000, 10000000, 20000000, 50000000].map((v) => <option key={v} value={v}>{dinero(v)}</option>)}
            </select>
          </label>

          <label className="campo">{t('pie')}
            <select value={p.pie || ''} onChange={(e) => cambiar({ pie: e.target.value })}>
              <option value="">{t('cualquiera')}</option>
              <option value="right">{t('derecho')}</option>
              <option value="left">{t('izquierdo')}</option>
              <option value="both">{t('ambos')}</option>
            </select>
          </label>
        </aside>

        <section className="principal" aria-label="Resultados">
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
            <p style={{ margin: 0, fontSize: 15 }} aria-live="polite">
              {jug ? <><strong style={{ fontFamily: 'var(--display)', fontSize: 22 }}>{miles(total)}</strong> {t('coinciden', { n: '' }).trim()}</> : t('cargando')}
            </p>
            <label className="campo" style={{ flexDirection: 'row', alignItems: 'center', gap: 8, fontWeight: 400 }}>{t('ordenar')}
              <select value={orden} onChange={(e) => cambiar({ orden: e.target.value })}>
                <option value="brecha">{t('ordBrecha')}</option>
                <option value="valor">{t('ordValor')}</option>
                <option value="estimado">{t('ordEstimado')}</option>
                <option value="edad">{t('ordEdad')}</option>
                <option value="minutos">{t('ordMinutos')}</option>
              </select>
            </label>
          </div>

          {chips.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {chips.map((c) => (
                <span key={c.k} className="chip-filtro">{c.txt}<button type="button" aria-label={`${t('quitarFiltro')}: ${c.txt}`} onClick={() => cambiar(c.quitar)}>×</button></span>
              ))}
            </div>
          )}

          <div className="tarjeta tabla-caja">
            {!jug ? <div className="cargando">{t('cargando')}</div> : total === 0 ? <div className="cargando">{t('sinResultados')}</div> : (
              <table className="tabla" style={{ minWidth: 900 }}>
                <thead>
                  <tr>
                    <th scope="col">#</th>
                    <th scope="col">{t('jugador')}</th>
                    <th scope="col">{t('pos')}</th>
                    <th scope="col" className="der">{t('edad')}</th>
                    <th scope="col">{t('nac')}</th>
                    <th scope="col">{t('contrato')}</th>
                    <th scope="col" className="der">{t('valorMercado')}</th>
                    <th scope="col" className="der">{t('valorEstimado')}</th>
                    <th scope="col">{t('brecha')}</th>
                  </tr>
                </thead>
                <tbody>
                  {filas.map((j, i) => {
                    const club = clubes[j.cl];
                    const lg = ligaPorId[j.lg];
                    const b = j.b;
                    const ancho = b === null ? 0 : Math.min(100, Math.abs(b) / 2);
                    return (
                      <tr key={j.id}>
                        <td style={{ color: 'var(--tenue)' }}>{(pagina - 1) * POR_PAGINA + i + 1}</td>
                        <td>
                          <div className="jugador-celda">
                            <Foto af={j.af} tam={36} />
                            <div>
                              <Link to={`/jugador/${j.id}`}>{j.n}</Link>
                              <small><Escudo club={club} tam={18} />{club ? club.n : '—'}{lg && !liga ? <><LogoLiga liga={lg} tam={16} /></> : null}</small>
                            </div>
                          </div>
                        </td>
                        <td><span className="etiqueta">{posTxt(j.p, idioma)}</span></td>
                        <td className="der">{j.e ? Math.floor(j.e) : '—'}</td>
                        <td>{paisTxt(j.nac, idioma)}</td>
                        <td>{j.ct ? mesAnio(j.ct, idioma) : <span className="sin-dato">{t('sinDato')}</span>}</td>
                        <td className="der">{dinero(j.v)}</td>
                        <td className="der" style={{ fontWeight: 600 }}>{j.ve ? dinero(j.ve) : <span className="sin-dato">—</span>}</td>
                        <td>
                          {b === null ? <span className="sin-dato">—</span> : (
                            <div className="brecha">
                              <div className="barra"><div style={{ width: `${ancho}%`, background: b >= 0 ? 'var(--marca)' : 'var(--naranja)' }} /></div>
                              <span style={{ color: b >= 0 ? 'var(--marca)' : 'var(--naranja-osc)' }}>{b >= 0 ? '+' : '−'}{Math.abs(b)}%</span>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
            {jug && total > POR_PAGINA && (
              <div className="paginacion">
                <span>{t('pagina', { p: pagina, t: paginas })}</span>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button type="button" className="boton secundario" disabled={pagina <= 1} onClick={() => cambiar({ pag: pagina - 1 })}>{t('anterior')}</button>
                  <button type="button" className="boton secundario" disabled={pagina >= paginas} onClick={() => cambiar({ pag: pagina + 1 })}>{t('siguiente')}</button>
                </div>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
            <div className="tarjeta relleno" style={{ flex: '2 1 420px' }}>
              <h3 className="tarjeta-t" style={{ fontSize: 16, margin: '0 0 6px' }}>{t('comoLeer')}</h3>
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.55, color: 'var(--tenue)' }}>{t('comoLeerTxt')}</p>
              <p className="nota" style={{ margin: '8px 0 0' }}>{t('soloConMinutos')}</p>
            </div>
            <div className="tarjeta relleno" style={{ flex: '1 1 260px' }}>
              <h3 className="tarjeta-t" style={{ fontSize: 16, margin: '0 0 10px' }}>{t('fuentes')}</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <span className="etiqueta" style={{ background: 'var(--superficie)', border: '1px solid var(--linea)' }}>Transfermarkt</span>
                <span className="etiqueta" style={{ background: 'var(--superficie)', border: '1px solid var(--linea)' }}>API-Football</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
