import os
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


def get_client() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("[Supabase] SUPABASE_URL o SUPABASE_KEY no configurados")
        return None
    return create_client(url, key)


def get_table_name() -> str:
    """Vista principal: vPoliza_Puntaje_Total o vPoliza_Asegurado."""
    return os.getenv("DB_TABLE_SINIESTROS", "vPoliza_Puntaje_Total")


def get_table_asegurado() -> str:
    return os.getenv("DB_TABLE_ASEGURADO", "vPoliza_Asegurado")


def get_documento_table() -> str:
    return os.getenv("DB_TABLE_DOCUMENTO", "DOCUMENTO")


def get_poliza_puntaje_table() -> str:
    return os.getenv("DB_TABLE_POLIZA_PUNTAJE", "POLIZA_PUNTAJE")


def get_score_riesgo_table() -> str:
    return os.getenv("DB_TABLE_SCORE_RIESGO", "SCORE_RIESGO")


def leer_siniestros() -> Optional[pd.DataFrame]:
    client = get_client()
    if client is None:
        return None

    table = get_table_name()

    try:
        response = client.table(table).select("*").execute()
        data = response.data
        if not data:
            print(f"[Supabase] La tabla '{table}' está vacía")
            return None
        return pd.DataFrame(data)
    except Exception as e:
        print(f"[Supabase] Error al leer: {e}")
        return None


def guardar_siniestros(df: pd.DataFrame, if_exists: str = "replace") -> bool:
    client = get_client()
    if client is None:
        return False

    table = get_table_name()

    try:
        client.table(table).delete().neq("id_siniestro", "").execute()

        records = df.to_dict("records")
        batch_size = 500
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            client.table(table).insert(batch).execute()
        return True
    except Exception as e:
        print(f"[Supabase] Error al guardar: {e}")
        return False


RANGOS_DEFAULT = [
    {"rango_desde": 16.0, "rango_hasta": 16.9, "nivel": "VERDE", "accion_sugerida": "Revisión estándar — sin indicios de riesgo"},
    {"rango_desde": 17.0, "rango_hasta": 17.9, "nivel": "AMARILLO", "accion_sugerida": "Requiere análisis adicional — pendiente de revisión"},
    {"rango_desde": 18.0, "rango_hasta": 20.0, "nivel": "ROJO", "accion_sugerida": "Requiere investigación prioritaria — posible fraude"},
]

MAPA_SCORE = {16: 40, 17: 60, 18: 76, 19: 88, 20: 100}


def obtener_rangos_score() -> list[dict]:
    """Lee la tabla SCORE_RIESGO. Si está vacía, retorna defaults."""
    client = get_client()
    if client is None:
        return RANGOS_DEFAULT
    try:
        resp = client.table(get_score_riesgo_table()).select("*").order("id").execute()
        if resp.data:
            return resp.data
    except Exception as e:
        print(f"[Supabase] Error al leer SCORE_RIESGO: {e}")
    return RANGOS_DEFAULT


def clasificar_por_rango(puntaje: float, rangos: list[dict]) -> tuple[str, str]:
    """Retorna (nivel, accion_sugerida) según el puntaje y los rangos."""
    for r in rangos:
        if r["rango_desde"] <= puntaje <= r["rango_hasta"]:
            return r["nivel"], r.get("accion_sugerida", "")
    return "VERDE", ""


def score_segun_puntaje(puntaje: int, rangos: list[dict] | None = None) -> int:
    """Mapea puntaje entero 0–20 a score 0–100 (tabla SCORE_RIESGO o MAPA_SCORE)."""
    p = int(max(0, min(puntaje, 20)))
    if rangos:
        for r in rangos:
            desde = int(float(r.get("rango_desde", 0)))
            hasta = int(float(r.get("rango_hasta", 20)))
            if desde <= p <= hasta and r.get("score") is not None:
                return int(r["score"])
    return MAPA_SCORE.get(p, min(p * 5, 100))


def _leer_tabla_completa(table: str, limit: int = 5000) -> Optional[pd.DataFrame]:
    client = get_client()
    if client is None:
        return None
    try:
        resp = client.table(table).select("*").limit(limit).execute()
        if not resp.data:
            return None
        return pd.DataFrame(resp.data)
    except Exception as e:
        print(f"[Supabase] Error al leer {table}: {e}")
        return None


def leer_poliza_puntaje_todos() -> Optional[pd.DataFrame]:
    """Todas las filas de POLIZA_PUNTAJE (señales por siniestro)."""
    return _leer_tabla_completa(get_poliza_puntaje_table())


def leer_documentos_todos() -> Optional[pd.DataFrame]:
    """Todas las filas de DOCUMENTO."""
    return _leer_tabla_completa(get_documento_table())


def leer_poliza_puntaje_por_siniestro(id_siniestro: str) -> Optional[list[dict]]:
    """Señales de POLIZA_PUNTAJE para un id_siniestro."""
    df = leer_poliza_puntaje_todos()
    if df is None or df.empty or "id_siniestro" not in df.columns:
        return leer_poliza_puntaje_por_poliza(id_siniestro)
    matches = df[df["id_siniestro"].astype(str).str.upper() == id_siniestro.upper()]
    if matches.empty:
        return leer_poliza_puntaje_por_poliza(id_siniestro)
    return matches.to_dict("records")


def leer_poliza_puntaje_por_poliza(poliza_id: str) -> Optional[list[dict]]:
    """Señales de POLIZA_PUNTAJE por id_poliza o poliza_id numérico."""
    client = get_client()
    if client is None:
        return None

    table = get_poliza_puntaje_table()
    raw = str(poliza_id).replace("POL-", "").lstrip("0") or "0"
    id_cols = ["id_poliza", "poliza_id", "id_siniestro"]

    for col in id_cols:
        for val in (poliza_id, raw, f"POL-{raw.zfill(6)}"):
            try:
                resp = client.table(table).select("*").eq(col, val).execute()
                if resp.data:
                    return resp.data
            except Exception:
                continue

    df = leer_poliza_puntaje_todos()
    if df is None:
        return None
    for col in id_cols:
        if col in df.columns:
            m = df[df[col].astype(str).isin({str(poliza_id), raw, f"POL-{raw.zfill(6)}"})]
            if not m.empty:
                return m.to_dict("records")
    return None


def leer_documentos_por_siniestro(id_siniestro: str) -> Optional[list[dict]]:
    df = leer_documentos_todos()
    if df is None or df.empty:
        return None
    if "id_siniestro" not in df.columns:
        return None
    matches = df[df["id_siniestro"].astype(str).str.upper() == id_siniestro.upper()]
    return matches.to_dict("records") if not matches.empty else None


def probar_conexion() -> str:
    client = get_client()
    if client is None:
        return "SUPABASE_URL o SUPABASE_KEY no configurados"

    try:
        response = client.table(get_table_name()).select("id_siniestro").limit(1).execute()
        return f"Conexión exitosa — {len(response.data)} registro(s) encontrados"
    except Exception as e:
        return f"Error de conexión: {e}"
