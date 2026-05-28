import random
import csv
import uuid
from pathlib import Path
from datetime import datetime, timedelta

RAMOS = ["Autos", "Vida", "Daños", "RC", "Combinado"]
COBERTURAS_AUTOS = ["Robo", "Choque", "Incendio", "Pérdida Total", "RC"]
COBERTURAS_VIDA = ["Muerte", "Invalidez"]
COBERTURAS_DANOS = ["Incendio", "Daño", "Robo"]
COBERTURAS_RC = ["RC Civil"]
COBERTURAS_COMBINADO = ["Completa", "Limitada"]
ESTADOS = ["Pendiente", "En revisión", "Pagado", "Rechazado"]
SUCURSALES = ["Norte", "Sur", "Este", "Oeste", "Centro", "Santiago", "Valparaíso", "Concepción"]
DINAMICAS = ["Frontal", "Posterior", "Volcadura", "Múltiple", "Choque lateral", "Atropello"]

BENEFICIARIOS = [
    "Taller El Rápido SPA", "Mecánica Express Ltda", "ServiAuto Chile",
    "Clínica Los Andes", "Hospital Central", "Funeraria Santa María",
    "Buenos Vecinos S.A.", "Transportes del Sur", "Peritos Asociados",
    "Evaluadores Chilenos", "Taller El Amigo", "Recambios Nacionales",
    "Grupo Asegurador Premium", "Consultores de Seguros", "Laboratorio Médico",
]


def generar_siniestro(idx: int) -> dict:
    id_siniestro = f"SN-{idx:06d}"
    ramo = random.choice(RAMOS)

    if ramo == "Autos":
        cobertura = random.choice(COBERTURAS_AUTOS)
    elif ramo == "Vida":
        cobertura = random.choice(COBERTURAS_VIDA)
    elif ramo == "Daños":
        cobertura = random.choice(COBERTURAS_DANOS)
    elif ramo == "RC":
        cobertura = random.choice(COBERTURAS_RC)
    else:
        cobertura = random.choice(COBERTURAS_COMBINADO)

    estado = random.choice(ESTADOS)
    sucursal = random.choice(SUCURSALES)

    fecha_inicio_poliza = datetime.now() - timedelta(days=random.randint(30, 730))
    dias_desde_inicio = random.choices(
        [random.randint(1, 15), random.randint(15, 90), random.randint(90, 365)],
        weights=[3, 3, 4],
    )[0]
    fecha_ocurrencia = fecha_inicio_poliza + timedelta(days=dias_desde_inicio)

    horas_reporte = random.choices(
        [random.randint(1, 12), random.randint(12, 48), random.randint(48, 120)],
        weights=[5, 3, 2],
    )[0]
    fecha_reporte = fecha_ocurrencia + timedelta(hours=horas_reporte)

    monto_reclamado = round(random.uniform(50_000, 15_000_000), 0)

    hist_asegurado = random.choices([0, 1, 2, 3, 4], weights=[6, 2, 1, 0.5, 0.5])[0]
    hist_vehiculo = random.choices([0, 1, 2, 3], weights=[7, 2, 0.5, 0.5])[0]
    hist_conductor = random.choices([0, 1, 2, 3], weights=[7, 2, 0.5, 0.5])[0]
    eventos_rc = random.choices([0, 1, 2, 3], weights=[8, 1, 0.5, 0.5])[0]

    en_lista_restrictiva = random.random() < 0.02
    casos_proveedor = random.choices([0, 1, 2, 3, 4, 5], weights=[8, 1, 0.5, 0.3, 0.1, 0.1])[0]
    docs_completos = random.random() < 0.95

    dinamica = random.choice(DINAMICAS)
    relato_inconsistente = random.random() < 0.03
    accidente_madrugada = random.random() < 0.04

    sin_tercero = random.random() < 0.15
    dano_severo = random.random() < 0.10

    inconsistencia_documental = random.random() < 0.03

    dias_reporte = round((fecha_reporte - fecha_ocurrencia).total_seconds() / 86400, 1)

    similitud_narrativa = random.choices(
        [0.0, round(random.uniform(0.5, 0.69), 2), round(random.uniform(0.7, 0.85), 2), round(random.uniform(0.86, 1.0), 2)],
        weights=[8, 1, 0.5, 0.5],
    )[0]

    suma_asegurada = monto_reclamado * random.uniform(1.0, 2.5)
    porcentaje_suma = round(monto_reclamado / suma_asegurada, 2)

    rf01 = random.random() < 0.01
    rf02 = random.random() < 0.005
    rf03 = random.random() < 0.01
    rf04 = random.random() < 0.005

    beneficiario = random.choice(BENEFICIARIOS)

    return {
        "id_siniestro": id_siniestro,
        "id_poliza": f"POL-{random.randint(10000, 99999)}",
        "id_asegurado": f"ASG-{random.randint(10000, 99999)}",
        "ramo": ramo,
        "cobertura": cobertura,
        "fecha_ocurrencia": fecha_ocurrencia.strftime("%Y-%m-%d"),
        "fecha_reporte": fecha_reporte.strftime("%Y-%m-%d %H:%M"),
        "monto_reclamado": monto_reclamado,
        "suma_asegurada": round(suma_asegurada, 0),
        "porcentaje_suma_asegurada": porcentaje_suma,
        "estado": estado,
        "sucursal": sucursal,
        "beneficiario": beneficiario if beneficiario else "Particular",
        "dias_desde_inicio_poliza": dias_desde_inicio,
        "horas_entre_ocurrencia_reporte": horas_reporte,
        "dias_entre_ocurrencia_reporte": dias_reporte,
        "historial_siniestros_asegurado": hist_asegurado,
        "historial_siniestros_vehiculo": hist_vehiculo,
        "historial_siniestros_conductor": hist_conductor,
        "eventos_previos_solo_rc": eventos_rc,
        "proveedor_lista_restrictiva": en_lista_restrictiva,
        "casos_observados_proveedor": casos_proveedor,
        "documentos_completos": docs_completos,
        "dinamica_accidente": dinamica,
        "relato_inconsistente": relato_inconsistente,
        "accidente_multiple_madrugada": accidente_madrugada,
        "sin_tercero_identificado": sin_tercero,
        "dano_severo": dano_severo,
        "inconsistencia_documental": inconsistencia_documental,
        "similitud_narrativa_max": similitud_narrativa,
        "rf01_perdida_total_robo": rf01,
        "rf02_falsificacion_documental": rf02,
        "rf03_lista_restrictiva": rf03,
        "rf04_dinamica_imposible": rf04,
    }


def generar_dataset(n: int = 500, output_path: str = None):
    if output_path is None:
        output_path = Path(__file__).parent.parent.parent / "data" / "synthetic" / "siniestros.csv"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    siniestros = [generar_siniestro(i) for i in range(1, n + 1)]
    fieldnames = list(siniestros[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(siniestros)

    print(f"Dataset generado: {output_path} ({n} siniestros)")
    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generar dataset sintético de siniestros")
    parser.add_argument("--n", type=int, default=500, help="Número de siniestros (default: 500)")
    parser.add_argument("--output", type=str, default=None, help="Ruta de salida del CSV")
    args = parser.parse_args()
    generar_dataset(args.n, args.output)
