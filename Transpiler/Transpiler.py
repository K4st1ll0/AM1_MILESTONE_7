from pathlib import Path
import subprocess
import sys


def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Estamos dentro del .exe
        return Path(sys.executable).resolve().parent
    else:
        # Estamos en modo script normal
        return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()
DATA_FILE = BASE_DIR / "Datos" / "datos_guardados.txt"
SCRIPT_PATH = BASE_DIR / "Transpiler_output" / "demo.script"



def map_body(spanish_name: str) -> str:
    mapping = {
        "Tierra": "Earth",
        "Luna": "Luna",
        "Marte": "Mars",
        "Venus": "Venus",
        "Júpiter": "Jupiter",
        "Jupiter": "Jupiter",
        "Saturno": "Saturn",
        "Urano": "Uranus",
        "Neptuno": "Neptune",
        "Mercurio": "Mercury",
        "Sol": "Sun",
    }
    return mapping.get(spanish_name, "Earth")


def map_coord_system(central_body_en: str, sistema_ref: str) -> str:
    """Devuelve algo tipo 'EarthMJ2000Eq' o 'EarthMJ2000Ec' según referencia."""
    s = (sistema_ref or "").lower()
    if "eclip" in s:
        suffix = "MJ2000Ec"
    else:
        suffix = "MJ2000Eq"
    return f"{central_body_en}{suffix}"


def map_time_format(fmt: str) -> str:
    mapping = {
        "UTC": "UTCGregorian",
        "TAI": "TAIGregorian",
        "TT":  "TTGregorian",
    }
    return mapping.get(fmt, "UTCGregorian")


def to_float(value: str, default: float = 0.0) -> float:
    try:
        v = value.strip().replace(",", ".")
        return float(v)
    except Exception:
        return default
    
def positive_or_default(value: str, default: float) -> float:
    """Convierte a float y asegura que sea > 0, si no, usa el default."""
    v = to_float(value, default)
    if v <= 0:
        return default
    return v



def sanitize_name(name: str, default: str = "Sat") -> str:
    """Convierte 'Mi nave 1' en 'Mi_nave_1' y se asegura de que no quede vacío."""
    if not name:
        return default
    name = name.strip()
    if not name:
        return default
    name = name.replace(" ", "_")
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    name = "".join(c for c in name if c in allowed)
    if not name:
        return default
    return name


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

    # Si te vuelve a dar problemas de acentos, cambia utf-8 por "latin-1"
    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            # Detectar secciones por los "=== ... ==="
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
                else:
                    current_section = None
                continue

            # Clave: valor
            if ":" in line and current_section is not None:
                key, value = line.split(":", 1)
                config[current_section][key.strip()] = value.strip()

    return config

def map_report_variable(label: str, sat_name: str) -> str | None:
    """
    Convierte el texto de la GUI (en español) en el campo GMAT correspondiente.
    Devuelve None si no está soportado (de momento).
    """
    label = label.strip()

    # Tiempo
    if label == "Elapsed Days":
        return f"{sat_name}.ElapsedDays"
    if label == "Elapsed Seconds":
        return f"{sat_name}.ElapsedSecs"   # si da error, lo quitamos luego

    # Cartesianas
    if label == "Posicion X":
        return f"{sat_name}.X"
    if label == "Posicion Y":
        return f"{sat_name}.Y"
    if label == "Posicion Z":
        return f"{sat_name}.Z"
    if label == "Velocidad VX":
        return f"{sat_name}.VX"
    if label == "Velocidad VY":
        return f"{sat_name}.VY"
    if label == "Velocidad VZ":
        return f"{sat_name}.VZ"

    # Keplerianas
    if label == "Semieje mayor (SMA)":
        return f"{sat_name}.SMA"
    if label == "Excentricidad (ECC)":
        return f"{sat_name}.ECC"
    if label == "Inclinacion (INC)":
        return f"{sat_name}.INC"
    if label == "RAAN":
        return f"{sat_name}.RAAN"
    if label == "Argumento del periapsis (AOP)":
        return f"{sat_name}.AOP"
    if label == "Anomalia verdadera (TA)":
        return f"{sat_name}.TA"

    # Si no lo tenemos mapeado todavía, devolvemos None
    return None

