from . import Grain
import trimesh
import numpy as np
from .unit import ureg

class mesh:
    def __init__(self, _grain = None, _resolution = None):
        self.grain = _grain
        self.resolution = _resolution

    def set_grain(self, _grain):
        # Check if right type provided
        #if (type(_grain) == type(Grain.grain)):
        self.grain = _grain
        #else:
        #    raise ImportError("Wrong grain provided")

    def set_resolution(self, _resolution):
        self.resolution = _resolution

    def create_mesh(self, param):
        resolution_m = self.resolution.to(ureg.meter).magnitude
        # Check if mesh already exist
        self.path = "{}{}.npy".format(self.grain.path, resolution_m)
        print(self.path)
        try:
            self.mesh = np.load(self.path)
        except:
            scene = trimesh.load(self.grain.path, force='scene')
            meshes = []
            for i, (name, mesh) in enumerate(scene.geometry.items()):
                vg = np.asarray(mesh.voxelized(resolution_m).fill().encoding.dense).astype(int)
                meshes.append(vg)

            objects = {
                "case": [],
                "grain": []
                }

            if (meshes[0].size > meshes[1].size):
                meshes[0][meshes[0] == 1] = 2
                objects["case"] = meshes[0]
                objects["grain"] = meshes[1]
            else:
                meshes[1][meshes[1] == 1] = 2
                objects["case"] = meshes[1]
                objects["grain"] = meshes[0]

            x_offset = round((objects["case"].shape[0] - objects["grain"].shape[0]) / 2)
            y_offset = round((objects["case"].shape[1] - objects["grain"].shape[1]) / 2)
            z_offset = objects["case"].shape[2] - objects["grain"].shape[2]

            fmesh = objects["case"]
            for i in range(objects["grain"].shape[0]):
                for j in range(objects["grain"].shape[1]):
                    for k in range(objects["grain"].shape[2]):
                        if (objects["grain"][i][j][k] == 1):
                            fmesh[i + x_offset][j + y_offset][k + z_offset] = 1

            np.save("{}".format(self.path), fmesh)

            self.mesh = fmesh
