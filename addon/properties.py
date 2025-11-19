# gblend_addon/properties.py
import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, EnumProperty, IntProperty

from .utils import on_gaussian_dir_changed, on_project_folder_changed, update_selected_camera, camera_enum_items, on_data_dir_changed

class PathsProps(PropertyGroup):
    project_root: StringProperty(
        name="Project Root",
        subtype='DIR_PATH',
        description="Root directory of the project",
        update=on_project_folder_changed
    )
    data_dir: StringProperty(
        name="Dataset Folder",
        subtype='DIR_PATH',
        description="Directory containing COLMAP dataset",
        update=on_data_dir_changed
    )
    scene_dir: StringProperty(
        name="3DGS_Scene Folder",
        description="Directory for Gaussian Splatting scene",
        subtype='DIR_PATH',
        update=on_gaussian_dir_changed
    )
    output_dir: StringProperty(
        name="Output Folder",
        description="Directory to save generated results",
        subtype='DIR_PATH',
        default=""
    )
    ply_path: StringProperty(
        name="PLY Path",
        subtype='FILE_PATH',
        description="PLY file path for Kiri Engine import"
    )
    camera_path: StringProperty(
        name="Camera JSON Path",
        subtype='FILE_PATH',
        description="Path to cameras.json for camera setup"
    )


class SettingsProps(PropertyGroup):
    scene_setup_mode: EnumProperty(
        name="Scene Setup Mode",
        description="Method for providing scene data",
        items=[
            ('GENERATE', "Generate Automatically", ""),
            ('MANUAL', "Use Existing Folder", ""),
        ],
        default='GENERATE',
    )
    scene_name: StringProperty(
        name="Scene Object Name",
        description="Name for the imported PLY object",
        default=""
    )
    import_object_name: StringProperty(
        name="Import Object Name",
        description="Name of the object to download or place in the scene",
        default=""
    )
    start_camera: bpy.props.EnumProperty(
        name="Start Camera",
        items=camera_enum_items,
        update=update_selected_camera
    )
    end_camera: bpy.props.EnumProperty(
        name="End Camera",
        items=camera_enum_items,
        update=update_selected_camera
    )
    interpolation_frames: IntProperty(
        name="Interpolation Frames",
        description="Frames to insert between camera keyframes",
        default=10, min=0
    )
    render_mode: EnumProperty(
        name="Render Mode",
        items=[
            ('EDIT', "Edit/Preview", ""),
            ('RENDER', "Prepare Render", ""),
        ],
        default='EDIT'
    )
    gaussian_url: bpy.props.StringProperty(
        name="3DGS URL",
        default="http://localhost:8000",
        description="Server endpoint for Gaussian Splatting",
    )
    grounded_sam_url: bpy.props.StringProperty(
        name="Grounded SAM URL",
        default="http://localhost:8001",
        description="Server endpoint for Grounded SAM used to estimate ground plane",
    )
    object_import_url: bpy.props.StringProperty(
        name="Object Import URL",
        default="http://localhost:8002",
        description="Server endpoint for downloading GLB objects",
    )
    save_rgb: bpy.props.BoolProperty(
        name="Save RGB",
        default=True,
        description="Save RGB images"
    )
    save_depth: bpy.props.BoolProperty(
        name="Save Depth",
        default=False,
        description="Save depth maps"
    )
    save_segmentation: bpy.props.BoolProperty(
        name="Save Segmentation",
        default=False,
        description="Save object/material segmentation masks"
    )

_classes = (
    PathsProps,
    SettingsProps,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.paths = bpy.props.PointerProperty(type=PathsProps)
    bpy.types.Scene.settings  = bpy.props.PointerProperty(type=SettingsProps)

def unregister():
    del bpy.types.Scene.settings
    del bpy.types.Scene.paths

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
