"""
tools_data.py — Carga y normalización según esquema Supabase real.

Tablas/vistas:
  - vPoliza_Puntaje_Total o vPoliza_Asegurado (póliza + asegurado + score)
  - POLIZA_PUNTAJE (señales: senial, puntaje por id_siniestro)
  - DOCUMENTO (entregado, inconsistencia_detectada por id_siniestro)
  - SCORE_RIESGO (rangos opcionales)
"""

from __future__ import annotations

import time
from typing import Any, Optional

import pandas as pd

from database.scoring import PUNTAJE_MAX, calcular_score_nivel, resolver_puntaje_fila
from database.supabase import (
    leer_documentos_todos,
    leer_poliza_puntaje_por_siniestro,
    leer_poliza_puntaje_todos,
    leer_siniestros,
)

_df_cache: Optional[pd.DataFrame] = None
_puntaje_cache: Optional[pd.DataFrame] = None
_docs_cache: Optional[pd.DataFrame] = None
_cache_ts: float = 0
CACHE_TTL_SEC = 60

BENEFICIARIO_COLS = [
    "beneficiario", "proveedor", "proveedor_nombre", "beneficiario_nombre",
]
ASEGURADO_NOMBRE_COMPLETO = ["asegurado_nombre_completo"]
ASEGURADO_NOMBRE_COLS = ["asegurado_nombre", "nombre_asegurado"]
ASEGURADO_APELLIDO_COLS = ["asegurado_apellido", "apellido_asegurado"]
ASEGURADO_ID_COLS = ["asegurado_codigo", "asegurado_id", "id_asegurado"]
CIUDAD_COLS = ["poliza_ciudad", "asegurado_ciudad", "sucursal", "ciudad"]
DIAS_INICIO_COLS = ["dias_desde_inicio_poliza", "dias_inicio_poliza"]
DOCS_COMPLETOS_COLS = ["documentos_completos", "docs_completos"]
MONTO_COLS = ["monto_reclamado", "monto_siniestro"]
SUMA_ASEG_COLS = ["poliza_suma_asegurada", "suma_asegurada"]


def resolver_columna(df: pd.DataFrame, candidatos: list[str], default: Optional[str] = None) -> Optional[str]:
    for col in candidatos:
        if col in df.columns:
            return col
    lower_map = {c.lower(): c for c in df.columns}
    for col in candidatos:
        if col.lower() in lower_map:
            return lower_map[col.lower()]
    return default


def valor_fila(row: pd.Series, candidatos: list[str], default: Any = None) -> Any:
    for col in candidatos:
        if col in row.index and pd.notna(row[col]):
            return row[col]
    return default


def _bool_val(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).lower() in ("true", "1", "si", "sí", "yes")


def col_beneficiario(df: pd.DataFrame) -> str:
    col = resolver_columna(df, BENEFICIARIO_COLS)
    if col:
        return col
    if "_beneficiario" in df.columns:
        return "_beneficiario"
    df["_beneficiario_norm"] = "N/A"
    return "_beneficiario_norm"


def nombre_asegurado(row: pd.Series) -> str:
    completo = valor_fila(row, ASEGURADO_NOMBRE_COMPLETO, None)
    if completo and str(completo).strip():
        return str(completo).strip()
    nombre = str(valor_fila(row, ASEGURADO_NOMBRE_COLS, "") or "").strip()
    apellido = str(valor_fila(row, ASEGURADO_APELLIDO_COLS, "") or "").strip()
    full = f"{nombre} {apellido}".strip()
    return full or str(valor_fila(row, ASEGURADO_ID_COLS, "N/A"))


def _id_siniestro_desde_poliza(poliza_id: Any) -> str:
    return f"POL-{str(poliza_id).replace('POL-', '').zfill(6)}"


def _agregar_poliza_puntaje(df: pd.DataFrame, pp: pd.DataFrame) -> pd.DataFrame:
    """Une señales de POLIZA_PUNTAJE al dataframe principal."""
    if pp is None or pp.empty:
        return df

    pp = pp.copy()
    if "id_siniestro" not in pp.columns and "id_poliza" in pp.columns:
        pp["id_siniestro"] = pp["id_poliza"].apply(
            lambda x: x if str(x).upper().startswith("POL") else _id_siniestro_desde_poliza(x)
        )
    if "id_siniestro" not in pp.columns:
        return df

    def _senales(gr):
        filas = []
        for _, r in gr.iterrows():
            filas.append({
                "senial": str(r.get("senial", "Señal")),
                "puntaje": int(r.get("puntaje", 0)),
                "id_puntaje": r.get("id_puntaje"),
            })
        return filas

    agg = pp.groupby("id_siniestro").apply(
        lambda g: pd.Series({
            "total_puntaje_senales": pd.to_numeric(g["puntaje"], errors="coerce").sum(),
            "senales_json": _senales(g),
        })
    ).reset_index()

    merged = df.merge(agg, on="id_siniestro", how="left")
    if "total_puntaje" not in merged.columns or merged["total_puntaje"].isna().all():
        merged["total_puntaje"] = merged["total_puntaje_senales"]
    else:
        merged["total_puntaje"] = merged["total_puntaje"].fillna(merged["total_puntaje_senales"])
    return merged


