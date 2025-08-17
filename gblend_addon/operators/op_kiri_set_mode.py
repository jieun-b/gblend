import bpy

class GBLEND_OT_kiri_set_mode(bpy.types.Operator):
    bl_idname = "gblend.set_kiri_mode"
    bl_label = "Set Kiri 3DGS Mode"
    bl_description = "Set Kiri Engine 'active_object_update_mode' for the imported 3DGS object"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('Show As Point Cloud', "Show As Point Cloud", "Display as point cloud"),
            ('Enable Camera Updates', "Enable Camera Updates", "Use object to drive camera updates"),
        ],
        default='Enable Camera Updates'
    )

    @classmethod
    def description(cls, context, properties):
        tip = {
            'Show As Point Cloud': "Display object as point cloud in Kiri Engine",
            'Enable Camera Updates': "Enable camera updates from this object",
        }
        return tip.get(getattr(properties, "mode", ""), cls.bl_description)

    @classmethod
    def poll(cls, context):
        settings = context.scene.gblend_scene_settings
        name = getattr(settings, "scene_name", "")
        return bool(name and bpy.data.objects.get(name))

    def execute(self, context):
        scene = context.scene
        settings = scene.gblend_scene_settings

        # 1) Use scene.gblend_scene_settings.scene_name as the object name
        obj_name = getattr(settings, "scene_name", "") or ""
        obj = bpy.data.objects.get(obj_name) if obj_name else None

        # 2) If not found, use the currently active object as a fallback
        if obj is None:
            obj = context.object

        if obj is None:
            self.report({'ERROR'}, "대상 오브젝트를 찾지 못했습니다. Scene.gblend_scene_settings.scene_name을 설정하거나 오브젝트를 선택하세요.")
            return {'CANCELLED'}

        # Ensure the object is selected and active
        try:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
        except Exception:
            pass  # Ignore if selection fails

        # Set Kiri Engine custom property
        if not hasattr(obj, "sna_kiri3dgs_active_object_update_mode"):
            self.report({'ERROR'}, "Kiri Engine 속성이 오브젝트에 없습니다. Kiri 3DGS로 임포트된 오브젝트인지 확인하세요.")
            return {'CANCELLED'}

        obj.sna_kiri3dgs_active_object_update_mode = self.mode
        self.report({'INFO'}, f"[{obj.name}] mode → {self.mode}")
        return {'FINISHED'}