// Carga y cache de los JSON estaticos generados por el pipeline (web/public/data).
const cache = {};

export function cargar(nombre) {
  if (!cache[nombre]) {
    cache[nombre] = fetch(`/data/${nombre}`).then((r) => {
      if (!r.ok) throw new Error(`No se pudo cargar ${nombre}`);
      return r.json();
    });
  }
  return cache[nombre];
}

let jugadoresCache = null;
// jugadores.json viene en formato columnar; aqui se convierte a filas una sola vez.
export function cargarJugadores() {
  if (!jugadoresCache) {
    jugadoresCache = cargar('jugadores.json').then((c) => {
      const n = c.id.length;
      const filas = new Array(n);
      const claves = Object.keys(c);
      for (let i = 0; i < n; i++) {
        const f = {};
        for (const k of claves) f[k] = c[k][i];
        filas[i] = f;
      }
      return filas;
    });
  }
  return jugadoresCache;
}

export function cargarDetalle(id) {
  return cargar(`j/${Number(id) % 256}.json`).then((frag) => frag[String(id)] || {});
}

// ---------- formato
export function dinero(v) {
  if (v === null || v === undefined) return '—';
  if (v >= 1e6) return `€${(v / 1e6).toFixed(v >= 1e8 ? 0 : 1)}M`;
  if (v >= 1e3) return `€${Math.round(v / 1e3)}K`;
  return `€${v}`;
}

const MESES = {
  es: ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'],
  en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
};
export function mesAnio(ym, idioma = 'es') {
  if (!ym) return null;
  const [a, m] = ym.split('-');
  return `${MESES[idioma][Number(m) - 1]} ${a}`;
}
export function fecha(iso, idioma = 'es') {
  if (!iso) return '';
  const [a, m, d] = iso.split('-');
  return idioma === 'es' ? `${Number(d)} ${MESES.es[Number(m) - 1]} ${a}` : `${MESES.en[Number(m) - 1]} ${Number(d)}, ${a}`;
}
export function miles(n) {
  if (n === null || n === undefined) return '—';
  return Number(n).toLocaleString('en-US');
}

// ---------- posiciones
export const POSICIONES = [
  { id: 'POR', incluye: ['POR'] },
  { id: 'DFC', incluye: ['DFC'] },
  { id: 'LAT', incluye: ['LI', 'LD'] },
  { id: 'MCD', incluye: ['MCD'] },
  { id: 'MC', incluye: ['MC'] },
  { id: 'MCO', incluye: ['MCO'] },
  { id: 'MI/MD', incluye: ['MI', 'MD'] },
  { id: 'EXT', incluye: ['EI', 'ED'] },
  { id: 'DC', incluye: ['DC', 'SD'] },
];
export const POS_EN = { POR: 'GK', DFC: 'CB', LI: 'LB', LD: 'RB', LAT: 'FB', MCD: 'DM', MC: 'CM', MCO: 'AM', MI: 'LM', MD: 'RM', 'MI/MD': 'WM', EI: 'LW', ED: 'RW', EXT: 'W', SD: 'SS', DC: 'CF' };
export function posTxt(p, idioma) {
  if (!p) return '—';
  return idioma === 'en' ? POS_EN[p] || p : p;
}

