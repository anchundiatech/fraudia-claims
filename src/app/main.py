"""
main.py — FastAPI entry point para Fraudia Claims.
hackIAthon 2026 — Reto Aseguradora del Sur.
"""

import os
import json
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.supabase import probar_conexion, obtener_rangos_score
from database.scoring import PUNTAJE_MAX
from ai_agent.tools_data import cargar_df, invalidar_cache
from .serializers import serializar_siniestro

app = FastAPI(
    title="Fraudia Claims API",
    description="API de detección de posibles fraudes en siniestros — hackIAthon 2026",
    version="1.0.0",
)

_cors_origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,https://fraudia-claims.vercel.app",
    ).split(",")
    if o.strip()
]
_frontend = os.getenv("FRONTEND_URL", "http://localhost:3000").strip()
if _frontend and _frontend not in _cors_origins:
    _cors_origins.append(_frontend)

# Para producción (Render / Vercel), es mejor permitir todos los orígenes (*) sin credenciales
# para evitar bloqueos por dominios de previsualización de Vercel.
if os.getenv("APP_ENV", "development").lower() != "development" or "*" in _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

_df_cache: Optional[pd.DataFrame] = None


def get_df(force_db: bool = False) -> pd.DataFrame:
    global _df_cache
    if _df_cache is not None and not force_db:
        return _df_cache

    if force_db:
        invalidar_cache()

    df = cargar_df(force=force_db)
    if df is not None and not df.empty:
        _df_cache = df
        return _df_cache

    raise HTTPException(
        status_code=503,
        detail="No se pudieron cargar datos desde Supabase. Verifica la conexión."
    )


class ChatRequest(BaseModel):
    pregunta: str


class ConfigAgenteRequest(BaseModel):
    provider: str
    model: Optional[str] = None


@app.post("/chat/config")
def configurar_agente(req: ConfigAgenteRequest):
    try:
        from ai_agent.agent import actualizar_config_agente, AgenteFraude
        actualizar_config_agente(req.provider, req.model)
        agente = AgenteFraude()
        
        modelo_activo = agente.gemini_model
        if agente.provider == "xai":
            modelo_activo = agente.xai_model
        elif agente.provider == "anthropic":
            modelo_activo = agente.anthropic_model
            
        return {
            "status": "ok",
            "provider": agente.provider,
            "model": modelo_activo,
            "mensaje": f"Configuración del agente actualizada a {agente.provider} ({modelo_activo})"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"mensaje": "Fraudia Claims API activa", "docs": "/docs"}


@app.get("/score-riesgo/rangos")
def rangos_score_riesgo():
    """Rangos de SCORE_RIESGO para el semáforo (puntaje 0–20)."""
    return {"puntaje_max": int(PUNTAJE_MAX), "rangos": obtener_rangos_score()}


@app.get("/siniestros")
def listar_siniestros(
    nivel: Optional[str] = Query(None, description="VERDE | AMARILLO | ROJO"),
    ramo: Optional[str]  = Query(None),
    limit: int           = Query(100, le=500),
    offset: int          = Query(0),
):
    df = get_df()

    if nivel:
        df = df[df["nivel_riesgo"] == nivel.upper()]
    if ramo:
        df = df[df["ramo"].str.lower() == ramo.lower()]

    df_sorted = df.sort_values("score", ascending=False)
    total = len(df_sorted)
    df_page = df_sorted.iloc[offset : offset + limit]

    registros = [serializar_siniestro(row) for _, row in df_page.iterrows()]

    return {"total": total, "offset": offset, "limit": limit, "siniestros": registros}


@app.get("/siniestros/{id_siniestro}")
def detalle_siniestro(id_siniestro: str):
    df = get_df()
    row = df[df["id_siniestro"].astype(str) == id_siniestro]

    if row.empty:
        raise HTTPException(status_code=404, detail=f"Siniestro {id_siniestro} no encontrado")

    return serializar_siniestro(row.iloc[0], incluir_alertas=True)


