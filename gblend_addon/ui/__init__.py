import bpy

from .step1_panel import GBLEND_PT_ProjectPanel
from .step2_panel import GBLEND_PT_ScenePanel
from .step3_panel import GBLEND_PT_CameraPanel
from .step4_panel import GBLEND_PT_ObjectPanel
from .step5_panel import GBLEND_PT_RenderPanel

def register():
    for cls in (
        GBLEND_PT_ProjectPanel,
        GBLEND_PT_ScenePanel,
        GBLEND_PT_CameraPanel,
        GBLEND_PT_ObjectPanel,
        GBLEND_PT_RenderPanel
    ):
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed((
        GBLEND_PT_ProjectPanel,
        GBLEND_PT_ScenePanel,
        GBLEND_PT_CameraPanel,
        GBLEND_PT_ObjectPanel,
        GBLEND_PT_RenderPanel
    )):
        bpy.utils.unregister_class(cls)