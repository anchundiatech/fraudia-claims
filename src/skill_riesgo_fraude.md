---
---
name: AuditoriaRiesgoFraudeSupabase
description: Instrucciones y consultas SQL optimizadas para auditar, clasificar y detectar fraudes en pólizas, siniestros y proveedores utilizando Supabase y PostgreSQL.
---

# Guía de Auditoría de Riesgo de Fraude (Supabase/PostgreSQL)

Esta guía técnica (Skill) contiene las consultas SQL declarativas de alto rendimiento necesarias para responder a las preguntas estratégicas y operativas de la Unidad Antifraude sobre la base de datos de producción de **Supabase**.

---

## 1. Catálogo Físico de Datos de Soporte y Relaciones

Para ejecutar las auditorías, las consultas interactúan con las siguientes estructuras relacionales:
*   **`public."ASEGURADO"`**: Almacena los datos personales del cliente (`nombre`, `apellido`, `nro_documento`).
*   **`public."POLIZA"`**: Almacena los contratos de cobertura vinculados a los asegurados (`prima`, `id_asegurado`).
*   **`public."SINIESTRO"`**: Registra las reclamaciones asociadas a cada póliza (`monto_reclamado`, `monto_estimado`, `monto_pagado`, `sucursal`, `ramo`, `cobertura`, `id_beneficiario`).
*   **`public."BENEFICIARIO_PROVEEDOR"`**: Almacena las identidades de los talleres mecánicos, clínicas y proveedores (`nombre`, `nro_documento`, `tipo`).
*   **`public."DOCUMENTO"`**: Almacena los requisitos documentales presentados por siniestro (`tipo_documento`, `estado`).
*   **`public."PUNTAJE"` (Catálogo de Reglas)**: Define los parámetros para las señales de riesgo (`A` = Vigencia, `B` = Robo, `C` = Frecuencia Asegurado, etc.).
*   **`public."POLIZA_PUNTAJE"` (Auditoría Persistida)**: Logs de puntaje asignado a pólizas y siniestros.
*   **`public."SCORE_RIESGO"` (Semáforo Antifraude)**: Rangos de riesgo que clasifican a las pólizas, siniestros, asegurados y proveedores en tres niveles (`Verde Bajo`, `Amarillo Medio`, `Rojo Alto`).

### Estructura de Salida Unificada
Por directiva de control analítico, **todas las consultas en esta guía deben incluir obligatoriamente las siguientes columnas métricas**:
1.  **CANTIDAD SINIESTROS** (`cantidad_siniestros`): Recuento físico de reclamos únicos.
2.  **monto_estimado** (`siniestro_monto_estimado`): Suma o valor individual de la reserva estimada de la compañía.
3.  **monto_reclamado** (`siniestro_monto_reclamado`): Suma o valor individual del dinero reclamado por el cliente.
4.  **prima** (`poliza_prima`): Suma o valor individual de la prima comercial cobrada.
5.  **puntaje** (`total_puntaje_riesgo`): Severidad de riesgo técnico persistida.
6.  **nombre** (`asegurado_nombre`): Identidad concatenada del cliente.

En las consultas con agrupamiento (Ramo, Ciudad, Proveedor), las métricas financieras se calculan mediante sumatorias (`SUM`), los siniestros mediante recuentos únicos (`COUNT(DISTINCT)`), los puntajes como sumatorias agregadas y los nombres de asegurados se listan de forma agregada utilizando la función analítica `STRING_AGG(DISTINCT)`.

---

## 2. Consultas de Auditoría (Q18 - Q29)

### Q18. ¿Cuáles son los 10 siniestros (SINIESTRO) con mayor riesgo de posible fraude (POLIZA_PUNTAJE)?
*   **Lógica**: Agrupa y suma el puntaje de todas las alarmas en `POLIZA_PUNTAJE` por siniestro, mostrando las métricas y los nombres de asegurados correspondientes, ordenados descendentemente.
```sql
SELECT 
    s.id AS siniestro_id,
    a.nombre || ' ' || a.apellido AS asegurado_nombre,
    COUNT(DISTINCT s.id) AS cantidad_siniestros,
    s.monto_estimado AS siniestro_monto_estimado,
    s.monto_reclamado AS siniestro_monto_reclamado,
    p.prima AS poliza_prima,
    SUM(pp.puntaje) AS total_puntaje_riesgo
FROM 
    public."POLIZA_PUNTAJE" pp
JOIN 
    public."SINIESTRO" s ON pp.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
GROUP BY 
    s.id, 
    a.nombre, 
    a.apellido, 
    s.monto_estimado, 
    s.monto_reclamado, 
    p.prima
ORDER BY 
    total_puntaje_riesgo DESC
LIMIT 10;
```

