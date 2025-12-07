from pathlib import Path
import subprocess

# === RUTAS IMPORTANTES (AJUSTA ESTAS) ===
BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / "datos_guardados.txt"
SCRIPT_PATH = BASE_DIR / "demo.script"

GMAT_BIN = Path(r"C:\Users\belen\Downloads\gmat-win-R2025a\GMAT_R2025a\bin")
GMAT_EXE = GMAT_BIN / "GmatConsole.exe"

# El report que generará GMAT (puedes cambiar el nombre si quieres)
REPORT_PATH = BASE_DIR / "DefaultReportFile.txt"


# ===========================
#   MAPEOS AUXILIARES
# ===========================

def map_body(spanish_name: str) -> str:
    mapping = {
        "Tierra": "Earth",
        "Luna": "Luna",
        "Marte": "Mars",
        "Venus": "Venus",
        "Júpiter": "Jupiter",
        "Saturno": "Saturn",
        "Urano": "Uranus",
        "Neptuno": "Neptune",
        "Mercurio": "Mercury",
        "Sol": "Sun",
    }
    return mapping.get(spanish_name, "Earth")


def map_coord_system(central_body_en: str, sistema_ref: str) -> str:
    # Muy simple: <Cuerpo>MJ2000Eq o Ec
    if sistema_ref == "Eclíptico":
        suffix = "MJ2000Ec"
    else:  # "Ecuatorial" u otro
        suffix = "MJ2000Eq"
    return f"{central_body_en}{suffix}"


def map_time_format(fmt: str) -> str:
    mapping = {
        "UTC": "UTCGregorian",
        "TAI": "TAIGregorian",
        "TT": "TTGregorian",
    }
    return mapping.get(fmt, "UTCGregorian")


def to_float(value: str, default: float = 0.0) -> float:
    try:
        v = value.strip().replace(",", ".")
        return float(v)
    except Exception:
        return default


def sanitize_name(name: str, default: str = "Sat") -> str:
    """Convierte 'Mi nave 1' en 'Mi_nave_1' y se asegura
    de que no quede vacío."""
    if not name:
        return default
    name = name.strip()
    if not name:
        return default
    # Reemplazar espacios por guión bajo
    name = name.replace(" ", "_")
    # Quitar caracteres raros
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    name = "".join(c for c in name if c in allowed)
    if not name:
        return default
    return name


# ===========================
#   PARSEAR datos_guardados.txt
# ===========================

def parse_gui_txt(path: Path) -> dict:
    """
    Lee datos_guardados.txt generado por la GUI y devuelve
    un diccionario con secciones:
      general, spacecraft, time, propagate, impulsive_burn, reportfile
    """
    config = {
        "general": {},
        "spacecraft": {},
        "time": {},
        "propagate": {},
        "impulsive_burn": {},
        "reportfile": {},
    }
    current_section = None

    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {path}")

    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            # Detectar secciones
            if line.startswith("=== ") and line.endswith(" ==="):
                if "GENERAL" in line:
                    current_section = "general"
                elif "SPACECRAFT" in line:
                    current_section = "spacecraft"
                elif "TIEMPO" in line:
                    current_section = "time"
                elif "PROPAGATE" in line:
                    current_section = "propagate"
                elif "IMPULSIVE BURN" in line:
                    current_section = "impulsive_burn"
                elif "REPORTFILE" in line:
                    current_section = "reportfile"
                continue

            # Clave: valor
            if ":" in line and current_section is not None:
                key, value = line.split(":", 1)
                config[current_section][key.strip()] = value.strip()

    return config


# ===========================
#   GENERAR SCRIPT GMAT
# ===========================

