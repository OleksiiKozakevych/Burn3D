import sys
import os
from PySide6 import QtWidgets, QtCore
from Example_Project.common_widgets import FloatLineEdit
from node_editor.node import Node
sys.path.append("C:/Users/tolle/OneDrive/Рабочий стол/PyThrash")
from Burn3D.modules import CLI
from Burn3D.modules.unit import ureg

class Nozzle_Node(Node):
    def __init__(self):
        super().__init__()
        self.title_text = "Nozzle"
        self.type_text = "Constants"
        self.set_color(title_color=(150, 200, 255))

        self.add_pin(name="data", is_output=True)

        self.nozzle = CLI.set_nozzle()

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # === Editable Float Fields ===
        self.inner_d = FloatLineEdit()
        self.inner_d.setPlaceholderText("Inner diameter mm")
        layout.addWidget(self.inner_d)

        self.outter_d = FloatLineEdit()
        self.outter_d.setPlaceholderText("Outter diameter mm")
        layout.addWidget(self.outter_d)

        self.widget.setLayout(layout)
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        # connect all editingFinished to a common callback
        for line in [self.inner_d, self.outter_d]:
            line.editingFinished.connect(self.on_any_field_edited)

        super().init_widget()

    # === Global input change callback ===
    def on_any_field_edited(self):
        self.nozzle.set_dimensions(float(self.inner_d.text())*ureg('mm'),
                                   float(self.outter_d.text())*ureg('mm')
                                )
        print("Nozzle data edited.")
        # You can trigger updates here
