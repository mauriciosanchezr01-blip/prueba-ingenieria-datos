"""Procesamiento de un archivo HTML: reemplazo de imagenes por base64."""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from .image_encoder import ImageEncoder, ImageEncodingError

# Busca tags <img ...> y captura el valor del atributo src, sin
# importar que otros atributos tenga el tag antes o despues de src.
PATRON_IMG = re.compile(
    r'(<img\b[^>]*?\bsrc\s*=\s*["\'])([^"\']+)(["\'][^>]*>)',
    re.IGNORECASE,
)


@dataclass
class ResultadoArchivo:
    """Resultado de procesar un unico archivo HTML."""

    exitosas: List[str] = field(default_factory=list)
    fallidas: dict = field(default_factory=dict)  # src -> motivo


class HtmlImageProcessor:
    """Toma un archivo HTML, reemplaza cada imagen local referenciada
    en un tag <img> por su version en base64, y escribe el resultado
    en un archivo nuevo sin tocar el original."""

    def __init__(self, encoder: ImageEncoder):
        self._encoder = encoder

    def process(self, html_path: Path, output_path: Path) -> ResultadoArchivo:
        contenido = html_path.read_text(encoding="utf-8")
        resultado = ResultadoArchivo()

        def reemplazar(match: re.Match) -> str:
            prefijo, src, sufijo = match.group(1), match.group(2), match.group(3)

            if self._es_remota_o_ya_embebida(src):
                resultado.fallidas[src] = "URL remota o imagen ya en base64, no se procesa"
                return match.group(0)

            ruta_imagen = (html_path.parent / src).resolve()

            try:
                data_uri = self._encoder.encode(ruta_imagen)
            except ImageEncodingError as exc:
                resultado.fallidas[src] = str(exc)
                return match.group(0)

            resultado.exitosas.append(src)
            return f"{prefijo}{data_uri}{sufijo}"

        nuevo_contenido = PATRON_IMG.sub(reemplazar, contenido)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(nuevo_contenido, encoding="utf-8")

        return resultado

    @staticmethod
    def _es_remota_o_ya_embebida(src: str) -> bool:
        if src.startswith("data:"):
            return True
        esquema = urlparse(src).scheme
        return esquema in ("http", "https")
