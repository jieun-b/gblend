import bpy

class GBLEND_PT_ObjectPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_object_panel"
    bl_label = "Step 4: Object Placement"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.gblend_scene_settings
        
        box = layout.box()
        box.prop(settings, "import_object_name", text="Search")
        box.operator("gblend.import_object", text="Download & Place")