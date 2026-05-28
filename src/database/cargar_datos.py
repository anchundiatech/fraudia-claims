import argparse
from pathlib import Path

import pandas as pd

from src.database.supabase import guardar_siniestros, probar_conexion


def cargar_csv_a_supabase(csv_path: str, if_exists: str = "replace"):
    path = Path(csv_path)
    if not path.exists():
        print(f"Archivo no encontrado: {path}")
        return False

    print("Cargando CSV...")
    df = pd.read_csv(path)
    print(f"  {len(df)} registros, {len(df.columns)} columnas")

    print("Conectando a Supabase...")
    conn_status = probar_conexion()
    print(f"  {conn_status}")

    ok = guardar_siniestros(df, if_exists=if_exists)
    if ok:
        print(f"Datos cargados exitosamente a Supabase ({len(df)} registros)")
    else:
        print("Error al cargar datos a Supabase")
    return ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cargar CSV de siniestros a Supabase")
    parser.add_argument("--csv", type=str, default=None,
                        help="Ruta al CSV (default: data/synthetic/siniestros.csv)")
    parser.add_argument("--if-exists", type=str, default="replace",
                        choices=["replace", "append", "fail"],
                        help="Qué hacer si la tabla existe")
    args = parser.parse_args()

    if args.csv is None:
        args.csv = Path(__file__).parent.parent.parent / "data" / "synthetic" / "siniestros.csv"

    cargar_csv_a_supabase(str(args.csv), args.if_exists)
