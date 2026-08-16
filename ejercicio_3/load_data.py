"""
Carga rachas.xlsx (hojas 'historia' y 'retiros') en una base SQLite.

Regla de calidad de datos aplicada: en 'historia' hay un par de casos con
el mismo (identificacion, corte_mes) repetido. Para esos casos nos
quedamos con el saldo mas alto reportado ese mes (asuncion documentada
en el README: ante ambiguedad, se prefiere el escenario mas conservador
para el analisis de riesgo).
"""
import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = os.path.join(BASE_DIR, "data", "rachas.xlsx")
DB_PATH = os.path.join(BASE_DIR, "data", "rachas.db")

def main():
    historia = pd.read_excel(XLSX_PATH, sheet_name="historia")
    retiros = pd.read_excel(XLSX_PATH, sheet_name="retiros")

    historia["corte_mes"] = pd.to_datetime(historia["corte_mes"]).dt.date
    retiros["fecha_retiro"] = pd.to_datetime(retiros["fecha_retiro"]).dt.date

    # Deduplicar cliente+mes quedandonos con el saldo mas alto
    antes = len(historia)
    historia = (
        historia.sort_values("saldo", ascending=False)
        .drop_duplicates(subset=["identificacion", "corte_mes"], keep="first")
    )
    despues = len(historia)
    if antes != despues:
        print(f"Se depuraron {antes - despues} filas duplicadas de cliente+mes en 'historia'")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    historia.to_sql("historia", conn, index=False)
    retiros.to_sql("retiros", conn, index=False)

    conn.execute("CREATE INDEX idx_historia_id ON historia(identificacion)")
    conn.execute("CREATE INDEX idx_historia_mes ON historia(corte_mes)")
    conn.execute("CREATE INDEX idx_retiros_id ON retiros(identificacion)")
    conn.commit()

    print(f"Base creada en {DB_PATH}")
    print(f"historia: {len(historia)} filas, {historia['identificacion'].nunique()} clientes")
    print(f"retiros: {len(retiros)} filas")
    conn.close()

if __name__ == "__main__":
    main()
