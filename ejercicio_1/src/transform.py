import re


def normalize_phone(phone):
    """
    Normaliza un número telefónico eliminando
    espacios, guiones, paréntesis y cualquier
    carácter no numérico.

    Ejemplos:
    (+57) 310-444-5555 -> 573104445555
    300 123 4567 -> 3001234567
    """

    # Si el valor es nulo, retornar nulo
    if phone is None:
        return None

    # Convertir a texto para evitar errores de tipo
    phone = str(phone)

    # Eliminar cualquier carácter que no sea un número
    return re.sub(r"\D", "", phone)
