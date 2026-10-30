import { Link } from 'react-router-dom';
import { useIdioma } from '../i18n.jsx';

const TEXTO = { equipos: 'prontoEquipos', simulador: 'prontoSimulador', metodologia: 'prontoMetodologia', noEncontrado: 'prontoNoEncontrado' };
const TITULO = { equipos: 'equipos', simulador: 'simulador', metodologia: 'metodologia', noEncontrado: 'pronto' };

export default function Proximamente({ modulo }) {
  const { t } = useIdioma();
  return (
    <main className="contenedor">
      <div className="tarjeta" style={{ padding: 40, maxWidth: 720 }}>
        {modulo !== 'noEncontrado' && <p className="sobretitulo">{t('pronto')}</p>}
        <h1 className="titulo">{t(TITULO[modulo])}</h1>
        <p className="subtitulo">{t(TEXTO[modulo])}</p>
        <Link to="/" className="boton" style={{ marginTop: 24 }}>{t('volverInicio')}</Link>
      </div>
    </main>
  );
}
