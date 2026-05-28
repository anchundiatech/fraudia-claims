"""
test_rules.py — Tests del motor de reglas de fraude.
Ejecutar: pytest tests/test_rules.py -v
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rules.fraud_rules import MotorReglasFraude, ResultadoScore


motor = MotorReglasFraude()


def siniestro_limpio():
    """Siniestro sin ninguna señal de riesgo."""
    return {
        "id_siniestro": "TEST-001",
        "cobertura": "choque",
        "dias_desde_inicio_poliza": 200,
        "horas_entre_ocurrencia_reporte": 10,
        "historial_siniestros_asegurado": 0,
        "historial_siniestros_vehiculo": 0,
        "historial_siniestros_conductor": 0,
        "eventos_previos_solo_rc": 0,
        "proveedor_lista_restrictiva": False,
        "casos_observados_proveedor": 0,
        "documentos_completos": True,
        "relato_inconsistente": False,
        "accidente_multiple_madrugada": False,
        "sin_tercero_identificado": False,
        "dano_severo": False,
        "inconsistencia_documental": False,
        "dias_entre_ocurrencia_reporte": 1,
        "similitud_narrativa_max": 0.0,
        "porcentaje_suma_asegurada": 0.3,
    }


def test_siniestro_limpio_verde():
    r = motor.evaluar(siniestro_limpio())
    assert r.nivel_riesgo == "VERDE"
    assert r.score <= 40
    assert len(r.alertas) == 0


def test_reclamo_borde_vigencia_rojo():
    s = siniestro_limpio()
    s["dias_desde_inicio_poliza"] = 5
    r = motor.evaluar(s)
    codigos = [a.codigo for a in r.alertas]
    assert "S01" in codigos
    assert any(a.puntos == 8 for a in r.alertas if a.codigo == "S01")


def test_reclamo_borde_vigencia_amarillo():
    s = siniestro_limpio()
    s["dias_desde_inicio_poliza"] = 20
    r = motor.evaluar(s)
    s01 = [a for a in r.alertas if a.codigo == "S01"]
    assert len(s01) == 1
    assert s01[0].puntos == 4


def test_demora_robo_rojo():
    s = siniestro_limpio()
    s["cobertura"] = "Robo total"
    s["horas_entre_ocurrencia_reporte"] = 72
    r = motor.evaluar(s)
    assert any(a.codigo == "S02" and a.puntos == 8 for a in r.alertas)


def test_proveedor_lista_restrictiva():
    s = siniestro_limpio()
    s["proveedor_lista_restrictiva"] = True
    r = motor.evaluar(s)
    assert any(a.codigo == "S07" and a.puntos == 10 for a in r.alertas)


def test_inconsistencia_documental_sube_score():
    s = siniestro_limpio()
    s["inconsistencia_documental"] = True
    r = motor.evaluar(s)
    assert any(a.codigo == "S11" for a in r.alertas)
    assert r.score > 0


def test_multiples_señales_nivel_rojo():
    s = siniestro_limpio()
    s["dias_desde_inicio_poliza"] = 3          # +8
    s["historial_siniestros_asegurado"] = 4    # +8
    s["proveedor_lista_restrictiva"] = True    # +10
    s["inconsistencia_documental"] = True      # +10
    s["documentos_completos"] = False          # +4
    r = motor.evaluar(s)
    assert r.nivel_riesgo == "ROJO"
    assert r.score >= 76


def test_regla_critica_rf03_fuerza_rojo():
    s = siniestro_limpio()
    s["rf03_lista_restrictiva"] = True
    r = motor.evaluar(s)
    assert r.nivel_riesgo == "ROJO"
    assert r.score >= 76


def test_narrativa_clonada():
    s = siniestro_limpio()
    s["similitud_narrativa_max"] = 0.91
    r = motor.evaluar(s)
    assert any(a.codigo == "S13" and a.puntos == 8 for a in r.alertas)


def test_score_no_supera_100():
    """El score nunca debe superar 100 aunque las señales sumen más."""
    s = siniestro_limpio()
    # Activar todas las señales posibles
    s.update({
        "dias_desde_inicio_poliza": 3,
        "cobertura": "robo",
        "horas_entre_ocurrencia_reporte": 100,
        "historial_siniestros_asegurado": 5,
        "historial_siniestros_vehiculo": 4,
        "historial_siniestros_conductor": 4,
        "eventos_previos_solo_rc": 3,
        "proveedor_lista_restrictiva": True,
        "documentos_completos": False,
        "relato_inconsistente": True,
        "inconsistencia_documental": True,
        "dias_entre_ocurrencia_reporte": 10,
        "similitud_narrativa_max": 0.95,
        "porcentaje_suma_asegurada": 0.99,
    })
    r = motor.evaluar(s)
    assert r.score <= 100
