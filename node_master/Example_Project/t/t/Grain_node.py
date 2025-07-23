from PySide6 import QtWidgets
from Example_Project.common_widgets import FloatLineEdit  # optional if used elsewhere
from node_editor.node import Node
import sys
import os
from nodeeditor.node_graphics_node import QDMGraphicsNode
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
sys.path.append("C:/Users/tolle/OneDrive/Рабочий стол/PyThrash")
from Burn3D.modules import CLI

class Grain_Node(Node):
    def __init__(self) -> None:
        super().__init__()

        self.title_text = "Grain File"
        self.type_text = "Geometry"
        self.set_color(title_color=(180, 255, 180))

        self.grain = CLI.set_grain()

        self.add_pin(name="file", is_output=True)
        
        self.build()

    def init_widget(self) -> None:
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(180)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Button to open file
        self.select_btn = QtWidgets.QPushButton("Select File")
        self.select_btn.clicked.connect(self.select_file)
        layout.addWidget(self.select_btn)

        # Label to show selected file (trimmed)
        self.file_label = QtWidgets.QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(self.file_label)

        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    def select_file(self):
        file_dialog = QtWidgets.QFileDialog()
        path, _ = file_dialog.getOpenFileName(
            None,
            "Select Grain Geometry File",
            os.getcwd(),  # starting directory
            "OBJ Files (*.obj);;All Files (*)"
        )

        if path:
            self.grain.path = path
            self.file_label.setText(os.path.basename(path))
