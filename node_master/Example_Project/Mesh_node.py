import json
import sys
import os
from PySide6 import QtWidgets, QtCore
from Example_Project.common_widgets import FloatLineEdit
from node_editor.node import Node
sys.path.append("C:/Users/tolle/OneDrive/Рабочий стол/PyThrash")
from Burn3D.modules import CLI
from Burn3D.modules.unit import ureg


class Mesh_Node(Node):
    def __init__(self):
        super().__init__()
        self.title_text = "Mesh"
        self.type_text = "Path"
        self.set_color(title_color=(150, 200, 255))

        self.add_pin(name="input_data", is_output=False)
        self.add_pin(name="output_data", is_output=True)

        self.mesh = CLI.set_mesh()

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # === Editable Float Fields ===
        self.resolution = FloatLineEdit()
        self.resolution.setPlaceholderText("Resolution (m)")
        layout.addWidget(self.resolution)

        # === Mesh Button ===
        mesh_button = QtWidgets.QPushButton("Mesh")
        mesh_button.clicked.connect(self.start_meshing)
        layout.addWidget(mesh_button)

        self.widget.setLayout(layout)
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    # === Start meshing ===
    def start_meshing(self):
        self.mesh.set_resolution(float(self.resolution.text())*ureg('meter'))
        grain = self.get_pin("input_data").connection.nodes()[0].grain
        self.mesh.set_grain(grain)
        self.long_task(message="Wait meshing", task=self.mesh.create_mesh)
        #self.mesh.create_mesh()