def build_gmat_script(cfg: dict, script_path: Path):
    gen = cfg["general"]
    sc  = cfg["spacecraft"]
    tm  = cfg["time"]
    pr  = cfg["propagate"]
    ib  = cfg["impulsive_burn"]

    # ========== GENERAL ==========
    sat_name_raw = gen.get("Nombre nave", "").strip()
    sat_name = sanitize_name(sat_name_raw, default="Sat")

    central_es   = gen.get("Cuerpo central", "Tierra")
    central_en   = map_body(central_es)
    sistema_ref  = gen.get("Sistema de referencia", "Ecuatorial")
    coord_system = map_coord_system(central_en, sistema_ref)

    time_fmt    = gen.get("Formato de tiempo", "UTC")
    date_format = map_time_format(time_fmt)

    # ========== TIEMPO ==========
    epoch_str_raw = tm.get("Fecha inicio", "").strip()

    def normalize_epoch(epoch: str) -> str:
        if "/" in epoch:
            parts = epoch.split()
            date_part = parts[0]
            time_part = parts[1] if len(parts) > 1 else "12:00:00"

            d, m, y = date_part.split("/")
            months = {
                "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
                "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
                "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
            }

            return f"{d} {months[m]} {y} {time_part}.000"

        if ":" in epoch:
            if not epoch.endswith(".000"):
                return epoch + ".000"
            return epoch

        return "01 Jan 2030 12:00:00.000"

    epoch_str = normalize_epoch(epoch_str_raw)


    paso_str = tm.get("Paso temporal", "").strip()
    if paso_str == "":
        dur_days = 1.0
    else:
        dur_days = to_float(paso_str, default=1.0)

    # ========== SPACECRAFT ==========
    coord_type = sc.get("Sistema de coordenadas", "Cartesianas").strip()

    # Cartesianas
    x  = to_float(sc.get("x",  "7000"), default=7000.0)
    y  = to_float(sc.get("y",  "0"),    default=0.0)
    z  = to_float(sc.get("z",  "0"),    default=0.0)
    vx = to_float(sc.get("vx", "0"),    default=0.0)
    vy = to_float(sc.get("vy", "7.5"),  default=7.5)
    vz = to_float(sc.get("vz", "0"),    default=0.0)

    # Keplerianas
    sma  = to_float(sc.get("SMA",  "7000"), default=7000.0)
    ecc  = to_float(sc.get("ECC",  "0.0"),  default=0.0)
    inc  = to_float(sc.get("INC",  "0.0"),  default=0.0)
    raan = to_float(sc.get("RAAN", "0.0"),  default=0.0)
    aop  = to_float(sc.get("AOP",  "0.0"),  default=0.0)
    ta   = to_float(sc.get("TA",   "0.0"),  default=0.0)

    # ========== PROPAGATE (desde GUI) ==========
    integ_type = pr.get("Tipo de integrador", "RungeKutta89").strip() or "RungeKutta89"

    init_step = positive_or_default(pr.get("Tamano de paso inicial", "60"),   60.0)
    accuracy  = positive_or_default(pr.get("Precision (accuracy)", "1e-6"),   1e-6)
    min_step  = positive_or_default(pr.get("Paso minimo", "0.1"),             0.1)
    max_step  = positive_or_default(pr.get("Paso maximo", "600"),             600.0)

    max_step_attempts_str = pr.get("Intentos max. paso", "50")
    try:
        max_step_attempts = int(float(max_step_attempts_str.replace(",", ".")))
        if max_step_attempts <= 0:
            max_step_attempts = 50
    except Exception:
        max_step_attempts = 50

    # (Opcional: podrías usar estos más adelante)
    fm_central_es = pr.get("Cuerpo central", gen.get("Cuerpo central", "Tierra"))
    fm_central_en = map_body(fm_central_es)

    # ========== IMPULSIVE BURN (desde GUI) ==========
    ib_coord_raw = ib.get("Sistema de coordenadas", "Local").strip()
    ib_origin_es = ib.get("Origen", central_es)
    ib_axes      = ib.get("Axes", "VNB").strip()

    dv1 = to_float(ib.get("Delta V Element 1", "0"), 0.0)
    dv2 = to_float(ib.get("Delta V Element 2", "0"), 0.0)
    dv3 = to_float(ib.get("Delta V Element 3", "0"), 0.0)

    has_burn = (abs(dv1) + abs(dv2) + abs(dv3)) > 0.0

    # "Local" => usa el mismo sistema de coordenadas que el spacecraft
    if ib_coord_raw == "Local":
        ib_coord_gmat = coord_system
    else:
        # La GUI ya usa nombres tipo EarthMJ2000Eq, EarthFixed, etc.
        ib_coord_gmat = ib_coord_raw

    ib_origin_en = map_body(ib_origin_es)

    # ========== CONSTRUIR SCRIPT ==========
    lines = []

    # Objetos básicos
    lines.append(f"Create Spacecraft {sat_name};")
    lines.append("Create ForceModel FM;")
    lines.append("Create Propagator Prop;")
    if has_burn:
        lines.append("Create ImpulsiveBurn ImpBurn;")
    lines.append("Create ReportFile DefaultReportFile;")
    lines.append("")

    # --- Spacecraft ---
    lines.append(f"{sat_name}.DateFormat = {date_format};")
    lines.append(f"{sat_name}.Epoch = '{epoch_str}';")
    lines.append(f"{sat_name}.CoordinateSystem = {coord_system};")

    if coord_type == "Cartesianas":
        lines.append(f"{sat_name}.DisplayStateType = Cartesian;")
        lines.append(f"{sat_name}.X  = {x};")
        lines.append(f"{sat_name}.Y  = {y};")
        lines.append(f"{sat_name}.Z  = {z};")
        lines.append(f"{sat_name}.VX = {vx};")
        lines.append(f"{sat_name}.VY = {vy};")
        lines.append(f"{sat_name}.VZ = {vz};")
    else:
        lines.append(f"{sat_name}.DisplayStateType = Keplerian;")
        lines.append(f"{sat_name}.SMA  = {sma};")
        lines.append(f"{sat_name}.ECC  = {ecc};")
        lines.append(f"{sat_name}.INC  = {inc};")
        lines.append(f"{sat_name}.RAAN = {raan};")
        lines.append(f"{sat_name}.AOP  = {aop};")
        lines.append(f"{sat_name}.TA   = {ta};")

    lines.append("")

    # --- ForceModel (simple) ---
    lines.append(f"FM.CentralBody   = {fm_central_en};")
    lines.append(f"FM.PrimaryBodies = {{{fm_central_en}}};")
    lines.append("FM.Drag = None;")
    lines.append("FM.SRP  = Off;")
    lines.append("")

    # --- Propagator ---
    lines.append(f"Prop.Type            = {integ_type};")
    lines.append("Prop.FM              = FM;")
    lines.append(f"Prop.InitialStepSize = {init_step};")
    lines.append(f"Prop.Accuracy        = {accuracy};")
    lines.append(f"Prop.MinStep         = {min_step};")
    lines.append(f"Prop.MaxStep         = {max_step};")
    lines.append(f"Prop.MaxStepAttempts = {max_step_attempts};")
    lines.append("")

    # --- ImpulsiveBurn (si hay ΔV) ---
    if has_burn:
        lines.append(f"ImpBurn.CoordinateSystem = {ib_coord_gmat};")
        lines.append(f"ImpBurn.Origin          = {ib_origin_en};")
        lines.append(f"ImpBurn.Axes            = {ib_axes};")
        lines.append(f"ImpBurn.Element1        = {dv1};")
        lines.append(f"ImpBurn.Element2        = {dv2};")
        lines.append(f"ImpBurn.Element3        = {dv3};")
        # Para no complicarnos con tanques:
        lines.append("ImpBurn.DecrementMass   = false;")
        lines.append("")

    # --- ReportFile (RUTA RELATIVA, PORTABLE) ---

    # script_path = AM1_MILESTONE_7/Transpiler_output/demo.script
    BASE_PROJECT_DIR = BASE_DIR

    OUTPUT_DIR = BASE_PROJECT_DIR / "GMAT_output"
    OUTPUT_DIR.mkdir(exist_ok=True)

    report_path = OUTPUT_DIR / "DefaultReportFile.txt"

    # GMAT 2019 acepta perfectamente rutas con '/'
    report_path_str = report_path.as_posix()

    lines.append(f"DefaultReportFile.Filename = '{report_path_str}';")
    lines.append("DefaultReportFile.WriteHeaders = true;")
    lines.append("DefaultReportFile.Precision = 16;")
    lines.append(
        f"DefaultReportFile.Add = "
        f"{{{sat_name}.ElapsedDays, {sat_name}.X, {sat_name}.Y, {sat_name}.Z}};"
    )
    lines.append("")




    # --- Mission Sequence ---
    lines.append("BeginMissionSequence;")
    lines.append(
        f"Report DefaultReportFile "
        f"{sat_name}.ElapsedDays {sat_name}.X {sat_name}.Y {sat_name}.Z;"
    )

    # Aplicamos el burn justo al principio, antes de propagar
    if has_burn:
        lines.append(f"Maneuver ImpBurn({sat_name});")

    lines.append(
        f"Propagate Prop({sat_name}) "
        f"{{{sat_name}.ElapsedDays = {dur_days}}};"
    )
    lines.append(
        f"Report DefaultReportFile "
        f"{sat_name}.ElapsedDays {sat_name}.X {sat_name}.Y {sat_name}.Z;"
    )
    lines.append("")

    script_text = "\n".join(lines)
    script_path.write_text(script_text, encoding="utf-8")

    print(f"Script GMAT generado en: {script_path}")
    print("Contenido aproximado:")
    print("-----------------------------------------")
    print(script_text[:400] + "...\n")



