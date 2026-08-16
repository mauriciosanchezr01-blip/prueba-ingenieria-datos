# Ejercicio 4 - Imagenes de HTML a base64

Scripts en Python puro (solo libreria estandar, sin pip install) que
recorren archivos HTML, encuentran las imagenes referenciadas en tags
`<img>`, y generan una copia nueva del HTML con esas imagenes
incrustadas en base64.

## Estructura

```
ejercicio_4/
├── main.py                  -> punto de entrada (linea de comandos)
├── src/
│   ├── image_encoder.py      -> lee una imagen y la vuelve un data URI
│   ├── html_processor.py      -> encuentra <img> en un HTML y los reemplaza
│   ├── file_collector.py       -> junta los .html a procesar (archivos o carpetas)
│   └── pipeline.py              -> conecta todo lo anterior y arma el reporte
├── tests/
│   └── test_pipeline.py          -> tests con unittest
└── examples/                       -> HTML e imagenes de prueba
```

## Cómo correrlo

```bash
python main.py archivo.html
python main.py carpeta1 carpeta2 archivo_suelto.html
python main.py examples --json-out reporte.json
```

Se le puede pasar cualquier combinación de archivos `.html` sueltos o
carpetas — si es una carpeta, recorre subcarpetas también buscando
`.html`.

Por cada HTML que encuentra, genera un archivo nuevo al lado del
original con el sufijo `_base64` (`catalogo.html` →
`catalogo_base64.html`), sin tocar el original.

## Qué hace cada parte

- `ImageEncoder`: recibe la ruta de una imagen, la lee, adivina su
  tipo MIME por la extensión, y arma el data URI
  (`data:image/png;base64,...`). Si el archivo no existe o no es una
  imagen reconocible, lanza un error específico.
- `HtmlImageProcessor`: busca los tags `<img src="...">` en el HTML,
  resuelve esa ruta relativa a donde está el archivo HTML, y para cada
  una intenta codificarla. Si funciona, reemplaza el `src`; si falla,
  deja el tag como estaba y anota el motivo.
- `FileCollector`: dado un listado de rutas (archivos o carpetas),
  devuelve todos los `.html` a procesar.
- `Pipeline`: junta todo — recolecta los HTML, procesa cada uno, y
  arma el reporte final.

## El reporte

Cada corrida devuelve (y opcionalmente guarda en JSON) un objeto así:

```json
{
  "success": {
    "examples/catalogo.html": ["images/logo.png", "images/banner.jpg"]
  },
  "fail": {
    "examples/catalogo.html": {
      "images/no_existe.png": "no existe el archivo: ...",
      "https://ejemplo.com/foto.png": "URL remota o imagen ya en base64, no se procesa"
    }
  }
}
```

`success` lista las imágenes que sí se pudieron convertir por cada
archivo. `fail` trae, por archivo, cada imagen que no se pudo procesar
junto con el motivo puntual.

## Decisiones que tomé

- **Imágenes remotas (`http://`, `https://`) se marcan como fallo, no
  se descargan.** El enunciado habla de imágenes asociadas a los
  archivos HTML, y descargar contenido externo cambia el alcance del
  ejercicio (dependencias de red, timeouts, etc). Lo dejo documentado
  como "no soportado" en vez de fallar silenciosamente.
- **Uso una expresión regular para encontrar los tags `<img>`**, en
  vez de un parser HTML completo. Es más simple, preserva el
  formato original del archivo tal cual estaba (un parser completo
  reordena atributos o normaliza el HTML al reescribirlo), y el
  enunciado ya asume que las imágenes siempre están en tag `<img>`.
- **El archivo nuevo se crea al lado del original**, con sufijo
  `_base64`, no en una carpeta aparte — me pareció más simple de
  navegar que reconstruir una estructura de carpetas de salida en
  paralelo.

## Tests

```bash
python -m unittest discover -s tests -v
```

Cubren: codificación de una imagen válida, manejo de imagen
inexistente, manejo de archivo que no es imagen, reporte
success/fail correcto, que el original no se modifica, que el archivo
nuevo sí trae el base64, y que el recorrido de carpetas funciona.
