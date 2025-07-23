from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, QPointF, QEvent

import sys

from PySide6.QtCore import QObject

class visualize(QObject):
    def __init__(self, solver=None):
        super().__init__()
        self.solver = solver
        self.window = None

    def set_solver(self, solver):
        self.solver = solver

    def show_window(self):
        if self.window is not None:
            self.plot_data()
            self.window.show()
            return

        self.window = QWidget()
        self.window.setWindowTitle("Simulation Results Viewer")
        self.window.setMinimumSize(900, 600)

        layout = QHBoxLayout()
        self.window.setLayout(layout)

        # === Chart Area ===
        self.chart = QChart()
        self.chart.setTitle("Simulation Results")
        self.chart.legend().setVisible(True)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMouseTracking(True)
        self.chart_view.viewport().installEventFilter(self)

        layout.addWidget(self.chart_view, stretch=3)

        # === Right Panel ===
        right_panel = QVBoxLayout()

        self.checkboxes = {}
        self.series_dict = {}

        for key in ["Chamber Pressure", "Thrust Coefficient", "Exit Pressure", "Thrust"]:
            cb = QCheckBox(key)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_chart)
            self.checkboxes[key] = cb
            right_panel.addWidget(cb)

        # Cursor label
        self.coord_label = QLabel("Cursor: X = -, Y = -")
        right_panel.addWidget(self.coord_label)

        right_panel.addStretch()
        layout.addLayout(right_panel, stretch=1)

        self.plot_data()
        self.window.show()

    def plot_data(self):
        if not self.solver:
            return

        results = self.solver.results
        times = [t.magnitude for t in results["Time"]]

        self.chart.removeAllSeries()
        self.series_dict.clear()

        for key in ["Chamber Pressure", "Thrust Coefficient", "Exit Pressure", "Thrust"]:
            series = QLineSeries()
            series.setName(key)
            values = [v.to_base_units().magnitude for v in results[key]]
            for t, y in zip(times, values):
                series.append(t, y)
            self.series_dict[key] = series
            self.chart.addSeries(series)

        self.chart.createDefaultAxes()
        self.update_chart()

    def update_chart(self):
        # Set visibility of series
        for key, cb in self.checkboxes.items():
            if key in self.series_dict:
                self.series_dict[key].setVisible(cb.isChecked())

        # Adjust Y-axis range to visible data
        all_y = []
        for key, series in self.series_dict.items():
            if self.checkboxes[key].isChecked():
                points = [series.at(i).y() for i in range(series.count())]
                all_y.extend(points)

        if all_y:
            min_y = min(all_y)
            max_y = max(all_y)
            y_axis = QValueAxis()
            y_axis.setRange(min_y, max_y * 1.05)
            self.chart.setAxisY(y_axis)
            for series in self.series_dict.values():
                series.attachAxis(y_axis)

    def eventFilter(self, obj, event):
        if obj == self.chart_view.viewport():
            if event.type() == QEvent.MouseMove:
                pos = event.position().toPoint()
                chart_pos = self.chart.mapToValue(pos, self.chart.series()[0]) if self.chart.series() else QPointF(0, 0)
                self.coord_label.setText(f"Cursor: X = {chart_pos.x():.2f}, Y = {chart_pos.y():.2f}")
        return False
