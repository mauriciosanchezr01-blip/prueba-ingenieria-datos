"""
Corre la consulta de rachas.sql con una fecha_base y un n dados.

Uso:
    python run_rachas.py --fecha-base 2024-12-31 --n 3
    python run_rachas.py --fecha-base 2024-06-30 --n 4 --out resultado.csv
"""
import sqlite3
import argparse
import os
import csv
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "rachas.db")
SQL_PATH = os.path.join(BASE_DIR, "sql", "rachas.sql")


def construir_query(fecha_base: str, n: int) -> str:
    """Toma el .sql base y reemplaza los valores del CTE 'parametros'
    por los que llegaron desde la linea de comandos, sin tener que
    editar el archivo a mano cada vez."""
    with open(SQL_PATH, encoding="utf-8") as f:
        sql = f.read()

    sql = re.sub(
        r"'2024-12-31'\s+AS fecha_base",
        f"'{fecha_base}' AS fecha_base",
        sql,
    )
    sql = re.sub(
        r"3\s+AS n",
        f"{n} AS n",
        sql,
    )
    return sql


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fecha-base", default="2024-12-31", help="Fecha de corte (YYYY-MM-DD)")
    parser.add_argument("--n", type=int, default=3, help="Largo minimo de racha")
    parser.add_argument("--out", default=None, help="Ruta de salida CSV (opcional)")
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        raise SystemExit("No existe data/rachas.db. Corre primero: python load_data.py")

    conn = sqlite3.connect(DB_PATH)
    query = construir_query(args.fecha_base, args.n)
    cursor = conn.execute(query)
    columnas = [d[0] for d in cursor.description]
    filas = cursor.fetchall()

    print(f"fecha_base={args.fecha_base}  n={args.n}  clientes con racha valida={len(filas)}")
    print(",".join(columnas))
    for f in filas[:20]:
        print(",".join(str(x) for x in f))
    if len(filas) > 20:
        print(f"... ({len(filas) - 20} filas mas)")

    if args.out:
        out_path = os.path.join(BASE_DIR, args.out)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columnas)
            writer.writerows(filas)
        print(f"\nGuardado en {out_path}")

    conn.close()


if __name__ == "__main__":
    main()
