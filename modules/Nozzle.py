from .unit import ureg

class nozzle:
    def __init__(self, _dc=None, _do=None):
        self.d_crit = _dc
        self.d_exit = _do
        if (_dc and _do):
            self.A_crit = 3.14 * _dc**2 / 4
            self.A_exit = 3.14 * _do**2 / 4

    def set_dimensions(self, _dc, _do):
        self.d_crit = _dc
        self.d_exit = _do
        self.A_crit = 3.14 * _dc**2 / 4
        self.A_exit = 3.14 * _do**2 / 4