def build_gmat_script(cfg: dict, script_path: Path):
    gen = cfg["general"]
    sc = cfg["spacecraft"]
    tm = cfg["time"]
    pr = cfg["propagate"]
    rp = cfg["reportfile"]

    # --- GENERAL ---
    name_raw = gen.get("Nombre nave", "Sat")
    sat_name = sanitize_name(name_raw)

    central_es = gen.get("Cuerpo central", "Tierra")
    central_en = map_body(central_es)

    sistema_ref = gen.get("Sistema de referencia", "Ecuatorial")
    coord_system = map_coord_system(central_en, sistema_ref)

    time_fmt = gen.get("Formato de tiempo", "UTC")
    date_format = map_time_format(time_fmt)

    # --- TIME ---
    epoch_str = tm.get("Fecha inicio", "01 Jan 2030 12:00:00.000")
    # Usamos Paso temporal como duración en días (aprox)
    dur_days = to_float(tm.get("Paso temporal", "1.0"), default=1.0)

    # --- SPACECRAFT ---
    coord_type = sc.get("Sistema de coordenadas", "Cartesianas")
    use_cartesian = (coord_type == "Cartesianas")

    # Valores por defecto simples
    x = y = z = vx = vy = vz = 0.0
    sma = ecc = inc = raan = aop = ta = 0.0

    if use_cartesian:
        x = to_float(sc.get("x", "7000"))
        y = to_float(sc.get("y", "0"))
        z = to_float(sc.get("z", "0"))
        vx = to_float(sc.get("vx", "0"))
        vy = to_float(sc.get("vy", "7.5"))
        vz = to_float(sc.get("vz", "0"))
    else:
        sma = to_float(sc.get("SMA", "7000"))
        ecc = to_float(sc.get("ECC", "0.0"))
        inc = to_float(sc.get("INC", "0.0"))
        raan = to_float(sc.get("RAAN", "0.0"))
        aop = to_float(sc.get("AOP", "0.0"))
        ta = to_float(sc.get("TA", "0.0"))

    # --- PROPAGATE / INTEGRADOR ---
    integrador = pr.get("Tipo de integrador", "RungeKutta89")
    h0 = to_float(pr.get("Tamaño de paso inicial", "60"))
    acc = to_float(pr.get("Precision (accuracy)", "1e-10"))
    hmin = to_float(pr.get("Paso minimo", "0.1"))
    hmax = to_float(pr.get("Paso maximo", "600"))
    max_attempts = int(to_float(pr.get("Intentos max. paso", "50")))

    pr_central_es = pr.get("Cuerpo central", central_es)
    pr_primary_es = pr.get("Cuerpo primario", central_es)
    pr_central_en = map_body(pr_central_es)
    pr_primary_en = map_body(pr_primary_es)

    # --- REPORTFILE ---
    report_name = rp.get("Nombre del archivo de reporte", "DefaultReportFile.txt")
    if not report_name:
        report_name = "DefaultReportFile.txt"

    # Ruta (mismo directorio que este script)
    report_path_str = str((script_path.parent / report_name).as_posix())

    # De momento ignoramos la lista de variables seleccionadas en la GUI
    # y metemos un conjunto estándar: tiempo + estado cartesiano
    report_vars = "{{{sat}.ElapsedDays, {sat}.X, {sat}.Y, {sat}.Z}}".format(sat=sat_name)

    # =======================
    #  CONSTRUIR EL SCRIPT
    # =======================

    lines = []

    # Crear objetos básicos
    lines.append(f"Create Spacecraft {sat_name};")
    lines.append("Create ForceModel FM;")
    lines.append("Create Propagator Prop;")
    lines.append("Create ReportFile DefaultReportFile;")
    lines.append("")  # línea en blanco

    # Spacecraft
    lines.append(f"{sat_name}.DateFormat = {date_format};")
    lines.append(f"{sat_name}.Epoch = '{epoch_str}';")
    lines.append(f"{sat_name}.CoordinateSystem = {coord_system};")

    if use_cartesian:
        lines.append(f"{sat_name}.DisplayStateType = Cartesian;")
        lines.append(f"{sat_name}.X = {x};")
        lines.append(f"{sat_name}.Y = {y};")
        lines.append(f"{sat_name}.Z = {z};")
        lines.append(f"{sat_name}.VX = {vx};")
        lines.append(f"{sat_name}.VY = {vy};")
        lines.append(f"{sat_name}.VZ = {vz};")
    else:
        lines.append(f"{sat_name}.DisplayStateType = Keplerian;")
        lines.append(f"{sat_name}.SMA = {sma};")
        lines.append(f"{sat_name}.ECC = {ecc};")
        lines.append(f"{sat_name}.INC = {inc};")
        lines.append(f"{sat_name}.RAAN = {raan};")
        lines.append(f"{sat_name}.AOP = {aop};")
        lines.append(f"{sat_name}.TA = {ta};")

    lines.append("")  # línea en blanco

    # ForceModel sencillo (solo cuerpo principal como punto-masa)
    lines.append(f"FM.CentralBody = {pr_central_en};")
    lines.append(f"FM.PrimaryBodies = {{{{{pr_primary_en}}}}};")
    lines.append("FM.Drag = None;")
    lines.append("FM.SRP = Off;")
    lines.append("")

    # Propagador
    lines.append(f"Prop.Type = {integrador};")
    lines.append("Prop.FM = FM;")
    lines.append(f"Prop.InitialStepSize = {h0};")
    lines.append(f"Prop.Accuracy = {acc};")
    lines.append(f"Prop.MinStep = {hmin};")
    lines.append(f"Prop.MaxStep = {hmax};")
    lines.append(f"Prop.MaxStepAttempts = {max_attempts};")
    lines.append("")

    # ReportFile
    lines.append(f"DefaultReportFile.Filename = '{report_path_str}';")
    lines.append("DefaultReportFile.WriteHeaders = true;")
    lines.append("DefaultReportFile.Precision = 16;")
    lines.append("DefaultReportFile.AppendToExistingFile = false;")
    lines.append(f"DefaultReportFile.Add = {report_vars};")
    lines.append("")

    # Mission Sequence
    lines.append("BeginMissionSequence;")
    lines.append(f"Report DefaultReportFile {sat_name}.ElapsedDays {sat_name}.X {sat_name}.Y {sat_name}.Z;")
    lines.append(f"Propagate Prop({sat_name}) {{{{{sat_name}.ElapsedDays = {dur_days}}}}};")
    lines.append(f"Report DefaultReportFile {sat_name}.ElapsedDays {sat_name}.X {sat_name}.Y {sat_name}.Z;")
    lines.append("")

    script_text = "\n".join(lines) + "\n"
    script_path.write_text(script_text, encoding="utf-8")

    print(f"Script GMAT generado en: {script_path}")
    print("Contenido aproximado:")
    print("-----------------------------------------")
    print(script_text[:500] + "...\n")  # solo un trocito


# ===========================
#   LANZAR GMAT
# ===========================

def run_gmat(script_path: Path):
    if not GMAT_EXE.exists():
        raise FileNotFoundError(f"No se encuentra GMAT en {GMAT_EXE}")

    print(f"Voy a lanzar GMAT con: {GMAT_EXE}")
    print(f"Script: {script_path}")

    result = subprocess.run(
        [str(GMAT_EXE), "--run", str(script_path)],
        check=True,
        cwd=str(GMAT_BIN),
        text=True,
    )

    print("GmatConsole ha terminado.")
    print(f"Si todo ha ido bien, el report está en: {REPORT_PATH}")


# ===========================
#   MAIN
# ===========================

if __name__ == "__main__":
    cfg = parse_gui_txt(DATA_FILE)
    build_gmat_script(cfg, SCRIPT_PATH)
    run_gmat(SCRIPT_PATH)
