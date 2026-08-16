# Ejercicio 1 - Dataset de teléfonos de clientes

Pipeline en Python que toma el CSV crudo de clientes, limpia los números de
teléfono y deja un dataset validado listo para usar.

## Estructura

```
ejercicio_1/
├── conftest.py
├── requirements.txt
├── src/
│   ├── main.py         -> corre todo el proceso
│   ├── transform.py    -> normaliza el teléfono
│   └── validate.py     -> filtra lo que no sirve
├── tests/
│   └── test_dataset.py
└── data/
    ├── raw/         (clientes.csv va aquí)
    └── processed/   (se genera al correr main.py)
```

## Qué hace

`transform.py` le quita al teléfono todo lo que no sea un número: espacios,
guiones, paréntesis, el signo +, etc.

`validate.py` se encarga de:
- quitar filas sin teléfono
- quitar duplicados
- dejar solo los que tienen formato colombiano válido: 10 dígitos que
  empiecen en 3, o 12 dígitos con el indicativo 57 adelante

Cualquier otra cosa (números incompletos, con letras, etc.) se descarta.

## Cómo correrlo

Poner el `clientes.csv` en `data/raw/` y luego:

```bash
cd ejercicio_1/src
python main.py
```

Esto deja el archivo limpio en `data/processed/telefonos_clientes.csv` y
te dice cuántos registros quedaron válidos.

## Tests

Desde `ejercicio_1`:

```bash
pytest
```

El `conftest.py` es solo para que pytest encuentre los módulos de `src`
sin tener que instalar nada como paquete. Sin eso el import de
`validate` en los tests falla.

## Sobre CI/CD

La idea es que esto no sea un script que uno corre a mano cada vez, sino
algo integrado a un pipeline:

- En cada push/PR se corren los tests automáticamente (GitHub Actions,
  por ejemplo). Si algo rompe la validación, no debería pasar a producción.
- El pipeline podría tener un umbral: si de repente se está descartando
  un porcentaje muy alto de registros, eso es señal de que algo cambió
  en el origen de los datos y hay que revisar antes de publicar nada.
- Una vez validado, el dataset se publica al destino final (base de
  datos, bucket, etc.), idealmente versionado por fecha de corrida.
- El proceso se puede reprogramar para correr periódicamente (cron,
  Airflow) sobre datos nuevos, dejando registro de cuántos teléfonos se
  normalizaron, cuántos se descartaron y por qué — esto conecta directo
  con el ejercicio 2, que pide justamente visibilidad de calidad de datos.