---

### Q19. ¿Por qué este siniestro (SINIESTRO) fue marcado como alto riesgo (POLIZA_PUNTAJE)?
*   **Lógica**: Desglosa de forma detallada cada una de las señales y penalizaciones aplicadas a un siniestro específico, correlacionándolo con las columnas métricas del siniestro y del asegurado.
```sql
SELECT 
    pp.id_siniestro,
    a.nombre || ' ' || a.apellido AS asegurado_nombre,
    1 AS cantidad_siniestros,
    s.monto_estimado AS siniestro_monto_estimado,
    s.monto_reclamado AS siniestro_monto_reclamado,
    p.prima AS poliza_prima,
    pp.id_puntaje,
    p_cat.codigo AS senial_codigo,
    pp.senial AS senial_descripcion,
    pp.puntaje AS senial_puntaje
FROM 
    public."POLIZA_PUNTAJE" pp
JOIN 
    public."PUNTAJE" p_cat ON pp.id_puntaje = p_cat.id
JOIN 
    public."SINIESTRO" s ON pp.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
WHERE 
    pp.id_siniestro = :p_siniestro_id;
```

---

### Q20. ¿Qué proveedores (BENEFICIARIO_PROVEEDOR) concentran más alertas? (SINIESTRO) Y (POLIZA_PUNTAJE)
*   **Lógica**: Agrupa y cuenta las alertas, siniestros y sumatoria de puntajes por proveedor, consolidando los montos, primas y listando a los asegurados vinculados por medio de `STRING_AGG`.
```sql
SELECT 
    bp.id AS proveedor_id,
    bp.nombre AS proveedor_nombre,
    bp.tipo AS proveedor_tipo,
    bp.nro_documento AS proveedor_nro_documento,
    COUNT(DISTINCT s.id) AS cantidad_siniestros,
    SUM(s.monto_estimado) AS total_monto_estimado,
    SUM(s.monto_reclamado) AS total_monto_reclamado,
    SUM(p.prima) AS total_poliza_prima,
    SUM(pp.puntaje) AS total_puntaje_riesgo,
    COUNT(pp.id) AS total_alertas_detonadas,
    STRING_AGG(DISTINCT a.nombre || ' ' || a.apellido, ', ') AS asegurados_vinculados
FROM 
    public."POLIZA_PUNTAJE" pp
JOIN 
    public."SINIESTRO" s ON pp.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
JOIN 
    public."BENEFICIARIO_PROVEEDOR" bp ON s.id_beneficiario = bp.id
GROUP BY 
    bp.id, bp.nombre, bp.tipo, bp.nro_documento
ORDER BY 
    total_puntaje_riesgo DESC, 
    cantidad_siniestros DESC;
```

---

### Q21. ¿Qué ramos (SINIESTRO.ramo) tienen mayor porcentaje de casos sospechosos? (POLIZA_PUNTAJE)
*   **Lógica**: Calcula el porcentaje de casos sospechosos (siniestros con alertas) sobre el total de casos por ramo, incorporando las métricas unificadas y los nombres de asegurados involucrados.
```sql
WITH total_siniestros_ramo AS (
    SELECT 
        ramo,
        COUNT(id) AS total_casos,
        SUM(monto_estimado) AS total_estimado,
        SUM(monto_reclamado) AS total_reclamado
    FROM 
        public."SINIESTRO"
    GROUP BY 
        ramo
),
siniestros_sospechosos AS (
    SELECT 
        s.ramo,
        COUNT(DISTINCT s.id) AS casos_sospechosos,
        SUM(pp.puntaje) AS total_puntaje,
        SUM(p.prima) AS total_prima,
        STRING_AGG(DISTINCT a.nombre || ' ' || a.apellido, ', ') AS asegurados_nombres
    FROM 
        public."POLIZA_PUNTAJE" pp
    JOIN 
        public."SINIESTRO" s ON pp.id_siniestro = s.id
    JOIN 
        public."POLIZA" p ON s.id_poliza = p.id
    JOIN 
        public."ASEGURADO" a ON p.id_asegurado = a.id
    WHERE 
        pp.puntaje > 0
    GROUP BY 
        s.ramo
)
SELECT 
    tsr.ramo,
    tsr.total_casos AS cantidad_siniestros,
    tsr.total_estimado AS siniestro_monto_estimado,
    tsr.total_reclamado AS siniestro_monto_reclamado,
    COALESCE(ss.total_prima, 0) AS poliza_prima,
    COALESCE(ss.total_puntaje, 0) AS total_puntaje_riesgo,
    COALESCE(ss.casos_sospechosos, 0) AS casos_sospechosos,
    ROUND((COALESCE(ss.casos_sospechosos, 0)::numeric * 100.0 / tsr.total_casos), 2) AS pct_casos_sospechosos,
    COALESCE(ss.asegurados_nombres, '') AS asegurado_nombre
FROM 
    total_siniestros_ramo tsr
LEFT JOIN 
    siniestros_sospechosos ss ON tsr.ramo = ss.ramo
ORDER BY 
    pct_casos_sospechosos DESC;
```

