import json
import sys
import os
from PySide6 import QtWidgets, QtCore
from Example_Project.common_widgets import FloatLineEdit
from node_editor.node import Node
sys.path.append("C:/Users/tolle/OneDrive/Рабочий стол/PyThrash")
from Burn3D.modules import CLI
from Burn3D.modules.unit import ureg

PROPELLANT_JSON = "C:/Users/tolle/OneDrive/Рабочий стол/PyThrash/Burn3D/modules/propellants.json"

class Propellant_Node(Node):
    def __init__(self):
        super().__init__()
        self.title_text = "Propellant"
        self.type_text = "Constants"
        self.set_color(title_color=(150, 200, 255))

        self.add_pin(name="data", is_output=True)

        self.propellants = self.load_propellants()

        self.propellant = CLI.set_propellant()

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # === Editable Dropdown for Propellant ===
        self.combo = QtWidgets.QComboBox()
        self.combo.setEditable(True)
        self.combo.addItem("New")
        self.combo.addItems(self.propellants.keys())
        self.combo.currentTextChanged.connect(self.on_propellant_selected)
        layout.addWidget(self.combo)

        # === Editable Float Fields ===
        self.density_line = FloatLineEdit()
        self.density_line.setPlaceholderText("Density (kg/m³)")
        layout.addWidget(self.density_line)

        self.const_line = FloatLineEdit()
        self.const_line.setPlaceholderText("Burning const a (m/(s*Pa^n))")
        layout.addWidget(self.const_line)

        self.exp_line = FloatLineEdit()
        self.exp_line.setPlaceholderText("Exponent n")
        layout.addWidget(self.exp_line)

        self.gamma_line = FloatLineEdit()
        self.gamma_line.setPlaceholderText("Adiabatic coef γ")
        layout.addWidget(self.gamma_line)

        self.temp_line = FloatLineEdit()
        self.temp_line.setPlaceholderText("Temperature T (K)")
        layout.addWidget(self.temp_line)

        self.molar_mass_line = FloatLineEdit()
        self.molar_mass_line.setPlaceholderText("Molar mass (g/mol)")
        layout.addWidget(self.molar_mass_line)

        # === Save Button ===
        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(self.save_current_propellant)
        layout.addWidget(save_button)

        self.widget.setLayout(layout)
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        # connect all editingFinished to a common callback
        for line in [self.density_line, self.const_line, self.exp_line,
                     self.gamma_line, self.temp_line, self.molar_mass_line]:
            line.editingFinished.connect(self.on_any_field_edited)

        self.combo.currentIndexChanged.connect(self.on_any_field_edited)
        self.combo.lineEdit().editingFinished.connect(self.on_any_field_edited)

        super().init_widget()

    # === JSON Load/Save ===
    def load_propellants(self):
        print("Select propellant option")
        if os.path.exists(PROPELLANT_JSON):
            with open(PROPELLANT_JSON, "r") as f:
                return json.load(f)
        return {}

    def save_current_propellant(self):
        name = self.combo.currentText().strip()
        if not name:
            QtWidgets.QMessageBox.warning(None, "Error", "Please enter a name for the propellant.")
            return

        self.propellants[name] = {
            "density": self.density_line.text(),
            "a": self.const_line.text(),
            "n": self.exp_line.text(),
            "gamma": self.gamma_line.text(),
            "T": self.temp_line.text(),
            "M": self.molar_mass_line.text()
        }

        # Save to JSON
        with open(PROPELLANT_JSON, "w") as f:
            json.dump(self.propellants, f, indent=2)

        # Add to dropdown if new
        if self.combo.findText(name) == -1:
            self.combo.addItem(name)

        QtWidgets.QMessageBox.information(None, "Saved", f"Propellant '{name}' saved.")

    # === Dropdown handler ===
    def on_propellant_selected(self, name):
        data = self.propellants.get(name)
        if data:
            self.density_line.setText(str(data.get("density", 0)))
            self.const_line.setText(str(data.get("a", 0)))
            self.exp_line.setText(str(data.get("n", 0)))
            self.gamma_line.setText(str(data.get("gamma", 0)))
            self.temp_line.setText(str(data.get("T", 0)))
            self.molar_mass_line.setText(str(data.get("M", 0)))
        else:
            # Clear fields
            self.density_line.setText(None)
            self.const_line.setText(None)
            self.exp_line.setText(None)
            self.gamma_line.setText(None)
            self.temp_line.setText(None)
            self.molar_mass_line.setText(None)

    # === Global input change callback ===
    def on_any_field_edited(self):
        self.propellant.set_properties(float(self.density_line.text())*ureg('kilogram/meter**3'),
                                       float(self.exp_line.text()),
                                       float(self.const_line.text())*ureg('meter / (second * pascal**0.319)'),
                                       float(self.gamma_line.text()),
                                       float(self.temp_line.text())*ureg('kelvin'),
                                       float(self.molar_mass_line.text())*ureg('gram/mol')
                                    )
        
        print("Propellant data edited.")
        # You can trigger updates here
