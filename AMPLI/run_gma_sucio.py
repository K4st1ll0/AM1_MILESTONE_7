import subprocess
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# === RUTAS IMPORTANTES ===
GMAT_BIN = Path(r"C:\Users\belen\Downloads\gmat-win-R2025a\GMAT_R2025a\bin")
GMAT_EXE = GMAT_BIN / "GmatConsole.exe"   # ahora usamos la versión de consola

BASE_DIR = Path(r"C:\Users\belen\OneDrive\Desktop\AMPLI")
SCRIPT_PATH = BASE_DIR / "demo.script"
REPORT_PATH = BASE_DIR / "DefaultReportFile.txt"


def run_gmat():
    print(f"Voy a lanzar GMAT con el script: {SCRIPT_PATH}")
    print(f"Ejecutable: {GMAT_EXE}")

    # Esto es lo mismo que has probado a mano:
    # GmatConsole.exe --run "C:\...\demo.script"
    result = subprocess.run(
        [str(GMAT_EXE), "--run", str(SCRIPT_PATH)],
        check=True,
        cwd=str(GMAT_BIN),   # muy importante: se ejecuta desde la carpeta bin
        text=True,
    )

    print("GmatConsole ha terminado.")


def read_and_plot_report():
    if not REPORT_PATH.exists():
        raise FileNotFoundError(f"No se encuentra {REPORT_PATH}")

    # Leemos el report (separado por espacios)
    df = pd.read_csv(REPORT_PATH, sep=r"\s+")
    # Forzamos a numérico y quitamos filas raras (cabeceras duplicadas, etc.)
    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    print("Columnas en el ReportFile:")
    print(df.columns)
    print("\nPrimeras filas:")
    print(df.head())

    cols = list(df.columns)
    time_col = cols[0]
    x_col = cols[1]
    y_col = cols[2]

    plt.figure()
    plt.plot(df[x_col], df[y_col])
    plt.xlabel(f"{x_col} (km)")
    plt.ylabel(f"{y_col} (km)")
    plt.title("Órbita en plano XY")
    plt.axis("equal")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    run_gmat()
    read_and_plot_report()
