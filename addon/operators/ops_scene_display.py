import bpy


class GBLEND_OT_scene_display(bpy.types.Operator):
    """Set display mode for imported 3DGS object (Point Cloud / Camera Updates)"""
    bl_idname = "gblend.display_scene"
    bl_label = "Scene Display"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Display Mode",
        items=[
            ('Show As Point Cloud', "Show As Point Cloud", "Display as point cloud"),
            ('Enable Camera Updates', "Enable Camera Updates", "Use object to drive camera updates"),
        ],
        default='Enable Camera Updates'
    )

    @classmethod
    def description(cls, context, properties):
        tips = {
            'Show As Point Cloud': "Display object as point cloud",
            'Enable Camera Updates': "Use object to update animated cameras",
        }
        return tips.get(getattr(properties, "mode", ""), cls.__doc__)


    @classmethod
    def poll(cls, context):
        settings = context.scene.settings
        name = getattr(settings, "scene_name", "")
        return bool(name and bpy.data.objects.get(name))

    def execute(self, context):
        scene = context.scene
        settings = scene.settings

        # Get target object by scene_name property
        obj_name = getattr(settings, "scene_name", "") or ""
        obj = bpy.data.objects.get(obj_name) if obj_name else None

        # If not found, fallback to currently active object
        if obj is None:
            obj = context.object

        if obj is None:
            self.report({'ERROR'}, "No valid object found. Set scene_name or select an object.")
            return {'CANCELLED'}

        # Ensure the object is selected and active
        try:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
        except Exception:
            pass

        # Check Kiri custom property
        if not hasattr(obj, "sna_kiri3dgs_active_object_update_mode"):
            self.report({'ERROR'}, "Target object does not have Kiri 3DGS properties.")
            return {'CANCELLED'}

        # Set display mode
        obj.sna_kiri3dgs_active_object_update_mode = self.mode
        self.report({'INFO'}, f"[{obj.name}] display mode → {self.mode}")
        return {'FINISHED'}
