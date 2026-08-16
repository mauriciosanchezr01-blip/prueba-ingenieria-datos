# Ejercicio 3 - Rachas de saldo por cliente

Consultas SQL para identificar, para cada cliente, la racha de meses
consecutivos en un mismo nivel de deuda, a partir de la informacion de
`rachas.xlsx`.

## Estructura

```
ejercicio_3/
├── data/
│   └── rachas.xlsx      -> archivo original
├── sql/
│   └── rachas.sql        -> la consulta completa
├── load_data.py           -> carga el excel a sqlite
├── run_rachas.py          -> corre la consulta con distintos parametros
└── requirements.txt
```

Uso SQLite porque no necesita servidor, corre con el archivo, y
cualquiera puede replicarlo sin instalar nada aparte de python.

## Cómo correrlo

```bash
pip install pandas openpyxl -r requirements.txt
python load_data.py                                  # crea data/rachas.db
python run_rachas.py --fecha-base 2024-12-31 --n 3    # corre la consulta
```

`--fecha-base` es la fecha en la que uno se "para" a mirar el histórico
(no tiene que ser la fecha de hoy), y `--n` es el largo mínimo de racha
que se está buscando. Se puede guardar el resultado con `--out
resultado.csv`.

## Los datos

`historia`: identificacion, corte_mes, saldo — un registro por cliente
por mes.

`retiros`: identificacion, fecha_retiro — los clientes que se retiraron
en algún momento del histórico.

Antes de cargar los datos me encontré con dos filas duplicadas de mismo
cliente + mismo mes en `historia` (una con el mismo saldo repetido, otra
con dos saldos distintos para el mismo corte). `load_data.py` las
depura quedándose con el saldo más alto reportado — es una decisión
que tomé para no perder el registro sin saber cuál de los dos es el
correcto, y en un caso real se lo consultaría a quien entregó los datos.

## Niveles de saldo

```
N0: saldo >= 0          y < 300.000
N1: saldo >= 300.000    y < 1.000.000
N2: saldo >= 1.000.000  y < 3.000.000
N3: saldo >= 3.000.000  y < 5.000.000
N4: saldo >= 5.000.000
```

## Cómo maneja la consulta los meses sin dato

Si un cliente no aparece en un mes específico después de haber
aparecido por primera vez, se asume saldo 0 (nivel N0) para ese mes —
así lo pide el enunciado. La única excepción es si ese mes ya es
posterior a la fecha de retiro del cliente: ahí simplemente no se
imputa nada, el cliente sale del análisis desde su retiro en adelante.

Para armar esto, la consulta genera un calendario completo de meses
(de fin a fin de mes) entre el primer corte disponible en toda la
historia y la `fecha_base`, y lo cruza con cada cliente desde su primera
aparición. Donde no hay saldo real reportado, queda en 0.

## Cómo se arman las rachas

Una vez cada mes tiene su nivel asignado (real o imputado), agrupo los
meses consecutivos que quedan en el mismo nivel usando la técnica de
gaps-and-islands: la diferencia entre la posición del mes dentro de
toda la serie del cliente y su posición dentro de su mismo nivel se
mantiene constante mientras no cambie de nivel, y cambia apenas hay un
mes distinto — eso es lo que separa una racha de la siguiente.

De todas las rachas de un cliente, me quedo solo con las que tengan al
menos `n` meses. Si un cliente tiene más de una que cumple, elijo la
más larga; si hay empate en longitud, la que termina más cerca de la
`fecha_base`.

## Resultado

La consulta devuelve, por cliente:

- `identificacion`
- `racha`: cuántos meses consecutivos duró
- `fecha_fin`: en qué corte de mes terminó esa racha
- `nivel`: en qué nivel de saldo estuvo esa racha

## Verificación manual

Antes de dar la consulta por buena, tracé a mano el histórico completo
de un cliente (`IGOQX9XYBSRDMOZXT`) y confirmé mes a mes que la racha
de 6 meses en N4 que devuelve la consulta (jul-dic 2023) es correcta,
incluyendo un mes sin dato en medio del histórico que se imputó bien
como N0. También verifiqué que los clientes retirados dejan de
considerarse justo después de su fecha de retiro, y no antes ni
después.
