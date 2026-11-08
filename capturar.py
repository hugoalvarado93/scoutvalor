"""Toma capturas de las secciones de https://scoutvalor.app para el reporte."""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "https://scoutvalor.app"
OUT = Path("t/portal")
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5, locale="es-MX")
    pag = ctx.new_page()

    def tomar(ruta, nombre, alto=900):
        pag.goto(BASE + ruta, wait_until="networkidle")
        pag.wait_for_timeout(3500)
        pag.screenshot(path=str(OUT / f"{nombre}.png"), clip={"x": 0, "y": 0, "width": 1440, "height": alto}, full_page=True)
        print(nombre, "ok")

    tomar("/", "inicio", 1100)
    tomar("/radar", "radar", 1100)
    enlace = pag.locator("a[href^='/jugador/']").first.get_attribute("href")
    tomar(enlace, "jugador", 1300)
    tomar("/equipos", "equipos", 1300)
    tomar("/simulador", "simulador", 1200)
    tomar("/metodologia", "metodologia", 1100)
    (OUT / "jugador_url.txt").write_text(enlace)
    nav.close()
