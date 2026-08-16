"""Orquesta el proceso completo sobre una lista de archivos/directorios."""
from pathlib import Path
from typing import Iterable

from .file_collector import FileCollector
from .html_processor import HtmlImageProcessor
from .image_encoder import ImageEncoder


class Pipeline:
    """Punto de entrada del proceso: recibe rutas (archivos .html o
    carpetas), procesa cada HTML encontrado y devuelve un reporte
    consolidado con las imagenes que se lograron convertir y las que
    fallaron, por archivo."""

    SUFIJO_SALIDA = "_base64"

    def __init__(self):
        self._collector = FileCollector()
        self._processor = HtmlImageProcessor(ImageEncoder())

    def run(self, rutas: Iterable[str]) -> dict:
        archivos_html = self._collector.collect(rutas)

        reporte = {"success": {}, "fail": {}}

        for html_path in archivos_html:
            output_path = self._ruta_salida(html_path)
            resultado = self._processor.process(html_path, output_path)

            clave = str(html_path)
            if resultado.exitosas:
                reporte["success"][clave] = resultado.exitosas
            if resultado.fallidas:
                reporte["fail"][clave] = resultado.fallidas

        return reporte

    def _ruta_salida(self, html_path: Path) -> Path:
        return html_path.with_name(
            f"{html_path.stem}{self.SUFIJO_SALIDA}{html_path.suffix}"
        )