def _agregar_documentos(df: pd.DataFrame, docs: pd.DataFrame) -> pd.DataFrame:
    """Une estado documental desde tabla DOCUMENTO."""
    if docs is None or docs.empty or "id_siniestro" not in docs.columns:
        return df

    def _resumen(gr):
        entregado = gr["entregado"] if "entregado" in gr.columns else pd.Series([True] * len(gr))
        todos_entregados = entregado.apply(_bool_val).all()
        inconsistencia = False
        if "inconsistencia_detectada" in gr.columns:
            inconsistencia = gr["inconsistencia_detectada"].apply(_bool_val).any()
        ilegibles = 0
        if "legible" in gr.columns:
            ilegibles = int((~gr["legible"].apply(_bool_val)).sum())
        faltantes = int((~entregado.apply(_bool_val)).sum())
        tipos_faltantes = []
        if faltantes and "tipo_documento" in gr.columns:
            tipos_faltantes = gr[~entregado.apply(_bool_val)]["tipo_documento"].astype(str).tolist()
        return pd.Series({
            "_docs_completos": todos_entregados,
            "_inconsistencia_documental": inconsistencia,
            "_docs_faltantes": faltantes,
            "_docs_ilegibles": ilegibles,
            "_tipos_doc_faltantes": tipos_faltantes,
        })

    doc_agg = docs.groupby("id_siniestro").apply(_resumen).reset_index()
    return df.merge(doc_agg, on="id_siniestro", how="left")


def enriquecer_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "id_siniestro" not in df.columns and "poliza_id" in df.columns:
        df["id_siniestro"] = df["poliza_id"].apply(_id_siniestro_desde_poliza)

    if "poliza_ramo" in df.columns:
        df["ramo"] = df["poliza_ramo"]
    elif "ramo" not in df.columns:
        df["ramo"] = ""
    col_ciudad = resolver_columna(df, CIUDAD_COLS)
    df["sucursal"] = df[col_ciudad].astype(str) if col_ciudad else ""
    df["estado"] = df["poliza_estado"] if "poliza_estado" in df.columns else ""
    df["id_poliza"] = df["id_siniestro"]
    col_aid_early = resolver_columna(df, ASEGURADO_ID_COLS)
    df["id_asegurado"] = df[col_aid_early].astype(str) if col_aid_early else ""
    col_suma = resolver_columna(df, SUMA_ASEG_COLS)
    if col_suma:
        df["monto_reclamado"] = pd.to_numeric(df[col_suma], errors="coerce").fillna(0)

    pp = _puntaje_cache if _puntaje_cache is not None else leer_poliza_puntaje_todos()
    docs = _docs_cache if _docs_cache is not None else leer_documentos_todos()
    df = _agregar_poliza_puntaje(df, pp)
    df = _agregar_documentos(df, docs)

    puntajes_totales, scores, niveles, acciones = [], [], [], []
    for _, row in df.iterrows():
        p_res = resolver_puntaje_fila(row)
        score, nivel, accion = calcular_score_nivel(
            total_puntaje=row.get("total_puntaje"),
            asegurado_score=row.get("asegurado_score"),
            puntaje_resuelto=p_res,
        )
        puntajes_totales.append(p_res)
        scores.append(score)
        niveles.append(nivel)
        acciones.append(accion)

    df["puntaje_total"] = puntajes_totales
    df["score"] = scores
    df["nivel_riesgo"] = niveles
    df["accion_sugerida"] = acciones

    df["_asegurado_nombre_completo"] = df.apply(nombre_asegurado, axis=1)
    col_aid = resolver_columna(df, ASEGURADO_ID_COLS)
    df["_asegurado_id"] = df[col_aid].astype(str) if col_aid else df["_asegurado_nombre_completo"]

    col_ben = resolver_columna(df, BENEFICIARIO_COLS)
    if col_ben:
        df["_beneficiario"] = df[col_ben].astype(str).str.strip()
    else:
        df["_beneficiario"] = "N/A"

    if "_docs_completos" not in df.columns:
        col_docs = resolver_columna(df, DOCS_COMPLETOS_COLS)
        if col_docs:
            df["_docs_completos"] = df[col_docs].apply(_bool_val)
        else:
            df["_docs_completos"] = True

    col_dias = resolver_columna(df, DIAS_INICIO_COLS)
    df["_dias_inicio_poliza"] = (
        pd.to_numeric(df[col_dias], errors="coerce").fillna(9999) if col_dias else 9999
    )

    col_monto = resolver_columna(df, MONTO_COLS)
    col_suma = resolver_columna(df, SUMA_ASEG_COLS)
    if col_monto and col_suma:
        m = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
        s = pd.to_numeric(df[col_suma], errors="coerce").replace(0, pd.NA)
        df["_pct_suma"] = (m / s).fillna(0)
    else:
        df["_pct_suma"] = 0.0

    df["beneficiario"] = df["_beneficiario"]
    return df