def _jsonify_counts(series) -> dict:
    """Convierte conteos de pandas a dict JSON-serializable."""
    return {str(k): int(v) for k, v in series.to_dict().items()}


@app.get("/estadisticas")
def estadisticas():
    df = get_df()

    dist_riesgo = {str(k): int(v) for k, v in df["nivel_riesgo"].value_counts().to_dict().items()}

    col_ramo = "ramo" if "ramo" in df.columns else "poliza_ramo"
    col_ciudad = "sucursal" if "sucursal" in df.columns else "poliza_ciudad"
    col_proveedor = "beneficiario" if "beneficiario" in df.columns else "_beneficiario"

    rojos = df[df["nivel_riesgo"] == "ROJO"]
    alertas = df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])]

    top_ramos = _jsonify_counts(rojos.groupby(col_ramo).size().sort_values(ascending=False).head(5))

    prov = alertas[alertas[col_proveedor].astype(str).str.strip() != "N/A"]
    top_proveedores = (
        _jsonify_counts(prov.groupby(col_proveedor).size().sort_values(ascending=False).head(5))
        if not prov.empty and col_proveedor in prov.columns
        else {}
    )

    top_sucursales = _jsonify_counts(
        rojos.groupby(col_ciudad).size().sort_values(ascending=False).head(5)
    ) if col_ciudad in rojos.columns else {}

    return {
        "total_siniestros": len(df),
        "distribucion_riesgo": dist_riesgo,
        "score_promedio": round(float(df["score"].mean()), 1),
        "top_ramos_riesgo": top_ramos,
        "top_proveedores_alertas": top_proveedores,
        "top_sucursales_riesgo": top_sucursales,
        "casos_criticos": int((df["nivel_riesgo"] == "ROJO").sum()),
    }


@app.get("/chat/status")
def chat_status():
    try:
        from ai_agent.agent import AgenteFraude
        agente = AgenteFraude()
        modelo = "gemini-1.5-flash"
        if agente.provider == "xai":
            modelo = agente.xai_model
        elif agente.provider == "anthropic":
            modelo = agente.anthropic_model
        return {
            "status": "ok",
            "modelo": modelo,
            "proveedor": agente.provider,
            "mensaje": f"Agente activo con proveedor {agente.provider}"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/chat")
async def chat_agente(req: ChatRequest):
    try:
        from ai_agent.agent import AgenteFraude
        agente = AgenteFraude()
        respuesta = agente.consultar(req.pregunta)
        return {"respuesta": respuesta}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error del Agente: {str(e)}")


@app.get("/agent/tools")
def agent_tools():
    from ai_agent.tools import TOOLS_DEFINICION
    return {"tools": [t["function"]["name"] for t in TOOLS_DEFINICION]}


@app.get("/db/status")
def db_status():
    return {"status": probar_conexion(), "tabla": os.getenv("DB_TABLE_SINIESTROS", "vPoliza_Puntaje_Total")}


@app.post("/db/recargar")
def db_recargar():
    global _df_cache
    _df_cache = None
    invalidar_cache()
    try:
        df = get_df(force_db=True)
        return {"mensaje": "Datos recargados desde Supabase", "registros": len(df)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al recargar: {e}")


@app.get("/exportar/csv")
def exportar_csv():
    from fastapi.responses import StreamingResponse
    import io

    df = get_df()

    sospechosos = df[
        df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])
    ].sort_values("score", ascending=False)

    cols = [
        "id_siniestro", "ramo", "cobertura", "fecha_ocurrencia",
        "monto_reclamado", "estado", "sucursal", "score",
        "nivel_riesgo", "resumen_ia"
    ]

    output = io.BytesIO()
    csv_data = sospechosos[cols].to_csv(index=False, sep=";")
    output.write(csv_data.encode("utf-8-sig"))
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=casos_sospechosos.csv"}
    )
