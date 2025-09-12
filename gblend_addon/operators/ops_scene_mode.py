import bpy


class GBLEND_OT_scene_mode(bpy.types.Operator):
    """Switch between Render and Edit scene modes for the scene object"""
    bl_idname = "gblend.mode_scene"
    bl_label = "Mode Scene"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('RENDER', "Prepare Render", "Prepare setup for rendering"),
            ('EDIT', "Edit Scene", "Switch to edit mode for the scene object"),
        ],
        default='EDIT'
    )

    @classmethod
    def description(cls, context, properties):
        return {
            'RENDER': "Prepare setup for rendering (HQ, etc)",
            'EDIT': "Switch to edit mode for the scene object (LQ, etc)",
        }.get(getattr(properties, "mode", ""), "Switch between render and edit modes")


    @classmethod
    def poll(cls, context):
        settings = context.scene.gblend_scene_settings
        name = getattr(settings, "scene_name", "")
        return bool(name and bpy.data.objects.get(name))

    def execute(self, context):
        scene = context.scene
        settings = scene.gblend_scene_settings
        obj_name = getattr(settings, "scene_name", "")
        obj = bpy.data.objects.get(obj_name)

        if obj is None:
            self.report({'ERROR'}, "Scene object not found.")
            return {'CANCELLED'}

        # Always set interface mode and Eevee engine
        scene["sna_kiri3dgs_interface_active_sub_interface_mode"] = 4
        try:
            scene.render.engine = (
                'BLENDER_EEVEE_NEXT'
                if any(i.identifier == 'BLENDER_EEVEE_NEXT'
                       for i in scene.render.bl_rna.properties['engine'].enum_items)
                else 'BLENDER_EEVEE'
            )
        except Exception as e:
            self.report({'ERROR'}, f"Eevee 전환 실패: {e}")
            return {'CANCELLED'}

        if self.mode == 'RENDER':
            self._prepare_render(scene, obj)
        else:
            self._prepare_edit(obj)

        # Refresh 3D view
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        settings.render_mode = self.mode
        return {'FINISHED'}

    def _prepare_render(self, scene, obj):
        # Match resolution to camera background image if available
        if scene.camera and hasattr(scene.camera.data, "background_images"):
            for bg in scene.camera.data.background_images:
                if bg.image:
                    scene.render.resolution_x = bg.image.size[0]
                    scene.render.resolution_y = bg.image.size[1]
                    break

        # Material HQ
        if hasattr(obj.active_material, "sna_kiri3dgs_lq__hq"):
            obj.active_material.sna_kiri3dgs_lq__hq = "HQ Mode (Blended Alpha)"
        else:
            self.report({'WARNING'}, "Kiri LQ/HQ 머티리얼 속성을 찾지 못했습니다.")

        # Sampling
        if hasattr(scene.eevee, "taa_samples"):
            scene.eevee.taa_samples = 1
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = 1

        # View transform
        scene.view_settings.view_transform = 'Standard'
        scene.view_settings.look = 'Medium Contrast'

        msg = (
            f"Prepared: {obj.name} | Engine={scene.render.engine} "
            "| HQ | samples=1/1 | ViewTransform=Standard | Look=Medium Contrast"
        )
        self.report({'INFO'}, msg)

    def _prepare_edit(self, obj):
        if hasattr(obj.active_material, "sna_kiri3dgs_lq__hq"):
            obj.active_material.sna_kiri3dgs_lq__hq = "LQ Mode (Dithered Alpha)"
        else:
            self.report({'WARNING'}, "Kiri LQ/HQ 머티리얼 속성을 찾지 못했습니다.")

        msg = f"Prepared: {obj.name} | LQ"
        self.report({'INFO'}, msg)
