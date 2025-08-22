import numpy as np
import trimesh
import skfmm
from skimage.measure import marching_cubes
from .unit import ureg
from scipy.optimize import fsolve

class solver:
    def __init__(self, _mesh=None, _propellant=None, _nozzle=None):
        self.mesh = _mesh
        self.propellant = _propellant
        self.nozzle = _nozzle

    def set_mesh(self, _mesh):
        self.mesh = _mesh
    def set_propellant(self, _propellant):
        self.propellant = _propellant
    def set_nozzle(self, _nozzle):
        self.nozzle = _nozzle

    def getExitMach(self):
        expansion_ratio_squared = (self.nozzle.d_exit / self.nozzle.d_crit)**2
        k = self.propellant.k
        f = lambda M: (1/M**2) * (2/(k+1) * (1+(k-1)/2*M**2))**((k+1)/(k-1)) - expansion_ratio_squared
        M0 = 2
        M_exit = fsolve(f, M0)

        return M_exit

    def getExitPressure(self, p1):
        k = self.propellant.k
        M = self.Mach_exit
        p2 = p1 * (1 + (k-1)/2*M**2)**(k/(1-k))

        return p2   

    def simulate(self, _param):
        self.results = {"Time": [],
                        "Chamber Pressure": [],
                        "Thrust Coefficient": [],
                        "Exit Pressure": [],
                        "Thrust": [],
                        "Kn": []
                    }
        
        # Let _param be simulation parameters that include dt
        dt = _param[0]

        # Get Mach number on exit of nozzle
        self.Mach_exit = self.getExitMach()

        globalT = 0.01*ureg('second') # Initial 0.01s added to form starting burn surface
        array = self.mesh.mesh
        resolution = self.mesh.resolution

        def fmm(array, r, dt):
            _dx = resolution.to(ureg.meter).magnitude
            # Constructing speed array
            speed = np.zeros_like(array, dtype=np.float32)
            # air
            speed[array == 0] = 100000000
            #grain
            speed[array == 1] = r

            # Constructing burn array
            # case not burn
            mask = [array == 2]
            # what will burn and what will not
            phi = np.ones_like(array)
            phi[phi.shape[0] // 2, phi.shape[1] // 2, 0] = -1
            phi = np.ma.MaskedArray(phi, mask)
            
            t = skfmm.travel_time(phi, speed, dx=_dx)
            
            return t
        
        # Generate a regression map with isosurfaces regarding time
        refSpeed = 0.005*ureg('meter/second')
        regMap = fmm(array, refSpeed, dt)

        def burnArea(surface):
            verts, faces, normals, values = marching_cubes(surface, level=0.5)
            verts *= self.mesh.resolution
            
            # Step 1: find valid vertices (no NaN or inf)
            valid_mask = np.isfinite(verts).all(axis=1)  # True if each row has no nan/inf
            valid_indices = np.where(valid_mask)[0]

            # Step 2: build mapping from old index to new
            old_to_new = -np.ones(len(verts), dtype=int)  # -1 for invalid
            old_to_new[valid_indices] = np.arange(len(valid_indices))


            # Step 3: remap and filter faces
            faces_remapped = old_to_new[faces]  # use map to remap faces
            faces_valid = (faces_remapped >= 0).all(axis=1)  # keep only fully valid triangles

            # Final clean mesh
            surface = trimesh.Trimesh(
                vertices=verts[valid_mask],
                faces=faces_remapped[faces_valid],
                vertex_normals=normals[valid_mask]
            )
            
            surface_area = surface.area * self.mesh.resolution.units**2

            return surface_area
        
        def Kn(array):
            # Find interface of the burning
            surface = np.array(regMap > globalT).astype(np.float32)
            surface[regMap.mask] = np.nan
            return burnArea(surface) / self.nozzle.A_crit

        def updateResults():
            try:
                P = (self.propellant.C * Kn(array)**(1 / (1 - self.propellant.n))).to_base_units()
            except:
                P = 0*ureg('pascal')
            self.results["Chamber Pressure"].append(P)
            try:
                t = self.results["Time"][-1] + dt
            except:
                t = 0*ureg('second')
            self.results["Time"].append(t)
            p2 = self.getExitPressure(self.results["Chamber Pressure"][-1])
            self.results["Exit Pressure"].append(p2)
            k = self.propellant.k
            Cf = (2*k**2/(k - 1) * (2/(k+1))**((k+1)/(k-1)) * (1 - (self.results["Exit Pressure"][-1]/self.results["Chamber Pressure"][-1])**((k-1)/k)))**0.5 + (self.results["Exit Pressure"][-1] - 100000*ureg('pascal'))/self.results["Chamber Pressure"][-1] * self.nozzle.A_exit / self.nozzle.A_crit
            self.results["Thrust Coefficient"].append(Cf)
            T = self.results["Thrust Coefficient"][-1] * self.results["Chamber Pressure"][-1] * self.nozzle.A_crit
            self.results["Thrust"].append(T) 

        updateResults()

        while True:
            r = (self.propellant.a * self.results["Chamber Pressure"][-1]**self.propellant.n).to_base_units()
            print(self.results["Time"][-1])
            localT = r / refSpeed * dt
            globalT += localT
            burned = np.array(regMap <= globalT).astype(np.uint8)
            burned[array == 2] = 2
            array[burned == 1] = 0

            #if (np.sum(array == 1) == 0):
            print(self.results["Chamber Pressure"][-1].to_base_units().magnitude)
            if (self.results["Chamber Pressure"][-1].to_base_units().magnitude < 100000):
                updateResults()                
                break

            updateResults()
