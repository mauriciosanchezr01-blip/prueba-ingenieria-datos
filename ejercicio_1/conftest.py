import sys
import os

# Agrega la carpeta "src" al path para que los tests puedan
# importar los módulos (transform, validate) sin necesidad
# de convertir el proyecto en un paquete instalable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
