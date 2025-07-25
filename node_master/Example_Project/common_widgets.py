from __future__ import annotations

from typing import Optional
from typing import Tuple

from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class FloatLineEdit(QtWidgets.QLineEdit):  # type: ignore
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        #self.setValidator(FloatValidator())

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:
            event.ignore()
        else:
            super().keyPressEvent(event)


class FloatValidator(QtGui.QDoubleValidator):  # type: ignore
    def __init__(self, parent: Optional[QtGui.QObject] = None) -> None:
        super().__init__(parent)

    def validate(self, input_str: str, pos: int) -> Tuple[QtGui.QValidator.State, str, int]:
        if input_str == "":
            return QtGui.QValidator.Intermediate, input_str, pos  # дозволяємо пусте поле
        state, num, pos = super().validate(input_str, pos)
        if state == QtGui.QValidator.Acceptable:
            return QtGui.QValidator.Acceptable, num, pos
        if str(num).count(".") > 1:
            return QtGui.QValidator.Invalid, num, pos
        if input_str[pos - 1] == ".":
            return QtGui.QValidator.Acceptable, num, pos
        return QtGui.QValidator.Invalid, num, pos
