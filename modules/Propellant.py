from .unit import ureg

class propellant:
    def __init__(self, _rho=None, _n=None, _a=None, _k=None, _T=None, _M=None):
        self.rho = _rho
        self.n = _n
        self.a = _a
        self.k = _k
        self.T = _T
        self.M = _M
        if (_M):
            self.R = 8.314 * ureg('joule / (mol * kelvin)') / _M
            _C = (_a * _rho * (_k/self.R/_T*(2/(_k+1))**((_k+1)/(_k-1)))**-0.5)**(1 / (1 - _n))
            _C = ureg.Quantity(_C.to_base_units().magnitude, ureg.pascal)
            self.C = _C

    def set_properties(self, _rho, _n, _a, _k, _T, _M):
        self.rho = _rho
        self.n = _n
        self.a = _a
        self.k = _k
        self.T = _T
        self.M = _M
        self.R = 8.314 * ureg('joule / (mole * kelvin)') / _M
        if (_M):
            _C = (_a * _rho * (_k/self.R/_T*(2/(_k+1))**((_k+1)/(_k-1)))**-0.5)**(1 / (1 - _n))
            _C = ureg.Quantity(_C.to_base_units().magnitude, ureg.pascal)
            self.C = _C
