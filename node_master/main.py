from __future__ import annotations

import re
import json
import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

import qdarktheme
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import QByteArray  # Or from PySide2.QtCore import QByteArray

from node_editor.compute_graph import compute_dag_nodes
from node_editor.connection import Connection
from node_editor.gui.node_list import NodeList
from node_editor.gui.node_widget import NodeWidget
from node_editor.node import Node
from PySide6.QtWidgets import (
    QDialog, QLabel, QComboBox, QVBoxLayout, QDialogButtonBox, QApplication, QHBoxLayout
)

logging.basicConfig(level=logging.DEBUG)

"""
A simple Node Editor application that allows the user to create, modify and connect nodes of various types.

The application consists of a main window that contains a splitter with a Node List and a Node Widget. The Node List
shows a list of available node types, while the Node Widget is where the user can create, edit and connect nodes.

This application uses PySide6 as a GUI toolkit.

Author: Bryan Howard
Repo: https://github.com/bhowiebkr/simple-node-editor
"""

class MultiUnitSelectDialog(QDialog):
    def __init__(self, parent=None, default_units=None):
        super().__init__(parent)
        self.setWindowTitle("Select Units")

        self.unit_fields = {
            "Length": ["m", "mm", "cm", "ft", "in"],
            "Volume": ["m^3", "mm^3", "cm^3", "ft^3", "in^3"],
            "Velocity": ["m/s", "mm/s", "cm/s", "ft/s", "in/s"],
            "Force": ["N", "lbf"],
            "Impulse": ["N*s", "lbf*s"],
            "Pressure": ["Pa", "MPa", "psi"],
            "Mass": ["kg", "g", "lb", "oz"],
            "Density": ["kg/m^3", "g/cm^3", "lb/in^3"],
            "Mass Flow": ["kg/s", "g/s", "lb/s", "oz/s"],
            "Burn Rate Coefficient": ["m/(s*Pa^n)", "in/(s*psi^n)"]
        }

        self.combos = {}
        layout = QVBoxLayout()

        for label_text, unit_list in self.unit_fields.items():
            row = QHBoxLayout()
            label = QLabel(f"{label_text}:")
            combo = QComboBox()
            combo.addItems(unit_list)

            # Pre-selected units if saved
            if default_units and label_text in default_units:
                saved_unit = default_units[label_text]
                if saved_unit in unit_list:
                    combo.setCurrentText(saved_unit)
                    
            row.addWidget(label)
            row.addWidget(combo)
            layout.addLayout(row)
            self.combos[label_text] = combo

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def selected_units(self):
        return {key: combo.currentText() for key, combo in self.combos.items()}

