import bpy

from .project_panel import GBLEND_PT_ProjectPanel
from .scene_panel import GBLEND_PT_ScenePanel
from .splats_panel import GBLEND_PT_SplatsPanel
from .camera_panel import GBLEND_PT_CameraPanel
from .adjust_panel import GBLEND_PT_SceneAdjustPanel
from .render_panel import GBLEND_PT_RenderPanel

def register():
    for cls in (
        GBLEND_PT_ProjectPanel,
        GBLEND_PT_ScenePanel,
        GBLEND_PT_SplatsPanel,
        GBLEND_PT_CameraPanel,
        GBLEND_PT_SceneAdjustPanel,
        GBLEND_PT_RenderPanel
    ):
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed((
        GBLEND_PT_ProjectPanel,
        GBLEND_PT_ScenePanel,
        GBLEND_PT_SplatsPanel,
        GBLEND_PT_CameraPanel,
        GBLEND_PT_SceneAdjustPanel,
        GBLEND_PT_RenderPanel
    )):
        bpy.utils.unregister_class(cls)