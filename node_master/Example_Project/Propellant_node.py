import json
from pathlib import Path
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

        current_file = Path(__file__)
        parent_dir = current_file.parent.parent
        self.preferences_json = parent_dir / "preferences.json"
        with open(self.preferences_json, "r") as f:
            self.preferences = json.load(f)

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
        self.density_line.setPlaceholderText("Density ({})".format(self.preferences["units"]["Density"]))
        layout.addWidget(self.density_line)

        self.const_line = FloatLineEdit()
        self.const_line.setPlaceholderText("Burning const a ({})".format(self.preferences["units"]["Burn Rate Coefficient"]))
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
            "density": self.density_line.text() +" "+ str(ureg.parse_units(self.preferences["units"]["Density"])).replace(" ", ""),
            "a": self.const_line.text() +" "+ str(ureg.parse_units(self.preferences["units"]["Burn Rate Coefficient"].replace("^n", "^"+self.exp_line.text()))).replace(" ", ""),
            "n": self.exp_line.text(),
            "gamma": self.gamma_line.text(),
            "T": self.temp_line.text() +" "+ str('kelvin'),
            "M": self.molar_mass_line.text() +" "+ str('gram/mol')
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
        # Check is nuw inits set
        with open(self.preferences_json, "r") as f:
            self.preferences = json.load(f)
            
        def converted_units(var, units):
            var = ureg(var)
            if (units == "Burn Rate Coefficient"):
                converted = var.to(self.preferences["units"][units].replace("^n", "^"+str(data.get("n", 0))))
                print(self.preferences["units"][units].replace("^n", "**"+str(data.get("n", 0))))
            else:
                converted = var.to(self.preferences["units"][units])
            print(converted)
            value = str(converted.magnitude)
            return value

        print(self.propellants)
        data = self.propellants.get(name)
        print(data)
        print(name)
        print(converted_units(str(data.get("density", 0)), "Density"))
        if data:
            density = converted_units(str(data.get("density", 0)), "Density")
            self.density_line.setText(density)
            a = converted_units(str(data.get("a", 0)), "Burn Rate Coefficient")
            self.const_line.setText(a)
            self.exp_line.setText(str(data.get("n", 0)))
            self.gamma_line.setText(str(data.get("gamma", 0)))
            self.temp_line.setText(str(ureg(str(data.get("T", 0))).magnitude))
            self.molar_mass_line.setText(str(ureg(str(data.get("M", 0))).magnitude))
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
        print(self.preferences)
        self.propellant.set_properties(float(self.density_line.text())*ureg.parse_units(self.preferences["units"]["Density"]),
                                       float(self.exp_line.text()),
                                       float(self.const_line.text())*ureg.parse_units(self.preferences["units"]["Burn Rate Coefficient"].replace("^n", "^"+self.exp_line.text())),
                                       float(self.gamma_line.text()),
                                       float(self.temp_line.text())*ureg('kelvin'),
                                       float(self.molar_mass_line.text())*ureg('gram/mol')
                                    )
        
        print("Propellant data edited.")
        # You can trigger updates here
