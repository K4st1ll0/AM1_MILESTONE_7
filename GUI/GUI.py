from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QTabWidget, QVBoxLayout, QFormLayout
)
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
        self.paso_temporal = QLineEdit()
        
        form_time.addRow("Fecha de inicio:", self.fecha_inicio)
        form_time.addRow("Fecha final:", self.fecha_final)
        form_time.addRow("Paso temporal:", self.paso_temporal)
        tab_time.setLayout(form_time)


        ### Tab Propagate setup

        tab_propagate = QWidget()


        # Añadir pestañas
        tabs.addTab(tab_general, "General")
        tabs.addTab(tab_spacecraft, "Spacecraft")
        tabs.addTab(tab_time, "Tiempo")
        

        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def update_spacecraft_fields(self):

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
            self.tanks_input = QLineEdit()
            self.drag_input = QLineEdit()
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
            self.form_spacecraft.addRow("Número de tanques:", self.tanks_input)
            self.form_spacecraft.addRow("Arrastre:", self.drag_input)
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
            self.tanks_input = QLineEdit()
            self.drag_input = QLineEdit()
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
            self.form_spacecraft.addRow("Número de tanques:", self.tanks_input)
            self.form_spacecraft.addRow("Arrastre:", self.drag_input)
            self.form_spacecraft.addRow("Formato de fecha:", self.epoch_input)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 600)
    window.show()
    sys.exit(app.exec())