---

### Q22. ¿Qué ciudades presentan (SINIESTRO.sucursal) mayor concentración de alertas? (POLIZA_PUNTAJE)
*   **Lógica**: Agrupa y cuenta las alertas, siniestros y sumatoria de puntaje por ciudad de la sucursal, consolidando los montos financieros y los nombres de asegurados vinculados.
```sql
SELECT 
    s.sucursal AS ciudad_sucursal,
    COUNT(DISTINCT s.id) AS cantidad_siniestros,
    SUM(s.monto_estimado) AS total_monto_estimado,
    SUM(s.monto_reclamado) AS total_monto_reclamado,
    SUM(p.prima) AS total_poliza_prima,
    SUM(pp.puntaje) AS total_puntaje_riesgo,
    COUNT(pp.id) AS total_alertas_detonadas,
    STRING_AGG(DISTINCT a.nombre || ' ' || a.apellido, ', ') AS asegurados_vinculados
FROM 
    public."POLIZA_PUNTAJE" pp
JOIN 
    public."SINIESTRO" s ON pp.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
GROUP BY 
    s.sucursal
ORDER BY 
    total_puntaje_riesgo DESC, 
    cantidad_siniestros DESC;
```

---

### Q23. ¿Qué asegurados (ASEGURADO.nro_documento y nombre) tienen mayor frecuencia de reclamos? (POLIZA_PUNTAJE)
*   **Lógica**: Clasifica a los asegurados según su frecuencia de siniestros reportados y la sumatoria de puntaje acumulado en el sistema, incorporando sus montos financieros.
```sql
SELECT 
    a.id AS asegurado_id,
    a.nombre || ' ' || a.apellido AS asegurado_nombre,
    a.nro_documento AS asegurado_documento,
    COUNT(DISTINCT s.id) AS cantidad_siniestros,
    SUM(s.monto_estimado) AS total_monto_estimado,
    SUM(s.monto_reclamado) AS total_monto_reclamado,
    SUM(p.prima) AS total_poliza_prima,
    SUM(pp.puntaje) AS total_puntaje_riesgo
FROM 
    public."POLIZA_PUNTAJE" pp
JOIN 
    public."SINIESTRO" s ON pp.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
GROUP BY 
    a.id, a.nombre, a.apellido, a.nro_documento
ORDER BY 
    total_puntaje_riesgo DESC, 
    cantidad_siniestros DESC;
```

---

### Q24. ¿Qué documentos (DOCUMENTO) faltan en los casos críticos? (POLIZA_PUNTAJE)
*   **Lógica**: Filtra los siniestros con estatus crítico (Rojo Alto, puntaje total >= 76) y lista detalladamente los documentos pendientes, no entregados o rechazados.
```sql
WITH siniestros_criticos AS (
    SELECT 
        pp.id_siniestro,
        SUM(pp.puntaje) AS total_puntaje
    FROM 
        public."POLIZA_PUNTAJE" pp
    GROUP BY 
        pp.id_siniestro
    HAVING 
        SUM(pp.puntaje) >= 76
)
SELECT 
    sc.id_siniestro,
    sc.total_puntaje AS total_puntaje_riesgo,
    COUNT(DISTINCT s.id) AS cantidad_siniestros,
    SUM(s.monto_estimado) AS total_monto_estimado,
    SUM(s.monto_reclamado) AS total_monto_reclamado,
    SUM(p.prima) AS total_poliza_prima,
    STRING_AGG(DISTINCT a.nombre || ' ' || a.apellido, ', ') AS asegurado_nombre,
    d.id AS documento_id,
    d.tipo_documento AS documento_tipo,
    d.estado AS documento_estado
FROM 
    siniestros_criticos sc
JOIN 
    public."SINIESTRO" s ON sc.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
JOIN 
    public."DOCUMENTO" d ON s.id = d.id_siniestro
WHERE 
    d.estado IN ('Pendiente', 'No Entregado', 'Rechazado')
GROUP BY 
    sc.id_siniestro, 
    sc.total_puntaje, 
    d.id, 
    d.tipo_documento, 
    d.estado
ORDER BY 
    total_puntaje_riesgo DESC, 
    sc.id_siniestro ASC;
```

