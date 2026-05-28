"""
tools_gemini.py — TOOLS_DEFINICION convertido al formato nativo de google-genai.

Reemplaza el bloque TOOLS_DEFINICION en tools.py por este.
Requiere: google-genai >= 0.8.0
"""

from google.genai import types

def ejecutar_tool(nombre: str, args: dict) -> str:
    """Ejecuta la tool correspondiente y retorna resultado como string."""
    from .tools_data import (
        obtener_top_riesgo,
        detalle_siniestro,
        score_proveedor,
        ramos_sospechosos,
        proveedores_alertas,
        ciudades_riesgo,
        recomendar_acciones,
        asegurados_frecuencia_reclamos,
        casos_documentos_incompletos,
        casos_montos_atipicos,
        siniestros_cerca_inicio_poliza,
        resumen_casos_criticos,
        patrones_sospechosos,
    )
    mapping = {
        "obtener_top_riesgo": obtener_top_riesgo,
        "detalle_siniestro": detalle_siniestro,
        "score_proveedor": score_proveedor,
        "ramos_sospechosos": ramos_sospechosos,
        "proveedores_alertas": proveedores_alertas,
        "ciudades_riesgo": ciudades_riesgo,
        "recomendar_acciones": recomendar_acciones,
        "asegurados_frecuencia_reclamos": asegurados_frecuencia_reclamos,
        "casos_documentos_incompletos": casos_documentos_incompletos,
        "casos_montos_atipicos": casos_montos_atipicos,
        "siniestros_cerca_inicio_poliza": siniestros_cerca_inicio_poliza,
        "resumen_casos_criticos": resumen_casos_criticos,
        "patrones_sospechosos": patrones_sospechosos,
    }
    func = mapping.get(nombre)
    if func:
        return str(func(**args))
    return f"Tool {nombre} no implementada"


TOOLS_DEFINICION = types.Tool(
    function_declarations=[

        # ── Q18 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="obtener_top_riesgo",
            description=(
                "Obtiene los N siniestros/pólizas con mayor score de riesgo de fraude, "
                "ordenados de mayor a menor puntaje."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Cantidad de resultados a retornar. Por defecto 10.",
                    )
                },
            ),
        ),

        # ── Q19 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="detalle_siniestro",
            description=(
                "Retorna el detalle completo de un siniestro por su ID: score, nivel de riesgo, "
                "alertas activas, desglose de señales (POLIZA_PUNTAJE) y estado documental."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "id_siniestro": types.Schema(
                        type=types.Type.STRING,
                        description="ID del siniestro. Formato esperado: POL-000123.",
                    )
                },
                required=["id_siniestro"],
            ),
        ),

        # ── Q20 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="score_proveedor",
            description=(
                "Retorna el score de riesgo y distribución de alertas de un proveedor o "
                "beneficiario (taller mecánico, clínica, perito) buscado por nombre."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "nombre_proveedor": types.Schema(
                        type=types.Type.STRING,
                        description="Nombre o fragmento del nombre del proveedor/beneficiario.",
                    )
                },
                required=["nombre_proveedor"],
            ),
        ),

        # ── Q21 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="ramos_sospechosos",
            description=(
                "Lista los ramos de seguro con mayor porcentaje de casos ROJO y AMARILLO, "
                "incluyendo score promedio y conteo de siniestros sospechosos por ramo."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={},
            ),
        ),

        # ── Q20 por señal ────────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="proveedores_alertas",
            description=(
                "Lista los proveedores o beneficiarios con mayor concentración de alertas "
                "de fraude (casos ROJO y AMARILLO), ordenados por total de alertas."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Cantidad de proveedores a retornar. Por defecto 5.",
                    )
                },
            ),
        ),

        # ── Q22 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="ciudades_riesgo",
            description=(
                "Lista las ciudades o sucursales con mayor concentración de casos críticos "
                "(ROJO), incluyendo score promedio y porcentaje de riesgo por ciudad."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={},
            ),
        ),

        # ── Q29 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="recomendar_acciones",
            description=(
                "Genera recomendaciones operativas de revisión para un siniestro específico "
                "según su nivel de riesgo (ROJO/AMARILLO/VERDE) y alertas activas."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "id_siniestro": types.Schema(
                        type=types.Type.STRING,
                        description="ID del siniestro. Formato esperado: POL-000123.",
                    )
                },
                required=["id_siniestro"],
            ),
        ),

        # ── Q23 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="asegurados_frecuencia_reclamos",
            description=(
                "Lista los asegurados con mayor frecuencia de reclamos o siniestros asociados, "
                "con su score promedio y cantidad de casos ROJO."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Cantidad de asegurados a retornar. Por defecto 10.",
                    )
                },
            ),
        ),

        # ── Q24 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="casos_documentos_incompletos",
            description=(
                "Retorna casos críticos (ROJO/AMARILLO) con documentos faltantes, "
                "no entregados, rechazados o con inconsistencias detectadas."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "solo_criticos": types.Schema(
                        type=types.Type.BOOLEAN,
                        description=(
                            "Si es true, filtra solo casos ROJO y AMARILLO. "
                            "Por defecto true."
                        ),
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Máximo de casos a retornar. Por defecto 20.",
                    ),
                },
            ),
        ),

        # ── Q25 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="casos_montos_atipicos",
            description=(
                "Retorna siniestros con montos reclamados atípicamente altos: "
                "cercanos o superiores a un porcentaje de la suma asegurada."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "umbral_pct": types.Schema(
                        type=types.Type.NUMBER,
                        description=(
                            "Proporción mínima del monto reclamado sobre la suma asegurada "
                            "(0.0 a 1.0). Por defecto 0.95 (95%)."
                        ),
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Cantidad de casos a retornar. Por defecto 20.",
                    ),
                },
            ),
        ),

        # ── Q26 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="siniestros_cerca_inicio_poliza",
            description=(
                "Retorna siniestros ocurridos pocos días después del inicio de la póliza, "
                "señal de posible fraude por borde de vigencia (Señal A)."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "dias_max": types.Schema(
                        type=types.Type.INTEGER,
                        description=(
                            "Días máximos desde el inicio de la póliza para considerar "
                            "el siniestro como sospechoso. Por defecto 30."
                        ),
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Cantidad de casos a retornar. Por defecto 20.",
                    ),
                },
            ),
        ),

        # ── Q28 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="resumen_casos_criticos",
            description=(
                "Genera un resumen ejecutivo de los casos críticos (ROJO) para el analista: "
                "totales por nivel de riesgo, proveedor con más alertas y top casos prioritarios."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Cantidad de casos prioritarios a incluir. Por defecto 10.",
                    )
                },
            ),
        ),

        # ── Q27 equivalente ─────────────────────────────────────────────────
        types.FunctionDeclaration(
            name="patrones_sospechosos",
            description=(
                "Detecta patrones recurrentes en casos de alto riesgo: ramos y proveedores "
                "más frecuentes, documentos incompletos, siniestros cerca del inicio de póliza, "
                "montos atípicos y narrativas similares."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={},
            ),
        ),
    ]
)