if __name__ == "__main__":
    cfg = parse_gui_txt(DATA_FILE)

    # Solo para comprobar por pantalla 
    print("=== GENERAL ===")
    for k, v in cfg["general"].items():
        print(f"{k} -> {v}")

    print("\n=== SPACECRAFT ===")
    for k, v in cfg["spacecraft"].items():
        print(f"{k} -> {v}")

    print("\n=== TIEMPO ===")
    for k, v in cfg["time"].items():
        print(f"{k} -> {v}")

    # Y ahora generamos el script
    build_gmat_script(cfg, SCRIPT_PATH)


#### Ejecutar GMAT en modo consola ####
# ================================
# DETECCIÓN AUTOMÁTICA DE GMAT
# ================================


def find_gmat():
    posibles = [
        Path(r"C:\Program Files\GMAT\bin\GmatConsole.exe"),
        Path(r"C:\Program Files (x86)\GMAT\bin\GmatConsole.exe"),
        Path(r"C:\Program Files (x86)\GMAT-R2019aBeta-Windows-x64-public\bin\GmatConsole.exe")
    ]

    for p in posibles:
        if p.exists():
            return str(p)

    raise FileNotFoundError("❌ GMAT no está instalado o no se encontró GmatConsole.exe")


# ================================
# EJECUCIÓN DE GMAT
# ================================


def run_transpiler():
    # Asegurar carpetas
    (BASE_DIR / "Transpiler_output").mkdir(exist_ok=True)
    (BASE_DIR / "GMAT_output").mkdir(exist_ok=True)

    cfg = parse_gui_txt(DATA_FILE)
    build_gmat_script(cfg, SCRIPT_PATH)


