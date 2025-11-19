# gblend_addon/operators/__init__.py
import bpy

from .ops_scene_generate import GBLEND_OT_scene_generate
from .ops_scene_import import GBLEND_OT_scene_import
from .ops_scene_display import GBLEND_OT_scene_display
from .ops_camera_cull import GBLEND_OT_camera_cull
from .ops_scene_align import GBLEND_OT_scene_align
from .ops_animated_camera import GBLEND_OT_animated_camera
from .ops_scene_mode import GBLEND_OT_scene_mode
from .ops_scene_render import GBLEND_OT_scene_render
from .ops_object_import import GBLEND_OT_object_import

all_operator_classes = [
    GBLEND_OT_scene_generate,
    GBLEND_OT_scene_import,
    GBLEND_OT_scene_display,
    GBLEND_OT_camera_cull,
    GBLEND_OT_scene_align,
    GBLEND_OT_animated_camera, 
    GBLEND_OT_scene_mode,
    GBLEND_OT_scene_render,
    GBLEND_OT_object_import
]