"""Codificacion de imagenes a base64."""
import base64
import mimetypes
from pathlib import Path


class ImageEncodingError(Exception):
    """Se lanza cuando una imagen no se pudo leer o codificar."""


class ImageEncoder:
    """Convierte un archivo de imagen local en un data URI base64.

    Un data URI se ve asi: 'data:image/png;base64,iVBORw0KG...'
    y se puede usar directamente como valor del atributo src de un
    tag <img>, sin depender de un archivo externo.
    """

    def encode(self, image_path: Path) -> str:
        if not image_path.is_file():
            raise ImageEncodingError(f"no existe el archivo: {image_path}")

        mime_type, _ = mimetypes.guess_type(image_path.name)
        if mime_type is None or not mime_type.startswith("image/"):
            raise ImageEncodingError(
                f"no se reconoce como imagen: {image_path.name}"
            )

        try:
            contenido = image_path.read_bytes()
        except OSError as exc:
            raise ImageEncodingError(f"no se pudo leer {image_path}: {exc}") from exc

        codificado = base64.b64encode(contenido).decode("ascii")
        return f"data:{mime_type};base64,{codificado}"
