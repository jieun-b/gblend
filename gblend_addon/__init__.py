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

from .preferences import (
    GBlendAddonPreferences,
    InstallDependencyOperator,
    UninstallDependencyOperator,
)
from .ui import GBLEND_PT_panel
from .utils import on_gaussian_folder_changed, on_project_folder_changed
from .operators import all_operator_classes

classes = [
    GBlendAddonPreferences,
    InstallDependencyOperator,
    UninstallDependencyOperator,
    GBLEND_PT_panel,
] + all_operator_classes

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.gblend_project_dir = bpy.props.StringProperty(
        name="Project Folder",
        subtype='DIR_PATH',
        description="Root folder of the project",
        update=on_project_folder_changed
    )
    
    bpy.types.Scene.gblend_data_path = bpy.props.StringProperty(
        name="COLMAP Dataset Path",
        subtype='DIR_PATH',
        description="Path to COLMAP formatted dataset (images/, sparse/...)"
    )

    bpy.types.Scene.gblend_scene_setup_mode = bpy.props.EnumProperty(
        name="Scene Setup Mode",
        description="Choose how to provide scene data",
        items=[
            ('GENERATE', "Generate Automatically", ""),
            ('MANUAL', "Use Existing Folder", ""),
        ],
        default='GENERATE',
    )
    
    bpy.types.Scene.gblend_gaussian_output_dir = bpy.props.StringProperty(
        name="Gaussian Output Folder",
        subtype='DIR_PATH',
        description="Path to Gaussian Splatting result (contains point_cloud.ply and cameras.json)",
        update=on_gaussian_folder_changed
    )

    bpy.types.Scene.gblend_ply_path = bpy.props.StringProperty(
        name="PLY Path",
        subtype='FILE_PATH',
        description="Path to the .ply file (for Kiri Engine import)"
    )

    bpy.types.Scene.gblend_camera_path = bpy.props.StringProperty(
        name="Camera JSON Path",
        subtype='FILE_PATH',
        description="Path to camera.json (used internally for camera setup)"
    )
    
    bpy.types.Scene.gblend_search_text = bpy.props.StringProperty(
        name="Search 3D Object",
        description="Search term for Objaverse (CLIP-based)",
        default=""
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.gblend_project_dir
    del bpy.types.Scene.gblend_data_path
    del bpy.types.Scene.gblend_scene_setup_mode
    del bpy.types.Scene.gblend_gaussian_output_dir
    del bpy.types.Scene.gblend_ply_path
    del bpy.types.Scene.gblend_camera_path
    del bpy.types.Scene.gblend_search_text