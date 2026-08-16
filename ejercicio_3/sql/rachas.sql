-- =====================================================================
-- Rachas de saldo por cliente, parametrizado por fecha_base y n
--
-- Para cambiar la fecha "como si estuvieramos parados hoy" o el largo
-- minimo de racha que se quiere buscar, solo hay que editar los dos
-- valores en el CTE "parametros" de abajo.
-- =====================================================================

WITH parametros AS (
    SELECT
        '2024-12-31' AS fecha_base,   -- <-- cambiar aqui la fecha de corte
        3            AS n              -- <-- cambiar aqui el largo minimo de racha
),

-- Genera el calendario de fin de mes desde el primer corte disponible
-- en 'historia' hasta la fecha_base.
calendario(mes) AS (
    WITH RECURSIVE cal(mes) AS (
        SELECT date((SELECT MIN(corte_mes) FROM historia), 'start of month', '+1 month', '-1 day')
        UNION ALL
        SELECT date(mes, '+1 day', 'start of month', '+1 month', '-1 day')
        FROM cal
        WHERE mes < (SELECT fecha_base FROM parametros)
    )
    SELECT mes FROM cal
),

-- Primer mes en el que aparece cada cliente en la historia
primera_aparicion AS (
    SELECT identificacion, MIN(corte_mes) AS mes_inicio
    FROM historia
    GROUP BY identificacion
),

-- Meses relevantes para cada cliente: desde su primera aparicion hasta
-- fecha_base, pero solo hasta su fecha de retiro si aplica (despues del
-- retiro no se imputa nada, el cliente simplemente sale del analisis).
meses_cliente AS (
    SELECT
        p.identificacion,
        c.mes AS corte_mes
    FROM primera_aparicion p
    JOIN calendario c
        ON c.mes >= p.mes_inicio
        AND c.mes <= (SELECT fecha_base FROM parametros)
    LEFT JOIN retiros r ON r.identificacion = p.identificacion
    WHERE r.fecha_retiro IS NULL OR c.mes <= r.fecha_retiro
),

-- Se cruza cada mes relevante con el saldo reportado ese mes (si no
-- hay registro en 'historia' para ese cliente-mes, se asume saldo 0 -> N0)
saldos_completos AS (
    SELECT
        mc.identificacion,
        mc.corte_mes,
        COALESCE(h.saldo, 0) AS saldo
    FROM meses_cliente mc
    LEFT JOIN historia h
        ON h.identificacion = mc.identificacion
        AND h.corte_mes = mc.corte_mes
),

-- Clasificacion por nivel de saldo
niveles AS (
    SELECT
        identificacion,
        corte_mes,
        saldo,
        CASE
            WHEN saldo >= 5000000 THEN 'N4'
            WHEN saldo >= 3000000 THEN 'N3'
            WHEN saldo >= 1000000 THEN 'N2'
            WHEN saldo >= 300000  THEN 'N1'
            ELSE 'N0'
        END AS nivel
    FROM saldos_completos
),

-- Tecnica de gaps-and-islands: la diferencia entre el orden global del
-- cliente y su orden dentro del mismo nivel es constante mientras el
-- nivel no cambie mes a mes. Eso agrupa los meses consecutivos.
marcado AS (
    SELECT
        identificacion,
        corte_mes,
        nivel,
        ROW_NUMBER() OVER (PARTITION BY identificacion ORDER BY corte_mes)
            - ROW_NUMBER() OVER (PARTITION BY identificacion, nivel ORDER BY corte_mes)
            AS grupo
    FROM niveles
),

-- Se arma cada racha: cuantos meses seguidos, en que nivel, y cuando termina
rachas AS (
    SELECT
        identificacion,
        nivel,
        COUNT(*) AS racha,
        MIN(corte_mes) AS fecha_inicio,
        MAX(corte_mes) AS fecha_fin
    FROM marcado
    GROUP BY identificacion, nivel, grupo
),

-- Solo las rachas que cumplen el largo minimo n
rachas_validas AS (
    SELECT r.*
    FROM rachas r, parametros p
    WHERE r.racha >= p.n
),

-- Por cliente: la racha mas larga: si hay empate, la de fecha_fin mas reciente
rankeado AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY identificacion
            ORDER BY racha DESC, fecha_fin DESC
        ) AS orden
    FROM rachas_validas
)

SELECT
    identificacion,
    racha,
    fecha_fin,
    nivel
FROM rankeado
WHERE orden = 1
ORDER BY racha DESC, identificacion;
