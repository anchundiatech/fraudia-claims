"""
fraud_rules.py — Motor de reglas de negocio para detección de posibles fraudes.

Implementa las 12 señales + 7 reglas críticas definidas en el reto
Aseguradora del Sur (hackIAthon 2026).

IMPORTANTE: Este módulo genera alertas de revisión, no acusaciones de fraude.
"""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd


# ──────────────────────────────────────────────
# Modelos de datos
# ──────────────────────────────────────────────

@dataclass
class Alerta:
    codigo: str
    descripcion: str
    puntos: int
    nivel: str  # "ROJO" | "AMARILLO" | "INFO"


@dataclass
class ResultadoScore:
    id_siniestro: str
    score: int                        # 0–100
    nivel_riesgo: str                 # "VERDE" | "AMARILLO" | "ROJO"
    alertas: list[Alerta] = field(default_factory=list)
    resumen: str = ""

    @property
    def color_semaforo(self) -> str:
        return {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}.get(self.nivel_riesgo, "⚪")


# ──────────────────────────────────────────────
# Motor de reglas
# ──────────────────────────────────────────────

class MotorReglasFraude:
    """
    Evalúa un siniestro contra las señales de riesgo definidas en el reto
    y calcula un score ponderado de 0 a 100.
    """

    SCORE_MAX_VERDE = 40
    SCORE_MAX_AMARILLO = 75
    SCORE_MAX_ROJO = 100
    def evaluar(self, siniestro: dict) -> ResultadoScore:
        alertas: list[Alerta] = []
        puntos_total = 0
            fraudia-claims
        # ── SEÑAL 1: Reclamo cercano al borde de vigencia ─────────────────
        dias_inicio = siniestro.get("dias_desde_inicio_poliza", 9999)
        if dias_inicio <= 10:
            a = Alerta("S01", f"Siniestro a {dias_inicio} días del inicio de póliza (≤10 días)", 8, "ROJO")
            alertas.append(a); puntos_total += 8
        elif dias_inicio <= 30:
            a = Alerta("S01", f"Siniestro a {dias_inicio} días del inicio de póliza (11–30 días)", 4, "AMARILLO")
            alertas.append(a); puntos_total += 4

        # ── SEÑAL 2: Demora en denuncia de robo ───────────────────────────
        cobertura = str(siniestro.get("cobertura", "")).lower()
        horas_reporte = siniestro.get("horas_entre_ocurrencia_reporte", 0)
        if "robo" in cobertura:
            if horas_reporte > 48:
                a = Alerta("S02", f"Denuncia de robo con {horas_reporte:.0f}h de demora (>48h)", 8, "ROJO")
                alertas.append(a); puntos_total += 8
            elif horas_reporte >= 24:
                a = Alerta("S02", f"Denuncia de robo con {horas_reporte:.0f}h de demora (24–48h)", 4, "AMARILLO")
                alertas.append(a); puntos_total += 4

        # ── SEÑAL 3: Alta frecuencia de reclamos — asegurado ──────────────
        hist = siniestro.get("historial_siniestros_asegurado", 0)
        if hist >= 3:
            a = Alerta("S03", f"Asegurado con {hist} siniestros previos en ≤18 meses", 8, "ROJO")
            alertas.append(a); puntos_total += 8
        elif hist == 2:
            a = Alerta("S03", f"Asegurado con {hist} siniestros previos en ≤18 meses", 4, "AMARILLO")
            alertas.append(a); puntos_total += 4

        # ── SEÑAL 4: Alta frecuencia — vehículo ───────────────────────────
        hist_vehiculo = siniestro.get("historial_siniestros_vehiculo", 0)
        if hist_vehiculo >= 3:
            a = Alerta("S04", f"Vehículo con {hist_vehiculo} siniestros en ≤18 meses", 6, "ROJO")
            alertas.append(a); puntos_total += 6
        elif hist_vehiculo == 2:
            a = Alerta("S04", f"Vehículo con {hist_vehiculo} siniestros en ≤18 meses", 3, "AMARILLO")
            alertas.append(a); puntos_total += 3

        # ── SEÑAL 5: Alta frecuencia — conductor ──────────────────────────
        hist_conductor = siniestro.get("historial_siniestros_conductor", 0)
        if hist_conductor >= 3:
            a = Alerta("S05", f"Conductor presente en {hist_conductor} siniestros en ≤18 meses", 8, "ROJO")
            alertas.append(a); puntos_total += 8
        elif hist_conductor == 2:
            a = Alerta("S05", f"Conductor presente en {hist_conductor} siniestros en ≤18 meses", 4, "AMARILLO")
            alertas.append(a); puntos_total += 4

        # ── SEÑAL 6: Alta frecuencia reclamos solo RC ─────────────────────
        eventos_rc = siniestro.get("eventos_previos_solo_rc", 0)
        if eventos_rc > 2:
            a = Alerta("S06", f"Frecuencia atípica de RC: {eventos_rc} eventos previos solo RC", 6, "AMARILLO")
            alertas.append(a); puntos_total += 6
        elif eventos_rc == 1:
            a = Alerta("S06", "1 evento previo de solo RC", 3, "AMARILLO")
            alertas.append(a); puntos_total += 3

        # ── SEÑAL 7: Beneficiario / Proveedor recurrente ──────────────────
        en_lista_restrictiva = siniestro.get("proveedor_lista_restrictiva", False)
        casos_proveedor = siniestro.get("casos_observados_proveedor", 0)
        if en_lista_restrictiva:
            a = Alerta("S07", "Proveedor en Lista Restrictiva", 10, "ROJO")
            alertas.append(a); puntos_total += 10
        elif casos_proveedor > 2:
            a = Alerta("S07", f"Proveedor con {casos_proveedor} casos observados este año", 5, "AMARILLO")
            alertas.append(a); puntos_total += 5

        # ── SEÑAL 8: Documentos incompletos ───────────────────────────────
        docs_completos = siniestro.get("documentos_completos", True)
        if not docs_completos:
            a = Alerta("S08", "Faltan documentos legales obligatorios", 4, "AMARILLO")
            alertas.append(a); puntos_total += 4

        # ── SEÑAL 9: Dinámica sospechosa ──────────────────────────────────
        dinamica = str(siniestro.get("dinamica_accidente", "")).lower()
        relato_inconsistente = siniestro.get("relato_inconsistente", False)
        accidente_madrugada = siniestro.get("accidente_multiple_madrugada", False)
        if relato_inconsistente:
            a = Alerta("S09", "Relato inconsistente con tipo de impacto declarado", 6, "ROJO")
            alertas.append(a); puntos_total += 6
        elif accidente_madrugada and any(d in dinamica for d in ["frontal", "posterior", "volcadura", "múltiple"]):
            a = Alerta("S09", "Accidente múltiple en horario de madrugada", 3, "AMARILLO")
            alertas.append(a); puntos_total += 3

        # ── SEÑAL 10: Eventos sin tercero identificado ────────────────────
        sin_tercero = siniestro.get("sin_tercero_identificado", False)
        dano_severo = siniestro.get("dano_severo", False)
        if sin_tercero and dano_severo:
            a = Alerta("S10", "Daño severo sin rastro del tercero ni evidencia en cámaras", 5, "AMARILLO")
            alertas.append(a); puntos_total += 5

        # ── SEÑAL 11: Documentos inconsistentes ───────────────────────────
        inconsistencia = siniestro.get("inconsistencia_documental", False)
        if inconsistencia:
            a = Alerta("S11", "Documentos con fechas o valores inconsistentes / posible alteración", 10, "ROJO")
            alertas.append(a); puntos_total += 10

        # ── SEÑAL 12: Reporte tardío ──────────────────────────────────────
        dias_reporte = siniestro.get("dias_entre_ocurrencia_reporte", 0)
        if dias_reporte > 7:
            a = Alerta("S12", f"Siniestro reportado con {dias_reporte} días de demora (>7 días)", 5, "AMARILLO")
            alertas.append(a); puntos_total += 5
        elif dias_reporte >= 4:
            a = Alerta("S12", f"Siniestro reportado con {dias_reporte} días de demora (4–7 días)", 3, "AMARILLO")
            alertas.append(a); puntos_total += 3

        # ── SEÑAL 13: Narrativas similares (NLP externo, flag pre-calculado)
        similitud = siniestro.get("similitud_narrativa_max", 0.0)
        if similitud > 0.85:
            a = Alerta("S13", f"Narrativa con {similitud:.0%} de similitud con otro reclamo (posible clon)", 8, "ROJO")
            alertas.append(a); puntos_total += 8
        elif similitud >= 0.70:
            a = Alerta("S13", f"Narrativa con {similitud:.0%} de similitud con otro reclamo", 4, "AMARILLO")
            alertas.append(a); puntos_total += 4

        # ── SEÑAL 14: Monto cercano o superior a suma asegurada ───────────
        porcentaje_suma = siniestro.get("porcentaje_suma_asegurada", 0.0)
        if porcentaje_suma >= 0.95:
            a = Alerta("S14", f"Monto reclamado es el {porcentaje_suma:.0%} de la suma asegurada", 4, "AMARILLO")
            alertas.append(a); puntos_total += 4

        # ── REGLAS CRÍTICAS RF-01 a RF-04 (override a ROJO) ───────────────
        if siniestro.get("rf01_perdida_total_robo", False):
            a = Alerta("RF01", "Cobertura Pérdida Total por Robo (PTxRB)", 0, "ROJO")
            alertas.append(a)

        if siniestro.get("rf02_falsificacion_documental", False):
            a = Alerta("RF02", "Evidencia de falsificación o adulteración documental evidente", 0, "ROJO")
            alertas.append(a)

        if siniestro.get("rf03_lista_restrictiva", False):
            a = Alerta("RF03", "Asegurado, beneficiario o APS en Lista Restrictiva", 0, "ROJO")
            alertas.append(a)

        if siniestro.get("rf04_dinamica_imposible", False):
            a = Alerta("RF04", "Dinámica del accidente físicamente imposible", 0, "ROJO")
            alertas.append(a)

        # ── Normalizar score a 0–100 ───────────────────────────────────────
        MAX_PUNTOS_POSIBLES = 100
        score = min(int((puntos_total / MAX_PUNTOS_POSIBLES) * 100), 100)

        # Si hay una regla ROJO crítica, score mínimo 76
        tiene_rojo_critico = any(a.nivel == "ROJO" and a.codigo.startswith("RF") for a in alertas)
        if tiene_rojo_critico:
            score = max(score, 76)

        # Nivel de riesgo
        if score <= self.SCORE_MAX_VERDE:
            nivel = "VERDE"
        elif score <= self.SCORE_MAX_AMARILLO:
            nivel = "AMARILLO"
        else:
            nivel = "ROJO"

        # Resumen textual
        if alertas:
            tops = sorted(alertas, key=lambda a: a.puntos, reverse=True)[:3]
            motivos = "; ".join(a.descripcion for a in tops)
            resumen = f"Score {score}/100 ({nivel}). Principales señales: {motivos}."
        else:
            resumen = f"Score {score}/100. Sin señales de riesgo detectadas."

        return ResultadoScore(
            id_siniestro=str(siniestro.get("id_siniestro", "")),
            score=score,
            nivel_riesgo=nivel,
            alertas=alertas,
            resumen=resumen,
        )

    def evaluar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Evalúa todos los siniestros de un DataFrame y retorna el DF enriquecido."""
        resultados = [self.evaluar(row.to_dict()) for _, row in df.iterrows()]
        df = df.copy()
        df["score"]        = [r.score for r in resultados]
        df["nivel_riesgo"] = [r.nivel_riesgo for r in resultados]
        df["num_alertas"]  = [len(r.alertas) for r in resultados]
        df["resumen_ia"]   = [r.resumen for r in resultados]
        df["alertas_json"] = [
            [{"codigo": a.codigo, "descripcion": a.descripcion, "puntos": a.puntos, "nivel": a.nivel}
             for a in r.alertas]
            for r in resultados
        ]
        return df
