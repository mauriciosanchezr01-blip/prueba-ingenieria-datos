"""
Convierte las imagenes referenciadas en archivos HTML a base64.

Uso:
    python main.py archivo.html
    python main.py carpeta1 carpeta2 archivo_suelto.html
    python main.py examples --json-out reporte.json
"""
import argparse
import json
import sys

from src.pipeline import Pipeline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "rutas",
        nargs="+",
        help="Archivos .html o carpetas a procesar (recorre subcarpetas)",
    )
    parser.add_argument(
        "--json-out",
        help="Ruta donde guardar el reporte success/fail en formato JSON",
    )
    args = parser.parse_args()

    pipeline = Pipeline()
    reporte = pipeline.run(args.rutas)

    salida = json.dumps(reporte, indent=2, ensure_ascii=False)
    print(salida)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(salida)
        print(f"\nReporte guardado en {args.json_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
