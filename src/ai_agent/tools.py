"""
tools.py — Definición de herramientas para Gemini y xAI (Grok).
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
        "ciudades_riesgo": cities_riesgo if 'cities_riesgo' in locals() else ciudades_riesgo,
        "ciudades_riesgo_alias": ciudades_riesgo,
        "recomendar_acciones": recomendar_acciones,
        "asegurados_frecuencia_reclamos": asegurados_frecuencia_reclamos,
        "casos_documentos_incompletos": casos_documentos_incompletos,
        "casos_montos_atipicos": casos_montos_atipicos,
        "siniestros_cerca_inicio_poliza": siniestros_cerca_inicio_poliza,
        "resumen_casos_criticos": resumen_casos_criticos,
        "patrones_sospechosos": patrones_sospechosos,
    }
    # Asegurar mapeo alternativo
    if nombre == "ciudades_riesgo":
        func = ciudades_riesgo
    else:
        func = mapping.get(nombre)
        
    if func:
        return str(func(**args))
    return f"Tool {nombre} no implementada"

# Formato Nativo de Gemini
TOOLS_DEFINICION = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="obtener_top_riesgo",
            description="Obtiene los N siniestros/pólizas con mayor score de riesgo de fraude desde la vista vPoliza_Puntaje_Total.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "n": types.Schema(type=types.Type.INTEGER, description="Cantidad de resultados a retornar. Por defecto 10.")
                }
            )
        ),
        types.FunctionDeclaration(
            name="detalle_siniestro",
            description="Retorna el detalle completo de un siniestro desde vPoliza_Puntaje_Total.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "id_siniestro": types.Schema(type=types.Type.STRING, description="ID del siniestro.")
                },
                required=["id_siniestro"]
            )
        )
    ]
)

# FORMATO OPENAI / xAI COMPATIBLE
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "obtener_top_riesgo",
            "description": "Obtiene los N siniestros/pólizas con mayor score de riesgo de fraude de la base de datos (vPoliza_Puntaje_Total).",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Cantidad de resultados. Por defecto 10."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detalle_siniestro",
            "description": "Retorna el detalle completo de un siniestro por su ID de la vista vPoliza_Puntaje_Total.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_siniestro": {
                        "type": "string",
                        "description": "ID del siniestro. Ejemplo: POL-000005."
                    }
                },
                "required": ["id_siniestro"]
            }
        }
    }
]
