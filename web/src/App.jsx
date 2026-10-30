import { Routes, Route, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import Encabezado from './components/Encabezado.jsx';
import Pie from './components/Pie.jsx';
import Inicio from './pages/Inicio.jsx';
import Radar from './pages/Radar.jsx';
import Jugador from './pages/Jugador.jsx';
import Proximamente from './pages/Proximamente.jsx';
import Equipos from './pages/Equipos.jsx';
import Simulador from './pages/Simulador.jsx';

function AlInicio() {
  const { pathname } = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  return null;
}

export default function App() {
  return (
    <div className="app">
      <AlInicio />
      <Encabezado />
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/radar" element={<Radar />} />
        <Route path="/jugador/:id" element={<Jugador />} />
        <Route path="/equipos" element={<Equipos />} />
        <Route path="/simulador" element={<Simulador />} />
        <Route path="/metodologia" element={<Proximamente modulo="metodologia" />} />
        <Route path="*" element={<Proximamente modulo="noEncontrado" />} />
      </Routes>
      <Pie />
    </div>
  );
}
