import json
import sys
import os
from PySide6 import QtWidgets, QtCore
from Example_Project.common_widgets import FloatLineEdit
from node_editor.node import Node
sys.path.append("C:/Users/tolle/OneDrive/Рабочий стол/PyThrash")
from Burn3D.modules import CLI
from Burn3D.modules.unit import ureg
from PySide6.QtCore import QObject, Signal

class Solver_Node(Node):
    def __init__(self):
        super().__init__()
        self.title_text = "Solver"
        self.type_text = "Solver"
        self.set_color(title_color=(150, 200, 255))

        self.add_pin(name="input_mesh", is_output=False)
        self.add_pin(name="input_propellant", is_output=False)
        self.add_pin(name="input_nozzle", is_output=False)
        self.add_pin(name="output_plote", is_output=True)

        self.solver = CLI.set_solver()

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # === Editable Float Fields ===
        self.timestep = FloatLineEdit()
        self.timestep.setPlaceholderText("Timestep (s)")
        layout.addWidget(self.timestep)

        # === Mesh Button ===
        solve_button = QtWidgets.QPushButton("Solve")
        solve_button.clicked.connect(self.start_solver)
        layout.addWidget(solve_button)

        self.widget.setLayout(layout)
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    # === Start simulating ===
    def start_solver(self):
        mesh = self.get_pin("input_mesh").connection.nodes()[0].mesh
        self.solver.set_mesh(mesh)
        propellant = self.get_pin("input_propellant").connection.nodes()[0].propellant
        self.solver.set_propellant(propellant)
        nozzle = self.get_pin("input_nozzle").connection.nodes()[0].nozzle
        self.solver.set_nozzle(nozzle)

        self.long_task(message="Wait simulation", task=self.solver.simulate, param=[float(self.timestep.text())*ureg('second')])
