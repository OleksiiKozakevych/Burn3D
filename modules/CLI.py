from . import Grain
from . import Mesh
from . import Propellant
from . import Nozzle
from . import Solver
from . import Visualize
from .unit import ureg

def set_grain(path=None):
    grain = Grain.grain(path)
    return grain

def set_mesh(grain=None, resolution=None):
    mesh = Mesh.mesh(grain, resolution)
    return mesh

def set_propellant(rho=None, n=None, a=None, k=None, T=None, M=None):
    propellant = Propellant.propellant(rho, n, a, k, T, M)
    return propellant

def set_nozzle(d_crit=None, d_out=None):
    nozzle = Nozzle.nozzle(d_crit, d_out)
    return nozzle

def set_solver(mesh=None, propellant=None, nozzle=None):
    solver = Solver.solver(mesh, propellant, nozzle)
    return solver

def set_visualize(solver=None):
    vis = Visualize.visualize(solver)
    return vis
