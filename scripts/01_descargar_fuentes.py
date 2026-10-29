"""
Paso 1: descarga las fuentes de datos base del portal.

Fuentes:
  - Transfermarkt (dcaribou/transfermarkt-datasets, CC0): base DuckDB completa
  - StatsBomb Open Data: catalogo de competiciones gratuitas
  - football-data.co.uk: resultados con momios (ligas principales y "extra", incluye Mexico)
  - API-Football: estado de la cuenta y cobertura (usa ~4 de las 100 consultas diarias)

Uso (desde la raiz del proyecto):
    python scripts/01_descargar_fuentes.py
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
load_dotenv(RAIZ / ".env")

TM_DUCKDB = "https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/transfermarkt-datasets.duckdb"
SB_COMPETITIONS = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json"
FD_BASE = "https://www.football-data.co.uk"
# Temporada 2025-26 de ligas principales (codigo -> liga)
FD_MAIN = {
    "E0": "Premier League", "E1": "Championship", "SP1": "LaLiga", "I1": "Serie A",
    "D1": "Bundesliga", "F1": "Ligue 1", "N1": "Eredivisie", "P1": "Liga Portugal",
    "B1": "Jupiler Pro League", "T1": "Super Lig", "G1": "Super League Grecia",
    "SC0": "Scottish Premiership",
}
# Archivos "extra": historico multi-temporada por pais
FD_EXTRA = ["MEX", "ARG", "BRA", "USA", "JPN", "DNK", "AUT", "SWZ", "POL", "NOR", "SWE", "RUS"]

API_FOOTBALL = "https://v3.football.api-sports.io"


def descargar(url: str, destino: Path, minimo_bytes: int = 100) -> bool:
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            hecho = 0
            with open(destino, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
                    hecho += len(chunk)
                    if total > 10_000_000:
                        print(f"\r  {hecho/1e6:,.0f} / {total/1e6:,.0f} MB", end="")
            if total > 10_000_000:
                print()
        ok = destino.stat().st_size >= minimo_bytes
        print(f"  {'OK ' if ok else 'VACIO'} {destino.relative_to(RAIZ)} ({destino.stat().st_size/1e6:,.2f} MB)")
        return ok
    except Exception as e:  # noqa: BLE001
        print(f"  ERROR {url}: {e}")
        return False


def transfermarkt():
    print("\n[1/4] Transfermarkt (DuckDB completa, puede tardar varios minutos)")
    destino = RAW / "transfermarkt" / "transfermarkt-datasets.duckdb"
    if destino.exists() and destino.stat().st_size > 50_000_000:
        print("  Ya existe, se omite. Borra el archivo para volver a descargarlo.")
        return
    descargar(TM_DUCKDB, destino, minimo_bytes=50_000_000)


def statsbomb():
    print("\n[2/4] StatsBomb Open Data (catalogo de competiciones)")
    descargar(SB_COMPETITIONS, RAW / "statsbomb" / "competitions.json")


def football_data():
    print("\n[3/4] football-data.co.uk (resultados y momios)")
    for codigo in FD_MAIN:
        descargar(f"{FD_BASE}/mmz4281/2526/{codigo}.csv", RAW / "football_data" / "2526" / f"{codigo}.csv")
        time.sleep(0.5)
    for pais in FD_EXTRA:
        descargar(f"{FD_BASE}/new/{pais}.csv", RAW / "football_data" / "extra" / f"{pais}.csv")
        time.sleep(0.5)


def api_football():
    print("\n[4/4] API-Football (diagnostico de plan y cobertura)")
    key = os.getenv("API_FOOTBALL_KEY")
    if not key:
        print("  Falta API_FOOTBALL_KEY en .env, se omite.")
        return
    destino = RAW / "api_football" / "diagnostico"
    destino.mkdir(parents=True, exist_ok=True)
    consultas = {
        "status": ("/status", {}),
        "liga_mx": ("/leagues", {"id": 262}),
        "premier": ("/leagues", {"id": 39}),
        "jugadores_liga_mx_2025": ("/players", {"league": 262, "season": 2025, "page": 1}),
    }
    for nombre, (ruta, params) in consultas.items():
        try:
            r = requests.get(API_FOOTBALL + ruta, params=params,
                             headers={"x-apisports-key": key}, timeout=60)
            datos = r.json()
            (destino / f"{nombre}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
            errores = datos.get("errors")
            print(f"  {nombre}: HTTP {r.status_code}, resultados={datos.get('results')}, errores={errores or 'ninguno'}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {nombre}: {e}")
        time.sleep(7)  # el plan gratuito limita consultas por minuto


if __name__ == "__main__":
    transfermarkt()
    statsbomb()
    football_data()
    api_football()
    print("\nListo. Siguiente paso: python scripts/02_reporte_cobertura.py")
