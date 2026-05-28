"""
scoring.py — Puntaje 0–20 validado contra SCORE_RIESGO → score 0–100 y semáforo.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from database.supabase import clasificar_por_rango, obtener_rangos_score, score_segun_puntaje

PUNTAJE_MAX = 20.0


def nivel_desde_score_100(score: float) -> str:
    """Semáforo alternativo cuando solo hay score 0–100 (sin puntaje 0–20)."""
    if score <= 40:
        return "VERDE"
    if score <= 75:
        return "AMARILLO"
    return "ROJO"


def resolver_puntaje_fila(row: Any) -> Optional[float]:
    """
    Obtiene el puntaje total en escala 0–20.
    Prioridad: suma POLIZA_PUNTAJE → total_puntaje de vista (solo si ≤ 20).
    """
    senales = None
    if isinstance(row, pd.Series):
        senales = row.get("total_puntaje_senales")
        tp = row.get("total_puntaje")
    elif isinstance(row, dict):
        senales = row.get("total_puntaje_senales")
        tp = row.get("total_puntaje")
    else:
        return None

    if senales is not None and not (isinstance(senales, float) and pd.isna(senales)):
        return max(0.0, min(float(senales), PUNTAJE_MAX))

    if tp is not None and not (isinstance(tp, float) and pd.isna(tp)):
        p = float(tp)
        if 0 <= p <= PUNTAJE_MAX:
            return p

    return None


def calcular_desde_puntaje(puntaje: float) -> tuple[int, str, str]:
    """
    Valida puntaje (0–20) contra SCORE_RIESGO.
    Retorna (score 0–100, nivel, accion_sugerida).
    """
    p = max(0.0, min(float(puntaje), PUNTAJE_MAX))
    rangos = obtener_rangos_score()
    nivel, accion = clasificar_por_rango(p, rangos)
    score = score_segun_puntaje(int(round(p)), rangos)
    return int(score), nivel, accion


def calcular_score_nivel(
    total_puntaje: float | None = None,
    asegurado_score: float | None = None,
    puntaje_resuelto: float | None = None,
) -> tuple[int, str, str]:
    """
    Retorna (score 0–100, nivel, accion_sugerida).

    Si hay puntaje 0–20, siempre usa SCORE_RIESGO.
    Si no, usa asegurado_score con escala 0–100 (fallback).
    """
    p = puntaje_resuelto
    if p is None and total_puntaje is not None:
        tp = float(total_puntaje)
        if 0 <= tp <= PUNTAJE_MAX:
            p = tp

    if p is not None:
        return calcular_desde_puntaje(p)

    if asegurado_score is not None and float(asegurado_score) > 0:
        score = int(min(max(float(asegurado_score), 0), 100))
        return score, nivel_desde_score_100(score), ""

    return 0, "VERDE", ""


def enriquecer_fila_score(row: pd.Series) -> pd.Series:
    """Añade score, nivel_riesgo, puntaje_total y accion_sugerida a una fila."""
    puntaje = resolver_puntaje_fila(row)
    score, nivel, accion = calcular_score_nivel(
        total_puntaje=row.get("total_puntaje") if puntaje is None else None,
        asegurado_score=row.get("asegurado_score"),
        puntaje_resuelto=puntaje,
    )
    row = row.copy()
    row["puntaje_total"] = puntaje if puntaje is not None else (
        float(row["total_puntaje"]) if pd.notna(row.get("total_puntaje")) and float(row["total_puntaje"]) <= PUNTAJE_MAX else None
    )
    row["score"] = score
    row["nivel_riesgo"] = nivel
    row["accion_sugerida"] = accion
    return row
