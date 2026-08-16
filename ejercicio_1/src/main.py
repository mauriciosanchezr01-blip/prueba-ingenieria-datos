import os
import pandas as pd

from transform import normalize_phone
from validate import validate_dataset

# Rutas absolutas basadas en la ubicación de este archivo,
# para que el script funcione sin importar desde dónde se ejecute.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, "..", "data", "raw", "clientes.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "telefonos_clientes.csv")


def main():
    # Leer archivo fuente
    df = pd.read_csv(RAW_PATH)

    # Normalizar números telefónicos
    df["telefono"] = df["telefono"].apply(normalize_phone)

    # Aplicar reglas de validación
    df = validate_dataset(df)

    # Guardar dataset limpio
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)

    print(f"Dataset generado correctamente ({len(df)} registros válidos)")


if __name__ == "__main__":
    main()
