import { useIdioma } from '../i18n.jsx';

export default function Pie() {
  const { t } = useIdioma();
  return (
    <footer className="pie-sitio">
      <div className="contenedor">
        <span>{t('pieFuentes')}</span>
        <span>{t('pieProyecto')}</span>
      </div>
    </footer>
  );
}
