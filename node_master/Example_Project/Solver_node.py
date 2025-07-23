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

class Worker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, func, param):
        super().__init__()
        self.func = func  # your long-running function
        self.param = param

    def run(self):
        try:
            self.func(self.param)  # call your meshing/solving function
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class PleaseWaitDialog(QDialog):
    def __init__(self, message="Please wait..."):
        super().__init__()
        self.setWindowTitle("Working")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
        
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
        #self.solver.simulate([float(self.timestep.text())*ureg('second'), ])
        #dialog = PleaseWaitDialog("Meshing in progress...")
        #dialog.show()
        #worker.finished.connect(dialog.accept)  # closes the dialog

        # Step 1: Create thread and worker
        #from PySide6.QtCore import QThread
        #thread = QThread()
        #worker = Worker(self.solver.simulate, [float(self.timestep.text())*ureg('second'), ])  # pass your actual function here
        #worker.moveToThread(thread)

        # Step 2: Connect signals
        #thread.started.connect(worker.run)
        #worker.finished.connect(dialog.accept)
        #worker.finished.connect(thread.quit)
        #worker.finished.connect(worker.deleteLater)
        #thread.finished.connect(thread.deleteLater)

        # Optional: handle errors
        #def show_error(msg):
        #    dialog.reject()
        #    QMessageBox.critical(None, "Error", msg)

        #worker.error.connect(show_error)

        # Step 3: Start the thread
        #thread.start()

        # Step 4: Execute the dialog modally
        #dialog.exec()
