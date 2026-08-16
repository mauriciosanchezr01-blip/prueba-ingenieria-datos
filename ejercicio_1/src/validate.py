def validate_dataset(df):
    """
    Aplica reglas de calidad sobre el dataset de teléfonos:
    - Elimina registros sin teléfono.
    - Elimina teléfonos duplicados.
    - Conserva únicamente teléfonos con formato colombiano válido
      (10 dígitos iniciando en 3, o 12 dígitos iniciando en 57).
    """

    # Eliminar teléfonos vacíos
    df = df.dropna(subset=["telefono"])

    # Eliminar duplicados
    df = df.drop_duplicates(subset=["telefono"])

    # Validar formato colombiano
    df = df[
        df["telefono"].str.match(r"^(3\d{9}|57\d{10})$")
    ]

    return df
