"""
scoring.py — Puntaje 0–100 y semáforo.
"""

from __future__ import annotations
from typing import Any, Optional
import pandas as pd

# CAMBIO CRUCIAL: El máximo ahora es 100
PUNTAJE_MAX = 100.0

def nivel_desde_score_100(score: float) -> str:
    """Semáforo según requerimiento: 0-40 Verde, 41-75 Amarillo, 76-100 Rojo."""
    try:
        s = float(score)
    except (ValueError, TypeError):
        return "VERDE"
        
    if s <= 40:
        return "VERDE"
    if s <= 75:
        return "AMARILLO"
    return "ROJO"

def resolver_puntaje_fila(row: Any) -> Optional[float]:
    """Obtiene total_puntaje de la fila (0-100)."""
    tp = None
    if isinstance(row, pd.Series):
        tp = row.get("total_puntaje")
    elif isinstance(row, dict):
        tp = row.get("total_puntaje")
    
    if tp is not None and pd.notna(tp):
        # Retornamos el valor real de la tabla (ej: 20)
        return float(tp)
    return None

def calcular_score_nivel(
    total_puntaje: float | None = None,
    asegurado_score: float | None = None,
    puntaje_resuelto: float | None = None,
) -> tuple[int, str, str]:
    """Retorna (score 0–100, nivel, accion_sugerida)."""
    # Usamos el puntaje de la tabla directamente
    score_val = 0
    if puntaje_resuelto is not None:
        score_val = puntaje_resuelto
    elif total_puntaje is not None:
        score_val = total_puntaje
    elif asegurado_score is not None:
        score_val = asegurado_score

    score = int(max(0, min(float(score_val), PUNTAJE_MAX)))
    nivel = nivel_desde_score_100(score)
    
    accion = ""
    if nivel == "ROJO":
        accion = "Revisión inmediata por Unidad Antifraude"
    elif nivel == "AMARILLO":
        accion = "Auditoría documental requerida"
        
    return score, nivel, accion

def enriquecer_fila_score(row: pd.Series) -> pd.Series:
    """Añade score y nivel a una fila."""
    tp = resolver_puntaje_fila(row)
    score, nivel, accion = calcular_score_nivel(total_puntaje=tp)
    
    row = row.copy()
    row["score"] = score
    row["nivel_riesgo"] = nivel
    row["accion_sugerida"] = accion
    row["puntaje_total"] = tp
    return row
