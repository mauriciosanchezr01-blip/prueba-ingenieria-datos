"""Tests del pipeline de conversion de imagenes a base64.

Corren con: python -m unittest discover -s tests
Solo usa la libreria estandar (unittest, tempfile, base64).
"""
import base64
import tempfile
import unittest
from pathlib import Path

from src.pipeline import Pipeline
from src.image_encoder import ImageEncoder, ImageEncodingError

# Un PNG de 1x1 pixel valido, para no depender de archivos externos
PNG_1x1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class TestImageEncoder(unittest.TestCase):
    def test_codifica_imagen_valida(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "foto.png"
            ruta.write_bytes(PNG_1x1)

            resultado = ImageEncoder().encode(ruta)

            self.assertTrue(resultado.startswith("data:image/png;base64,"))

    def test_falla_si_no_existe(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "no_existe.png"
            with self.assertRaises(ImageEncodingError):
                ImageEncoder().encode(ruta)

    def test_falla_si_no_es_imagen(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "documento.txt"
            ruta.write_text("hola")
            with self.assertRaises(ImageEncodingError):
                ImageEncoder().encode(ruta)


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

        (self.base / "images").mkdir()
        (self.base / "images" / "logo.png").write_bytes(PNG_1x1)

        self.html_path = self.base / "pagina.html"
        self.html_path.write_text(
            '<html><body>'
            '<img src="images/logo.png">'
            '<img src="images/falta.png">'
            '<img src="https://externo.com/x.png">'
            '</body></html>',
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_reporte_success_y_fail(self):
        reporte = Pipeline().run([str(self.html_path)])

        clave = str(self.html_path)
        self.assertIn(clave, reporte["success"])
        self.assertEqual(reporte["success"][clave], ["images/logo.png"])

        self.assertIn(clave, reporte["fail"])
        self.assertIn("images/falta.png", reporte["fail"][clave])
        self.assertIn("https://externo.com/x.png", reporte["fail"][clave])

    def test_archivo_original_no_se_modifica(self):
        contenido_antes = self.html_path.read_text(encoding="utf-8")
        Pipeline().run([str(self.html_path)])
        contenido_despues = self.html_path.read_text(encoding="utf-8")
        self.assertEqual(contenido_antes, contenido_despues)

    def test_se_crea_archivo_nuevo_con_base64(self):
        Pipeline().run([str(self.html_path)])

        nuevo = self.base / "pagina_base64.html"
        self.assertTrue(nuevo.exists())
        contenido = nuevo.read_text(encoding="utf-8")
        self.assertIn("data:image/png;base64,", contenido)

    def test_recorre_directorios(self):
        reporte = Pipeline().run([str(self.base)])
        clave = str(self.html_path)
        self.assertIn(clave, reporte["success"])


if __name__ == "__main__":
    unittest.main()