// ---------- paises (nombres de Transfermarkt)
export const PAISES_ES = {
  Argentina: 'Argentina', Brazil: 'Brasil', Spain: 'España', Japan: 'Japón', Colombia: 'Colombia', France: 'Francia',
  Serbia: 'Serbia', Ukraine: 'Ucrania', Netherlands: 'Países Bajos', Mexico: 'México', 'Türkiye': 'Turquía',
  England: 'Inglaterra', 'United States': 'Estados Unidos', 'Korea, South': 'Corea del Sur', Germany: 'Alemania',
  Romania: 'Rumania', Sweden: 'Suecia', 'Czech Republic': 'Chequia', Portugal: 'Portugal', Denmark: 'Dinamarca',
  Norway: 'Noruega', Poland: 'Polonia', 'Saudi Arabia': 'Arabia Saudita', Croatia: 'Croacia', Russia: 'Rusia',
  Italy: 'Italia', Belgium: 'Bélgica', Australia: 'Australia', Greece: 'Grecia', Switzerland: 'Suiza', Austria: 'Austria',
  Nigeria: 'Nigeria', Scotland: 'Escocia', Uruguay: 'Uruguay', Morocco: 'Marruecos', Senegal: 'Senegal', Ghana: 'Ghana',
  "Cote d'Ivoire": 'Costa de Marfil', 'Bosnia-Herzegovina': 'Bosnia y Herzegovina', Algeria: 'Argelia', Slovakia: 'Eslovaquia',
  Canada: 'Canadá', 'New Zealand': 'Nueva Zelanda', Chile: 'Chile', Venezuela: 'Venezuela', Slovenia: 'Eslovenia',
  'South Africa': 'Sudáfrica', 'DR Congo': 'RD del Congo', Paraguay: 'Paraguay', Kosovo: 'Kosovo', Jamaica: 'Jamaica',
  Peru: 'Perú', Cameroon: 'Camerún', Albania: 'Albania', Ireland: 'Irlanda', Tunisia: 'Túnez', Mali: 'Malí',
  Ecuador: 'Ecuador', Georgia: 'Georgia', Montenegro: 'Montenegro', Wales: 'Gales', 'Northern Ireland': 'Irlanda del Norte',
  Iceland: 'Islandia', Finland: 'Finlandia', Hungary: 'Hungría', Bulgaria: 'Bulgaria', Egypt: 'Egipto', Iran: 'Irán',
  China: 'China', Honduras: 'Honduras', 'Costa Rica': 'Costa Rica', Panama: 'Panamá', 'El Salvador': 'El Salvador',
  Guatemala: 'Guatemala', Bolivia: 'Bolivia', Haiti: 'Haití', 'Cape Verde': 'Cabo Verde', Guinea: 'Guinea',
  'North Macedonia': 'Macedonia del Norte', Armenia: 'Armenia', Israel: 'Israel', Lithuania: 'Lituania', Latvia: 'Letonia',
  Estonia: 'Estonia', Belarus: 'Bielorrusia', Moldova: 'Moldavia', Luxembourg: 'Luxemburgo', Cyprus: 'Chipre',
  Qatar: 'Catar', Iraq: 'Irak', Uzbekistan: 'Uzbekistán', Kazakhstan: 'Kazajistán', Angola: 'Angola', Gabon: 'Gabón',
  Gambia: 'Gambia', 'Burkina Faso': 'Burkina Faso', Benin: 'Benín', Togo: 'Togo', Zambia: 'Zambia', Zimbabwe: 'Zimbabue',
  Kenya: 'Kenia', Congo: 'Congo', 'Equatorial Guinea': 'Guinea Ecuatorial', 'Guinea-Bissau': 'Guinea-Bisáu',
  'Dominican Republic': 'República Dominicana', Cuba: 'Cuba', Curacao: 'Curazao', Suriname: 'Surinam',
  Azerbaijan: 'Azerbaiyán', Thailand: 'Tailandia', Indonesia: 'Indonesia', Philippines: 'Filipinas', 'Korea, North': 'Corea del Norte',
};
export function paisTxt(p, idioma) {
  if (!p) return '—';
  return idioma === 'es' ? PAISES_ES[p] || p : p;
}

// URLs de medios de API-Football (escudos, logos de liga y fotos)
export const urlEscudo = (af) => (af ? `https://media.api-sports.io/football/teams/${af}.png` : null);
export const urlLiga = (af) => (af ? `https://media.api-sports.io/football/leagues/${af}.png` : null);
export const urlFoto = (af) => (af ? `https://media.api-sports.io/football/players/${af}.png` : null);