def invalidar_cache() -> None:
    global _df_cache, _puntaje_cache, _docs_cache, _cache_ts
    _df_cache = None
    _puntaje_cache = None
    _docs_cache = None
    _cache_ts = 0


def cargar_df(force: bool = False) -> Optional[pd.DataFrame]:
    global _df_cache, _puntaje_cache, _docs_cache, _cache_ts

    if not force and _df_cache is not None and (time.time() - _cache_ts) < CACHE_TTL_SEC:
        return _df_cache

    raw = leer_siniestros()
    if raw is None or raw.empty:
        return None

    _puntaje_cache = leer_poliza_puntaje_todos()
    _docs_cache = leer_documentos_todos()

    _df_cache = enriquecer_df(raw)
    _cache_ts = time.time()
    return _df_cache


def buscar_siniestro(df: pd.DataFrame, id_siniestro: str) -> Optional[pd.Series]:
    matches = df[df["id_siniestro"].astype(str).str.upper() == id_siniestro.upper()]
    return matches.iloc[0] if not matches.empty else None


def alertas_desde_senales(row: pd.Series) -> list[dict]:
    """Alertas desde POLIZA_PUNTAJE (campo senial) o fallback por score."""
    senales = row.get("senales_json")
    if isinstance(senales, list) and senales:
        alertas = []
        for s in senales:
            puntos = int(s.get("puntaje", 0))
            nivel = "ROJO" if puntos >= 8 else ("AMARILLO" if puntos >= 4 else "INFO")
            alertas.append({
                "codigo": str(s.get("senial", "SN"))[:20],
                "descripcion": str(s.get("senial", "Señal de riesgo")),
                "puntos": puntos,
                "nivel": nivel,
            })
        return alertas

    if row.get("_inconsistencia_documental"):
        return [{
            "codigo": "S11",
            "descripcion": "Inconsistencia detectada en documentos del siniestro",
            "puntos": 10,
            "nivel": "ROJO",
        }]

    if not row.get("_docs_completos", True):
        tipos = row.get("_tipos_doc_faltantes", [])
        desc = "Documentos incompletos o no entregados"
        if isinstance(tipos, list) and tipos:
            desc += f": {', '.join(tipos[:5])}"
        return [{
            "codigo": "S08",
            "descripcion": desc,
            "puntos": 4,
            "nivel": "AMARILLO",
        }]

    nivel = row.get("nivel_riesgo", "VERDE")
    score = int(row.get("score", 0))
    puntaje = row.get("puntaje_total")
    if puntaje is not None and not (isinstance(puntaje, float) and pd.isna(puntaje)):
        return [{
            "codigo": "PT",
            "descripcion": f"Puntaje total {float(puntaje):.0f}/{int(PUNTAJE_MAX)} — {nivel} (SCORE_RIESGO)",
            "puntos": int(round(float(puntaje))),
            "nivel": nivel,
        }]
    if nivel == "VERDE":
        return []
    return [{
        "codigo": "SCORE",
        "descripcion": f"Score {score}/100 — {nivel}",
        "puntos": score,
        "nivel": nivel,
    }]


def detalle_puntaje_poliza(poliza_id: Any) -> Optional[list[dict]]:
    sid = poliza_id if str(poliza_id).upper().startswith("POL") else _id_siniestro_desde_poliza(poliza_id)
    return leer_poliza_puntaje_por_siniestro(sid)


def detalle_documentos_siniestro(id_siniestro: str) -> Optional[list[dict]]:
    from database.supabase import leer_documentos_por_siniestro
    return leer_documentos_por_siniestro(id_siniestro)


def senales_proveedor_df(pp: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Filas de POLIZA_PUNTAJE relacionadas con proveedor/beneficiario."""
    pp = pp if pp is not None else leer_poliza_puntaje_todos()
    if pp is None or pp.empty or "senial" not in pp.columns:
        return pd.DataFrame()
    mask = pp["senial"].astype(str).str.lower().str.contains(
        r"proveedor|beneficiario|restrictiva|s07|s-07", regex=True, na=False
    )
    return pp[mask]