class NodeEditor(QtWidgets.QMainWindow):  # type: ignore
    OnProjectPathUpdate = QtCore.Signal(Path)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.settings: Optional[QtCore.QSettings] = None
        self.project_path: Optional[Path] = None
        self.imports: Optional[Dict[str, Dict[str, Any]]] = (
            None  # we will store the project import node types here for now.
        )

        icon = QtGui.QIcon("resources\\app.ico")
        self.setWindowIcon(icon)

        self.setWindowTitle("Simple Node Editor")
        settings = QtCore.QSettings("node-editor", "NodeEditor")

        # create a "File" menu and add an "Export CSV" action to it
        file_menu = QtWidgets.QMenu("File", self)
        self.menuBar().addMenu(file_menu)

        load_action = QtGui.QAction("Load Project", self)
        load_action.triggered.connect(self.get_project_path)
        file_menu.addAction(load_action)

        save_action = QtGui.QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        # create "Preferences"
        preferences_menu = QtWidgets.QMenu("Preferences", self)
        self.menuBar().addMenu(preferences_menu)

        units_action = QtGui.QAction("Units", self)
        units_action.triggered.connect(self.choose_units)
        preferences_menu.addAction(units_action)

        self.unit_dict = {
            # Length
            "m": "meter",
            "mm": "millimeter",
            "cm": "centimeter",
            "ft": "foot",
            "in": "inch",

            # Time
            "s": "second",

            # Mass
            "kg": "kilogram",
            "g": "gram",
            "lb": "pound",
            "oz": "ounce",

            # Force
            "N": "newton",
            "lbf": "pound_force",

            # Pressure
            "Pa": "pascal",
            "MPa": "megapascal",
            "psi": "psi"
        }

        # Layouts
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Widgets
        self.node_list: NodeList = NodeList(self)
        left_widget = QtWidgets.QWidget()
        self.splitter: QtWidgets.QSplitter = QtWidgets.QSplitter()
        execute_button = QtWidgets.QPushButton("Execute Graph")
        execute_button.setFixedHeight(40)
        execute_button.clicked.connect(self.execute_graph)
        self.node_widget: NodeWidget = NodeWidget(self)

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
        left_layout.addWidget(execute_button)
        main_layout.addWidget(self.splitter)

        # Load the example project
        example_project_path = Path(__file__).parent.resolve() / "Example_project"
        self.load_project(example_project_path)

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(QByteArray(settings.value("geometry")))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

    def execute_graph(self) -> None:
        print("Executing Graph:")

        # Get a list of the nodes in the view
        nodes = self.node_widget.scene.get_items_by_type(Node)
        edges = self.node_widget.scene.get_items_by_type(Connection)
        # sort them
        compute_dag_nodes(nodes, edges)

    def save_project(self) -> None:
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("JSON files (*.json)")
        file_path, _ = file_dialog.getSaveFileName()
        self.node_widget.save_project(file_path)

    def load_project(self, project_path: Optional[Path] = None) -> None:
        if not project_path:
            return

        project_path = Path(project_path)
        if project_path.exists() and project_path.is_dir():
            self.project_path = project_path

            self.imports = {}

            for file in project_path.glob("*.py"):
                if not file.stem.endswith("_node"):
                    print("file:", file.stem)
                    continue
                spec = importlib.util.spec_from_file_location(file.stem, file)  # type: ignore
                module = importlib.util.module_from_spec(spec)  # type: ignore
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if not name.endswith("_Node"):
                        continue
                    if inspect.isclass(obj):
                        self.imports[obj.__name__] = {"class": obj, "module": module}
                        # break

            self.node_list.update_project(self.imports)

            # work on just the first json file. add the ablitity to work on multiple json files later
            for json_path in project_path.glob("*.json"):
                self.node_widget.load_scene(str(json_path), self.imports)
                break

    def get_project_path(self) -> None:
        project_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Project Folder", "")
        if not project_path:
            return

        self.load_project(Path(project_path))

    def choose_units(self):
        app = QApplication.instance() or QApplication(sys.argv)
        path = "preferences.json"

        # Load saved units
        default_units = {}
        with open(path, "r") as f:
            try:
                preferences = json.load(f)
                default_units = preferences["units"]
            except json.JSONDecodeError:
                print("Error reading preferences.json, using defaults.")
                
        dialog = MultiUnitSelectDialog(default_units=default_units)
        if dialog.exec() == QDialog.Accepted:
            units = dialog.selected_units()
            units = {"units" : units}
            with open(path, "w") as f:
                json.dump(units, f, indent=4)
            #units_pint = {}
            #for _, key in enumerate(units["units"]):
            #    print(units["units"])
            #    pattern = re.compile("|".join(re.escape(k) for k in self.unit_dict.keys()))
            #    result_pint = pattern.sub(lambda m: self.unit_dict[m.group(0)], units["units"][key])
            #    units_pint[key] = result_pint
            #print(units_pint)
        else:
            print("Selection canceled.")
            return None

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Handles the close event by saving the GUI state and closing the application.

        Args:
            event: Close event.

        Returns:
            None.
        """

        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    qdarktheme.setup_theme()

    launcher = NodeEditor()
    launcher.show()
    app.exec()
    sys.exit()
