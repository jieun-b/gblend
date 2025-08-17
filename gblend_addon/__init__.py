# gblend_addon/__init__.py

bl_info = {
    "name": "GBlend Addon",
    "author": "Jieun Bae",
    "version": (0, 0, 1),
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > GBlend",
    "description": "3D Gaussian Splatting Scene Synthesis",
    "category": "3D View",
}

import bpy

from . import ui
from . import properties
from .preferences import (
    GBlendAddonPreferences,
    InstallDependencyOperator,
    UninstallDependencyOperator,
)
from .operators import all_operator_classes

classes = [
    GBlendAddonPreferences,
    InstallDependencyOperator,
    UninstallDependencyOperator,
] + all_operator_classes


def register():
    properties.register()
    ui.register()
    for cls in all_operator_classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(all_operator_classes):
        bpy.utils.unregister_class(cls)
    ui.unregister()
    properties.unregister()