import subprocess
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# === RUTAS IMPORTANTES ===
GMAT_BIN = Path(r"C:\Users\belen\Downloads\gmat-win-R2025a\GMAT_R2025a\bin")
GMAT_EXE = GMAT_BIN / "GmatConsole.exe"

BASE_DIR = Path(r"C:\Users\belen\OneDrive\Desktop\AMPLI")
SCRIPT_PATH = BASE_DIR / "demo.script"
REPORT_PATH = BASE_DIR / "DefaultReportFile.txt"


def generate_script(sma_km=7000.0, vy_kms=7.5, dur_days=1.0):
    """
    Genera demo.script a partir de parámetros sencillos.
    sma_km   : posición inicial X (km)
    vy_kms   : velocidad tangencial inicial (km/s)
    dur_days : tiempo de propagación en días
    """
    script_text = f"""
Create Spacecraft Sat;
Create ForceModel FM;
Create Propagator Prop;
Create ReportFile DefaultReportFile;

Sat.DateFormat = UTCGregorian;
Sat.Epoch = '01 Jan 2030 12:00:00.000';
Sat.CoordinateSystem = EarthMJ2000Eq;
Sat.DisplayStateType = Cartesian;
Sat.X = {sma_km};
Sat.Y = 0;
Sat.Z = 0;
Sat.VX = 0;
Sat.VY = {vy_kms};
Sat.VZ = 0;

FM.CentralBody = Earth;
FM.PrimaryBodies = {{Earth}};
FM.Drag = None;
FM.SRP = Off;

Prop.Type = RungeKutta89;
Prop.FM = FM;
Prop.InitialStepSize = 60;
Prop.Accuracy = 1e-10;
Prop.MinStep = 0.1;
Prop.MaxStep = 600;

DefaultReportFile.Filename = 'C:/Users/belen/OneDrive/Desktop/AMPLI/DefaultReportFile.txt';
DefaultReportFile.WriteHeaders = true;
DefaultReportFile.Precision = 16;
DefaultReportFile.AppendToExistingFile = false;
DefaultReportFile.Add = {{Sat.ElapsedDays, Sat.X, Sat.Y, Sat.Z}};

BeginMissionSequence;
Report DefaultReportFile Sat.ElapsedDays Sat.X Sat.Y Sat.Z;
Propagate Prop(Sat) {{Sat.ElapsedDays = {dur_days}}};
Report DefaultReportFile Sat.ElapsedDays Sat.X Sat.Y Sat.Z;
"""
    SCRIPT_PATH.write_text(script_text.strip() + "\n", encoding="utf-8")
    print(f"Script generado en: {SCRIPT_PATH}")


def run_gmat():
    print(f"Voy a lanzar GMAT con el script: {SCRIPT_PATH}")
    print(f"Ejecutable: {GMAT_EXE}")

    result = subprocess.run(
        [str(GMAT_EXE), "--run", str(SCRIPT_PATH)],
        check=True,
        cwd=str(GMAT_BIN),
        text=True,
    )

    print("GmatConsole ha terminado.")


def read_and_plot_report():
    if not REPORT_PATH.exists():
        raise FileNotFoundError(f"No se encuentra {REPORT_PATH}")

    # 1) Leer separado por espacios
    #    comment='S' hace que cualquier línea que empiece por 'S' (las cabeceras) se ignore
    df = pd.read_csv(
        REPORT_PATH,
        delim_whitespace=True,
        comment='S',
        header=None,
        names=['Sat.ElapsedDays', 'Sat.X', 'Sat.Y', 'Sat.Z']
    )

    # 2) Convertimos a numérico por si queda algo raro
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()

    print("Columnas en el ReportFile (limpias):")
    print(df.columns)
    print("\nPrimeras filas limpias:")
    print(df.head())

    time_col = 'Sat.ElapsedDays'
    x_col = 'Sat.X'
    y_col = 'Sat.Y'

    plt.figure()
    plt.plot(df[x_col], df[y_col])
    plt.xlabel(f"{x_col} (km)")
    plt.ylabel(f"{y_col} (km)")
    plt.title("Órbita en plano XY")
    plt.axis("equal")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # Elige aquí los parámetros
    generate_script(sma_km=10000.0, vy_kms=7.5, dur_days=0.1)
    run_gmat()
    read_and_plot_report()