---

### Q25. ¿Qué casos tienen montos (SINIESTRO.monto_pagado) atípicos? (POLIZA_PUNTAJE)
*   **Lógica**: Extrae los siniestros sospechosos (con alertas) cuyo `monto_pagado` sea significativamente atípico respecto al promedio de su ramo (+2 Desviaciones Estándar).
```sql
WITH estadisticas_ramo AS (
    SELECT 
        ramo,
        AVG(monto_pagado) AS media_monto,
        STDDEV(monto_pagado) AS desviacion_monto
    FROM 
        public."SINIESTRO"
    WHERE 
        monto_pagado > 0
    GROUP BY 
        ramo
),
puntajes_acumulados AS (
    SELECT 
        id_siniestro,
        SUM(puntaje) AS total_puntaje
    FROM 
        public."POLIZA_PUNTAJE" pp
    GROUP BY 
        id_siniestro
)
SELECT 
    s.id AS siniestro_id,
    a.nombre || ' ' || a.apellido AS asegurado_nombre,
    1 AS cantidad_siniestros,
    s.monto_estimado AS siniestro_monto_estimado,
    s.monto_reclamado AS siniestro_monto_reclamado,
    p.prima AS poliza_prima,
    s.monto_pagado,
    ROUND(er.media_monto::numeric, 2) AS media_ramo,
    ROUND((s.monto_pagado - er.media_monto)::numeric, 2) AS desviacion_de_media,
    pa.total_puntaje AS total_puntaje_riesgo
FROM 
    public."SINIESTRO" s
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
JOIN 
    estadisticas_ramo er ON s.ramo = er.ramo
LEFT JOIN 
    puntajes_acumulados pa ON s.id = pa.id_siniestro
WHERE 
    s.monto_pagado > (er.media_monto + 2 * er.desviacion_monto)
    AND pa.total_puntaje > 0
ORDER BY 
    s.monto_pagado DESC;
```

---

### Q26. ¿Qué siniestros ocurrieron (SINIESTRO.fecha_ocurrencia) cerca del inicio de la póliza (POLIZA.fecha_inicio y fecha_fin)? (POLIZA_PUNTAJE)
*   **Lógica**: Muestra los reclamos penalizados por la Señal A (cercanía a los límites de vigencia de póliza), detallando montos, primas y nombres de clientes.
```sql
SELECT 
    s.id AS siniestro_id,
    a.nombre || ' ' || a.apellido AS asegurado_nombre,
    1 AS cantidad_siniestros,
    s.monto_estimado AS siniestro_monto_estimado,
    s.monto_reclamado AS siniestro_monto_reclamado,
    p.prima AS poliza_prima,
    p.fecha_inicio AS poliza_fecha_inicio,
    p.fecha_fin AS poliza_fecha_fin,
    s.fecha_ocurrencia AS siniestro_fecha_ocurrencia,
    s.dias_desde_inicio_poliza AS dias_desde_inicio,
    s.dias_desde_fin_poliza AS dias_hasta_fin,
    pp.senial AS descripcion_alerta,
    pp.puntaje AS total_puntaje_riesgo
FROM 
    public."POLIZA_PUNTAJE" pp
JOIN 
    public."SINIESTRO" s ON pp.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
JOIN 
    public."PUNTAJE" pun ON pp.id_puntaje = pun.id
WHERE 
    pun.codigo = 'A'
ORDER BY 
    pp.puntaje DESC, 
    LEAST(s.dias_desde_inicio_poliza, s.dias_desde_fin_poliza) ASC;
```

---

