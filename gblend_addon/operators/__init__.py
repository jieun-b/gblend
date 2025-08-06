# gblend_addon/operators/__init__.py

from .pointcloud_mode import GBLEND_OT_set_point_cloud_mode
from .align_scene import GBLEND_OT_align_scene_to_ground
from .add_cameras import GBLEND_OT_add_cameras
from .generate_scene import GBLEND_OT_generate_scene

all_operator_classes = [
    GBLEND_OT_set_point_cloud_mode,
    GBLEND_OT_align_scene_to_ground,
    GBLEND_OT_add_cameras,
    GBLEND_OT_generate_scene,
]
