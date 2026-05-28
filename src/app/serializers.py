"""Serialización de filas del DataFrame para la API REST."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from ai_agent.tools_data import alertas_desde_senales
from database.scoring import PUNTAJE_MAX


def _safe_int(val: Any) -> int | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _safe_float(val: Any) -> float | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return round(float(val), 2)
    except (TypeError, ValueError):
        return None


def serializar_siniestro(row: pd.Series, incluir_alertas: bool = False) -> dict:
    """Convierte una fila enriquecida al JSON que consume el frontend."""
    alertas = alertas_desde_senales(row)

    senales = row.get("senales_json", [])
    if isinstance(senales, str):
        try:
            senales = json.loads(senales)
        except json.JSONDecodeError:
            senales = []

    puntaje_total = _safe_float(row.get("puntaje_total"))
    puntaje_senales = _safe_int(row.get("total_puntaje_senales"))
    puntaje_bd = _safe_float(row.get("total_puntaje"))
    asegurado_score = _safe_float(row.get("asegurado_score"))
    score = int(row.get("score", 0))
    nivel = str(row.get("nivel_riesgo", "VERDE"))
    accion = str(row.get("accion_sugerida", "") or "")
    ramo = row.get("ramo") or row.get("poliza_ramo", "")
    sucursal = row.get("sucursal") or row.get("poliza_ciudad") or row.get("asegurado_ciudad", "")

    if puntaje_total is not None:
        resumen = (
            f"Puntaje {puntaje_total:.0f}/{int(PUNTAJE_MAX)} → score {score}/100 ({nivel}). "
            f"Póliza {ramo} en {sucursal}."
        )
    else:
        resumen = f"Score {score}/100 ({nivel}). Póliza {ramo} en {sucursal}."
    if accion:
        resumen += f" {accion}"

    return {
        "id_siniestro": str(row.get("id_siniestro", "")),
        "id_poliza": str(row.get("id_poliza", "")),
        "id_asegurado": str(row.get("id_asegurado") or row.get("asegurado_codigo", "")),
        "ramo": str(ramo),
        "cobertura": str(row.get("cobertura", ramo)),
        "fecha_ocurrencia": str(row.get("fecha_ocurrencia", row.get("poliza_fecha_inicio", ""))),
        "monto_reclamado": _safe_float(row.get("monto_reclamado") or row.get("poliza_suma_asegurada")) or 0,
        "estado": str(row.get("estado", row.get("poliza_estado", ""))),
        "sucursal": str(sucursal),
        "beneficiario": str(row.get("beneficiario") or row.get("_beneficiario", "")),
        "asegurado_nombre": str(row.get("_asegurado_nombre_completo", row.get("asegurado_nombre_completo", ""))),
        "puntaje_total": puntaje_total,
        "puntaje_max": int(PUNTAJE_MAX),
        "score": score,
        "nivel_riesgo": nivel,
        "accion_sugerida": accion,
        "puntaje_senales": puntaje_senales,
        "puntaje_bd": puntaje_bd,
        "asegurado_score": asegurado_score,
        "num_alertas": len(alertas),
        "resumen_ia": resumen,
        "poliza_prima": _safe_float(row.get("poliza_prima")),
        "poliza_deducible": _safe_float(row.get("poliza_deducible")),
        "poliza_canal_venta": row.get("poliza_canal_venta"),
        "asegurado_segmento": row.get("asegurado_segmento"),
        "asegurado_email": row.get("asegurado_email"),
        "senales": senales if isinstance(senales, list) else [],
        **({"alertas": alertas} if incluir_alertas else {}),
    }
