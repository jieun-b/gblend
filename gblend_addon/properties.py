# gblend_addon/properties.py
import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, EnumProperty, IntProperty

from .utils import on_gaussian_folder_changed, on_project_folder_changed

class GBlendProjectPathsProps(PropertyGroup):
    project_root: StringProperty(
        name="Project Root",
        subtype='DIR_PATH',
        description="Root directory of the project",
        update=on_project_folder_changed
    )
    data_dir: StringProperty(
        name="COLMAP Dataset Folder",
        subtype='DIR_PATH',
        description="Directory containing COLMAP dataset",
    )
    gs_output_dir: StringProperty(
        name="GS Output Folder",
        description="Directory for Gaussian Splatting output",
        subtype='DIR_PATH',
        update=on_gaussian_folder_changed
    )
    output_dir: StringProperty(
        name="Render Output Folder",
        description="Directory to save rendered images or videos",
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


class GBlendSceneSettingsProps(PropertyGroup):
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
    frame_start: IntProperty(
        name="Frame Start",
        description="Start frame for animated camera",
        default=1,
        min=1
    )
    frame_end: IntProperty(
        name="Frame End",
        description="End frame for animated camera",
        min=1
    )
    stride: IntProperty(
        name="Keyframe Stride",
        description="Insert keyframes every Nth camera pose",
        default=10, min=1
    )
    interpolation_frames: IntProperty(
        name="Interpolation Frames",
        description="Frames to insert between camera keyframes",
        default=0, min=0
    )
    render_mode: EnumProperty(
        name="Render Mode",
        items=[
            ('EDIT', "Edit/Preview", ""),
            ('RENDER', "Prepare Render", ""),
        ],
        default='EDIT'
    )
    
_classes = (
    GBlendProjectPathsProps,
    GBlendSceneSettingsProps,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gblend_project_paths = bpy.props.PointerProperty(type=GBlendProjectPathsProps)
    bpy.types.Scene.gblend_scene_settings  = bpy.props.PointerProperty(type=GBlendSceneSettingsProps)

def unregister():
    del bpy.types.Scene.gblend_scene_settings
    del bpy.types.Scene.gblend_project_paths

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
