# gblend_addon/operators/__init__.py
import bpy

from .op_camera_cull import GBLEND_OT_camera_cull_light
from .op_kiri_set_mode import GBLEND_OT_kiri_set_mode
from .op_scene_align import GBLEND_OT_scene_align_to_ground
from .op_camera_add import GBLEND_OT_animated_camera_add
from .op_scene_generate import GBLEND_OT_scene_generate
from .op_kiri_import import GBLEND_OT_kiri_import_direct
from .op_set_scene_mode import GBLEND_OT_set_scene_mode
from .op_render_scene import GBLEND_OT_render_scene

all_operator_classes = [
    GBLEND_OT_camera_cull_light,
    GBLEND_OT_kiri_set_mode,
    GBLEND_OT_scene_align_to_ground,
    GBLEND_OT_animated_camera_add, 
    GBLEND_OT_scene_generate,
    GBLEND_OT_kiri_import_direct,
    GBLEND_OT_set_scene_mode,
    GBLEND_OT_render_scene
]