### Q27. ¿Qué patrones se repiten en los reclamos sospechosos (SINIESTRO.cobertura, id_beneficiario)? (POLIZA_PUNTAJE)
*   **Lógica**: Muestra la concurrencia de siniestros sospechosos agrupando por ramo, tipo de cobertura y taller/proveedor, totalizando las primas comerciales de la cartera.
```sql
SELECT 
    s.ramo AS siniestro_ramo,
    s.cobertura AS siniestro_cobertura,
    bp.nombre AS proveedor_nombre,
    COUNT(DISTINCT s.id) AS cantidad_siniestros,
    SUM(s.monto_estimado) AS total_monto_estimado,
    SUM(s.monto_reclamado) AS total_monto_reclamado,
    SUM(p.prima) AS total_poliza_prima,
    SUM(pp.puntaje) AS total_puntaje_riesgo,
    STRING_AGG(DISTINCT a.nombre || ' ' || a.apellido, ', ') AS asegurado_nombre
FROM 
    public."POLIZA_PUNTAJE" pp
JOIN 
    public."SINIESTRO" s ON pp.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
LEFT JOIN 
    public."BENEFICIARIO_PROVEEDOR" bp ON s.id_beneficiario = bp.id
GROUP BY 
    s.ramo, s.cobertura, bp.nombre
ORDER BY 
    total_puntaje_riesgo DESC, 
    cantidad_siniestros DESC;
```

---

### Q28. Genera un resumen ejecutivo de los casos críticos (SCORING_RIESGO.rango_desde y rango_hasta). (POLIZA_PUNTAJE)
*   **Lógica**: Totaliza los siniestros reportados, montos estimados, montos reclamados y primas agregados según las franjas de clasificación de riesgo definidas en `SCORE_RIESGO`.
```sql
WITH puntajes_totales AS (
    SELECT 
        id_siniestro,
        SUM(puntaje) AS total_puntaje
    FROM 
        public."POLIZA_PUNTAJE"
    GROUP BY 
        id_siniestro
),
siniestros_clasificados AS (
    SELECT 
        pt.id_siniestro,
        pt.total_puntaje,
        sr.nivel,
        sr.accion_sugerida
    FROM 
        puntajes_totales pt
    JOIN 
        public."SCORE_RIESGO" sr ON pt.total_puntaje >= sr.rango_desde 
                                AND pt.total_puntaje <= sr.rango_hasta
)
SELECT 
    sc.nivel AS nivel_riesgo,
    COUNT(DISTINCT s.id) AS cantidad_siniestros,
    SUM(s.monto_estimado) AS total_monto_estimado,
    SUM(s.monto_reclamado) AS total_monto_reclamado,
    SUM(p.prima) AS total_poliza_prima,
    SUM(sc.total_puntaje) AS total_puntaje_riesgo,
    STRING_AGG(DISTINCT a.nombre || ' ' || a.apellido, ', ') AS asegurado_nombre,
    sc.accion_sugerida AS accion_operativa
FROM 
    siniestros_clasificados sc
JOIN 
    public."SINIESTRO" s ON sc.id_siniestro = s.id
JOIN 
    public."POLIZA" p ON s.id_poliza = p.id
JOIN 
    public."ASEGURADO" a ON p.id_asegurado = a.id
GROUP BY 
    sc.nivel, sc.accion_sugerida
ORDER BY 
    total_monto_reclamado DESC;
```

---

### Q29. Recomienda qué casos debería revisar primero el analista. (POLIZA_PUNTAJE)
*   **Lógica**: Consulta y ordena las pólizas clasificadas por la vista `vPoliza_Clasificacion_Riesgo` incorporando los montos agregados por póliza, priorizando semáforos Amarillo y Rojo.
```sql
SELECT 
    vcr.poliza_id,
    vcr.poliza_ramo,
    vcr.poliza_estado,
    vcr.asegurado_nombre,
    1 AS cantidad_siniestros,
    SUM(s.monto_estimado) AS total_monto_estimado,
    SUM(s.monto_reclamado) AS total_monto_reclamado,
    SUM(p.prima) AS total_poliza_prima,
    vcr.total_puntaje AS total_puntaje_riesgo,
    vcr.riesgo_nivel,
    vcr.riesgo_accion_sugerida AS recomendacion_auditoria
FROM 
    public."vPoliza_Clasificacion_Riesgo" vcr
JOIN 
    public."POLIZA" p ON vcr.poliza_id = p.id
JOIN 
    public."SINIESTRO" s ON s.id_poliza = p.id
GROUP BY 
    vcr.poliza_id,
    vcr.poliza_ramo,
    vcr.poliza_estado,
    vcr.asegurado_nombre,
    vcr.total_puntaje,
    vcr.riesgo_nivel,
    vcr.riesgo_accion_sugerida
ORDER BY 
    total_puntaje_riesgo DESC, 
    poliza_id ASC;
```

---
