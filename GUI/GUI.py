from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QTabWidget, QVBoxLayout, QFormLayout, QPushButton, QListWidget, QAbstractItemView
)
from PySide6.QtCore import Qt

import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interfaz Orbital")

        layout = QVBoxLayout()
        tabs = QTabWidget()

        ### Tab general setup

        tab_general = QWidget()
        form_general = QFormLayout()

        self.nombre_nave = QLineEdit()
        self.Cuerpo_central = QComboBox()
        self.Cuerpo_central.addItems(["Tierra", "Luna", "Marte", "Venus", "Júpiter", "Saturno", "Urano", "Neptuno", "Mercurio", "Sol"])
        self.Sistema_de_referencia = QComboBox()
        self.Sistema_de_referencia.addItems(["Eclíptico", "Ecuatorial"]) ##############################
        self.formato_tiempo = QComboBox()
        self.formato_tiempo.addItems(["UTC", "TAI", "TT"]) ##############################
        form_general.addRow("Nombre de la nave:", self.nombre_nave)
        form_general.addRow("Cuerpo central:", self.Cuerpo_central)
        form_general.addRow("Sistema de referencia:", self.Sistema_de_referencia)
        form_general.addRow("Formato de tiempo:", self.formato_tiempo)
        self.formato_tiempo.currentTextChanged.connect(lambda _: self.actualizar_formato_tiempo())



        tab_general.setLayout(form_general)


        ### Tab spacecraft setup

        tab_spacecraft = QWidget()
        self.form_spacecraft = QFormLayout()
        tab_spacecraft.setLayout(self.form_spacecraft)

        self.coordinates = QComboBox()
        self.coordinates.addItems(["Cartesianas", "Keplerianas"])
        self.coordinates.currentIndexChanged.connect(self.update_spacecraft_fields)

        self.form_spacecraft.addRow("Sistema de coordenadas:", self.coordinates)

        self.update_spacecraft_fields()

        tab_spacecraft.setLayout(self.form_spacecraft)

        ### Tab time setup

        tab_time = QWidget()
        form_time = QFormLayout()

        self.fecha_inicio = QLineEdit()
        self.fecha_final = QLineEdit()

        form_time.addRow("Fecha de inicio:", self.fecha_inicio)
        form_time.addRow("Fecha final:", self.fecha_final)

        tab_time.setLayout(form_time)

        # Llamada inicial
        self.actualizar_formato_tiempo()



        ### Tab Propagate setup

        tab_propagate = QWidget()
        form_propagate = QFormLayout()

        # Integrador
        self.tipo_integrador = QComboBox()
        self.tipo_integrador.addItems(["RungeKutta89", "PrinceDormand78"])
        self.initial_step_size = QLineEdit()
        self.accuracy = QLineEdit()
        self.min_step_size = QLineEdit()
        self.max_step_size = QLineEdit()
        self.mas_step_attemps = QLineEdit()

        # Force Model
        self.central_body = QComboBox()
        self.central_body.addItems(["Tierra", "Luna", "Marte", "Venus", "Júpiter", "Saturno", "Urano", "Neptuno", "Mercurio", "Sol"])

        self.primary_body = QComboBox()
        self.primary_body.addItems(["Tierra", "Luna", "Marte", "Venus", "Júpiter", "Saturno", "Urano", "Neptuno", "Mercurio", "Sol"])

        self.gmodel = QComboBox()
        self.gmodel.addItems(["JGM-2", "JGM-3", "EGM-96", "None"])

        self.gdegree = QLineEdit()
        self.gorder = QLineEdit()
        self.gSTMLimit = QLineEdit()

        self.drag_atmosphere_model = QComboBox()
        self.drag_atmosphere_model.addItems(["None", "Jacchia Roberts", "MSISE90"])

        # Drag model —> opciones Spherical / SPADFile
        self.drag_model = QComboBox()
        self.drag_model.addItems(["Spherical", "SPADFile"])
        self.drag_model.setEnabled(False)
        self.drag_model.hide()

        # Activar / desactivar drag model según atmósfera
        self.drag_atmosphere_model.currentTextChanged.connect(self.on_atmosphere_changed)
        

        # Añadir campos al formulario propagate
        form_propagate.addRow("Integrador:", self.tipo_integrador)
        form_propagate.addRow("Tamaño de paso inicial:", self.initial_step_size)
        form_propagate.addRow("Precisión (accuracy):", self.accuracy)
        form_propagate.addRow("Paso mínimo:", self.min_step_size)
        form_propagate.addRow("Paso máximo:", self.max_step_size)
        form_propagate.addRow("Intentos máx. paso:", self.mas_step_attemps)

        form_propagate.addRow("Cuerpo central:", self.central_body)
        form_propagate.addRow("Cuerpo primario:", self.primary_body)
        form_propagate.addRow("Modelo gravitatorio:", self.gmodel)
        form_propagate.addRow("Grado:", self.gdegree)
        form_propagate.addRow("Orden:", self.gorder)
        form_propagate.addRow("STM Limit:", self.gSTMLimit)
        form_propagate.addRow("Atmósfera:", self.drag_atmosphere_model)
        form_propagate.addRow("Modelo de arrastre:", self.drag_model)

        tab_propagate.setLayout(form_propagate)


        ### Tab Impulsive burnt setup

        tab_impulsive_burn = QWidget()
        form_impulsive_burn = QFormLayout()

        self.coordinate_system = QComboBox()
        self.coordinate_system.addItems(["Local", "EarthMJ2000Eq", "EarthMJ2000Ec", "EarthFixed", "EarthICRF"])

        self.origin = QComboBox()
        self.origin.addItems(["Tierra", "Luna", "Marte", "Venus", "Júpiter", "Saturno", "Urano", "Neptuno", "Mercurio", "Sol"])

        self.axes = QComboBox()
        self.axes.addItems(["VNB", "LVLH", "MJ2000Eq", "SpacecraftBody"])

        self.DV_element1 = QLineEdit()
        self.DV_element2 = QLineEdit()
        self.DV_element3 = QLineEdit()

        form_impulsive_burn.addRow("Sistema de coordenadas:", self.coordinate_system)
        form_impulsive_burn.addRow("Origen:", self.origin)
        form_impulsive_burn.addRow("Axes:", self.axes)
        form_impulsive_burn.addRow("Delta V Element 1:", self.DV_element1)
        form_impulsive_burn.addRow("Delta V Element 2:", self.DV_element2)
        form_impulsive_burn.addRow("Delta V Element 3:", self.DV_element3)

        tab_impulsive_burn.setLayout(form_impulsive_burn)


        ### Tab reportfile setup

        tab_reportfile = QWidget()
        form_reportfile = QFormLayout()
       
        self.reportfile_name = QLineEdit()
        self.reportfile_name.setPlaceholderText("DefaultReportFile.txt")

        form_reportfile.addRow("Nombre del archivo de reporte:", self.reportfile_name)
        tab_reportfile.setLayout(form_reportfile)


        # Añadir pestañas 

        tabs.addTab(tab_general, "General")
        tabs.addTab(tab_spacecraft, "Spacecraft")
        tabs.addTab(tab_time, "Time")
        tabs.addTab(tab_propagate, "Propagate")
        tabs.addTab(tab_impulsive_burn, "Impulsive Burn")
        tabs.addTab(tab_reportfile, "Reportfile")
     
    

        # ==========================================================
        # --- BOTÓN GUARDAR DATOS ---
        # ==========================================================
        # Añadir pestañas y generar datos
        self.btn_guardar = QPushButton("Guardar datos en TXT")
        self.btn_guardar.clicked.connect(self.guardar_datos)

        layout.addWidget(tabs)
        layout.addWidget(self.btn_guardar)
        self.setLayout(layout)

    def actualizar_formato_tiempo(self):
        self.fecha_inicio.clear()
        self.fecha_final.clear()

        if self.formato_tiempo.currentText() == "UTC":
            self.fecha_inicio.setPlaceholderText("DD/MM/AAAA HH:MM:SS")
            self.fecha_final.setPlaceholderText("DD/MM/AAAA HH:MM:SS")
        else:
            self.fecha_inicio.setPlaceholderText("Días desde t0")
            self.fecha_final.setPlaceholderText("Días desde t0")


    
    def update_spacecraft_fields(self): # Actualiza los campos del formulario según el sistema de coordenadas seleccionado

        # 1. Borrar filas antiguas excepto la primera (el combo)
        while self.form_spacecraft.rowCount() > 1:
            self.form_spacecraft.removeRow(1)

        # 2. Cargar los campos adecuados
        if self.coordinates.currentText() == "Cartesianas":
            self.x_input = QLineEdit()
            self.y_input = QLineEdit()
            self.z_input = QLineEdit()
            self.vx_input = QLineEdit()
            self.vy_input = QLineEdit()
            self.vz_input = QLineEdit()
            self.dry_mass_input = QLineEdit()
            self.fuel_mass_input = QLineEdit()
            self.epoch_input = QComboBox()
            self.epoch_input.addItems(["UTC", "Julian Dates"])###########################

            self.form_spacecraft.addRow("x:", self.x_input)
            self.form_spacecraft.addRow("y:", self.y_input)
            self.form_spacecraft.addRow("z:", self.z_input)
            self.form_spacecraft.addRow("vx:", self.vx_input)
            self.form_spacecraft.addRow("vy:", self.vy_input)
            self.form_spacecraft.addRow("vz:", self.vz_input)
            self.form_spacecraft.addRow("Masa en seco [kg]:", self.dry_mass_input)
            self.form_spacecraft.addRow("Masa de combustible [kg]:", self.fuel_mass_input)
            self.form_spacecraft.addRow("Formato de fecha:", self.epoch_input)

        else:  # Keplerianas
            self.SMA_input = QLineEdit()
            self.ECC_input = QLineEdit()
            self.INC_input = QLineEdit()
            self.RAAN_input = QLineEdit()
            self.AOP_input = QLineEdit()
            self.TA_input = QLineEdit()
            self.dry_mass_input = QLineEdit()
            self.fuel_mass_input = QLineEdit()
            self.epoch_input = QComboBox()
            self.epoch_input.addItems(["UTC", "Julian Dates"])###########################

            self.form_spacecraft.addRow("Semi-major axis (SMA):", self.SMA_input)
            self.form_spacecraft.addRow("Eccentricity (ECC):", self.ECC_input)
            self.form_spacecraft.addRow("Inclination (INC):", self.INC_input)
            self.form_spacecraft.addRow("RAAN:", self.RAAN_input)
            self.form_spacecraft.addRow("AOP:", self.AOP_input)
            self.form_spacecraft.addRow("True Anomaly (TA):", self.TA_input)
            self.form_spacecraft.addRow("Masa en seco [kg]:", self.dry_mass_input)
            self.form_spacecraft.addRow("Masa de combustible [kg]:", self.fuel_mass_input)
            self.form_spacecraft.addRow("Formato de fecha:", self.epoch_input)
    
    def on_atmosphere_changed(self, text):
        if text != "None":
            self.drag_model.setEnabled(True)
            self.drag_model.show()
        else:
            self.drag_model.setEnabled(False)
            self.drag_model.hide()


    # ==========================================================
    # FUNCIÓN PARA GUARDAR DATOS EN UN TXT
    # ==========================================================
    def guardar_datos(self): # Recopila los datos de todas las pestañas y los guarda en un archivo TXT

        datos = []

        # --- GENERAL ---
        datos.append("=== GENERAL ===")
        datos.append(f"Nombre nave: {self.nombre_nave.text()}")
        datos.append(f"Cuerpo central: {self.Cuerpo_central.currentText()}")
        datos.append(f"Sistema de referencia: {self.Sistema_de_referencia.currentText()}")
        datos.append(f"Formato de tiempo: {self.formato_tiempo.currentText()}")

        # --- SPACECRAFT ---
        datos.append("\n=== SPACECRAFT ===")
        datos.append(f"Sistema de coordenadas: {self.coordinates.currentText()}")

        if self.coordinates.currentText() == "Cartesianas":
            datos.append(f"x: {self.x_input.text()}")
            datos.append(f"y: {self.y_input.text()}")
            datos.append(f"z: {self.z_input.text()}")
            datos.append(f"vx: {self.vx_input.text()}")
            datos.append(f"vy: {self.vy_input.text()}")
            datos.append(f"vz: {self.vz_input.text()}")
        else:
            datos.append(f"SMA: {self.SMA_input.text()}")
            datos.append(f"ECC: {self.ECC_input.text()}")
            datos.append(f"INC: {self.INC_input.text()}")
            datos.append(f"RAAN: {self.RAAN_input.text()}")
            datos.append(f"AOP: {self.AOP_input.text()}")
            datos.append(f"TA: {self.TA_input.text()}")

        datos.append(f"Masa seca: {self.dry_mass_input.text()}")
        datos.append(f"Masa combustible: {self.fuel_mass_input.text()}")
        datos.append(f"Formato epoch: {self.epoch_input.currentText()}")

        # --- TIME ---
        datos.append("\n=== TIEMPO ===")
        datos.append(f"Fecha inicio: {self.fecha_inicio.text()}")
        datos.append(f"Fecha final: {self.fecha_final.text()}")

        # --- PROPAGATE ---
        datos.append("\n=== PROPAGATE ===")
        datos.append(f"Tipo de integrador: {self.tipo_integrador.currentText()}")
        datos.append(f"Tamaño de paso inicial: {self.initial_step_size.text()}")
        datos.append(f"Precision (accuracy): {self.accuracy.text()}")
        datos.append(f"Paso minimo: {self.min_step_size.text()}")
        datos.append(f"Paso maximo: {self.max_step_size.text()}")
        datos.append(f"Intentos max. paso: {self.mas_step_attemps.text()}")
        datos.append(f"Cuerpo central: {self.central_body.currentText()}")
        datos.append(f"Cuerpo primario: {self.primary_body.currentText()}")
        datos.append(f"Modelo gravitatorio: {self.gmodel.currentText()}")
        datos.append(f"Grado: {self.gdegree.text()}")
        datos.append(f"Orden: {self.gorder.text()}")
        datos.append(f"STM Limit: {self.gSTMLimit.text()}")
        datos.append(f"Atmosfera: {self.drag_atmosphere_model.currentText()}")
        datos.append(f"Modelo de arrastre: {self.drag_model.currentText()}")

        # --- IMPULSIVE BURN ---
        datos.append("\n=== IMPULSIVE BURN ===")
        datos.append(f"Sistema de coordenadas: {self.coordinate_system.currentText()}")
        datos.append(f"Origen: {self.origin.currentText()}")
        datos.append(f"Axes: {self.axes.currentText()}")
        datos.append(f"Delta V Element 1: {self.DV_element1.text()}")
        datos.append(f"Delta V Element 2: {self.DV_element2.text()}")
        datos.append(f"Delta V Element 3: {self.DV_element3.text()}")


        # --- REPORTFILE ---
        datos.append("\n=== REPORTFILE ===")
        datos.append(f"Nombre del archivo de reporte: {self.reportfile_name}")
        


        # --- GUARDAR ---
        with open("datos_guardados.txt", "w") as f:
            f.write("\n".join(datos))

        print("Archivo guardado: datos_guardados.txt")





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 600)
    window.show()
    sys.exit(app.exec())
