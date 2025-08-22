import json
import sys
import os
from PySide6 import QtWidgets, QtCore
from Example_Project.common_widgets import FloatLineEdit
from node_editor.node import Node
sys.path.append("C:/Users/tolle/OneDrive/Рабочий стол/PyThrash")
from Burn3D.modules import CLI
from Burn3D.modules.unit import ureg


class Plotter_Node(Node):
    def __init__(self):
        super().__init__()
        self.title_text = "Plotter"
        self.type_text = "Plote"
        self.set_color(title_color=(150, 200, 255))

        self.add_pin(name="input_data", is_output=False)

        self.plot = CLI.set_visualize()

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # === Plote Button ===
        plote_button = QtWidgets.QPushButton("Plote")
        plote_button.clicked.connect(self.start_plote)
        layout.addWidget(plote_button)

        self.widget.setLayout(layout)
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    # === Start meshing ===
    def start_plote(self):
        solver = self.get_pin("input_data").connection.nodes()[0].solver
        self.plot.set_solver(solver)
        self.plot.show_window()
        
