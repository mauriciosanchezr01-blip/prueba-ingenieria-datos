import pandas as pd

from validate import validate_dataset


# Validar eliminación de duplicados
def test_remove_duplicates():

    data = {
        "id_cliente": [1, 2],
        "telefono": ["3001234567", "3001234567"]
    }

    df = pd.DataFrame(data)

    result = validate_dataset(df)

    assert len(result) == 1


# Validar teléfonos incorrectos
def test_remove_invalid_phone():

    data = {
        "id_cliente": [1, 2],
        "telefono": ["3001234567", "123"]
    }

    df = pd.DataFrame(data)

    result = validate_dataset(df)

    assert len(result) == 1


# Validar teléfono correcto
def test_valid_phone():

    data = {
        "id_cliente": [1],
        "telefono": ["3001234567"]
    }

    df = pd.DataFrame(data)

    result = validate_dataset(df)

    assert len(result) == 1


# Validar que se descartan registros sin teléfono (nulos)
def test_remove_null_phone():

    data = {
        "id_cliente": [1, 2],
        "telefono": ["3001234567", None]
    }

    df = pd.DataFrame(data)

    result = validate_dataset(df)

    assert len(result) == 1
