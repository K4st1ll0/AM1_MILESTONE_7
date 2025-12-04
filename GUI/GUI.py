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

        # =============================
        # TAB 1: NAVE
        # =============================
        tab_nave = QWidget()
        form_nave = QFormLayout()

        self.masa_input = QLineEdit()
        form_nave.addRow("Masa de la nave [kg]:", self.masa_input)

        tab_nave.setLayout(form_nave)

        # =============================
        # TAB 2: COORDENADAS INICIALES
        # =============================
        tab_coord = QWidget()
        form_coord = QFormLayout()

        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.z_input = QLineEdit()
        self.vx_input = QLineEdit()
        self.vy_input = QLineEdit()
        self.vz_input = QLineEdit()

        form_coord.addRow("x:", self.x_input)
        form_coord.addRow("y:", self.y_input)
        form_coord.addRow("z:", self.z_input)
        form_coord.addRow("vx:", self.vx_input)
        form_coord.addRow("vy:", self.vy_input)
        form_coord.addRow("vz:", self.vz_input)

        tab_coord.setLayout(form_coord)

        # =============================
        # TAB 3: ÓRBITA
        # =============================
        tab_orbita = QWidget()
        form_orbita = QFormLayout()

        self.tipo_orbita = QComboBox()
        self.tipo_orbita.addItems(["Circular", "Elíptica"])

        form_orbita.addRow("Tipo de órbita:", self.tipo_orbita)

        tab_orbita.setLayout(form_orbita)

        # Añadir pestañas
        tabs.addTab(tab_nave, "Nave")
        tabs.addTab(tab_coord, "Coordenadas Iniciales")
        tabs.addTab(tab_orbita, "Órbita")

        layout.addWidget(tabs)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(350, 250)
    window.show()
    sys.exit(app.exec())
