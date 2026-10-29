# Portal de scouting (proyecto Minería de Datos Aplicada)

Portal estadístico abierto de fútbol, inspirado en el modelo de reclutamiento del Brighton & Hove Albion.

## Cómo corre

El pipeline de datos se ejecuta en GitHub Actions (`.github/workflows/datos.yml`): se dispara en cada push a `scripts/` o manualmente desde la pestaña *Actions*. Al terminar, guarda el reporte en `data/reports/cobertura.md`.

Secrets requeridos en el repositorio: `API_FOOTBALL_KEY`.

## Ejecución local (opcional, Windows, PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts\01_descargar_fuentes.py
python scripts\02_reporte_cobertura.py
```

El primer script descarga varios cientos de MB en `data\raw`. El segundo genera `data\reports\cobertura.md`.

## Estructura

```
data/raw/        fuentes originales (no se versiona)
data/reports/    diagnósticos generados
scripts/         pipeline en Python, numerado por paso
.env             llaves de API (no se versiona)
```

## Fuentes de datos

| Fuente | Licencia / condición |
|---|---|
| Transfermarkt (dcaribou/transfermarkt-datasets) | CC0 |
| StatsBomb Open Data | Uso libre citando a StatsBomb con su logo |
| football-data.co.uk | Uso libre con atribución |
| API-Football | Según términos de la cuenta |
