"""Recoleccion de archivos HTML a procesar."""
from pathlib import Path
from typing import Iterable, List


class FileCollector:
    """Recibe una lista de rutas (archivos .html o directorios) y
    devuelve todos los archivos .html a procesar, recorriendo
    subdirectorios cuando la ruta es una carpeta."""

    def collect(self, rutas: Iterable[str]) -> List[Path]:
        archivos_html: List[Path] = []

        for ruta_texto in rutas:
            ruta = Path(ruta_texto)

            if not ruta.exists():
                continue

            if ruta.is_file() and ruta.suffix.lower() == ".html":
                archivos_html.append(ruta)
            elif ruta.is_dir():
                archivos_html.extend(sorted(ruta.rglob("*.html")))

        # eliminar duplicados conservando el orden, por si dos rutas
        # de entrada apuntan al mismo archivo
        vistos = set()
        unicos = []
        for archivo in archivos_html:
            resuelto = archivo.resolve()
            if resuelto not in vistos:
                vistos.add(resuelto)
                unicos.append(archivo)

        return unicos
