import bpy

class GBLEND_OT_set_scene_mode(bpy.types.Operator):
    bl_idname = "gblend.set_scene_mode"
    bl_label = "Set Scene Mode"
    bl_description = "Switch between Render and Edit scene modes for the scene object"
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
        tip = {
            'RENDER': "Prepare setup for rendering (HQ, etc)",
            'EDIT': "Switch to edit mode for the scene object (LQ, etc)",
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
        obj_name = getattr(settings, "scene_name", "") if settings else ""
        obj = bpy.data.objects.get(obj_name)
        if obj is None:
            self.report({'ERROR'}, "Scene object not found.")
            return {'CANCELLED'}

        # Always set interface mode and Eevee engine
        try:
            scene["sna_kiri3dgs_interface_active_sub_interface_mode"] = 4
        except Exception:
            pass
        try:
            scene.render.engine = (
                'BLENDER_EEVEE_NEXT'
                if any(i.identifier == 'BLENDER_EEVEE_NEXT' for i in scene.render.bl_rna.properties['engine'].enum_items)
                else 'BLENDER_EEVEE'
            )
        except Exception as e:
            self.report({'ERROR'}, f"Eevee 전환 실패: {e}")
            return {'CANCELLED'}

        if self.mode == 'RENDER':
            camera = scene.camera

            if camera and hasattr(camera.data, "background_images"):
                for bg in camera.data.background_images:
                    if bg.image:
                        scene.render.resolution_x = bg.image.size[0]
                        scene.render.resolution_y = bg.image.size[1]
                        break

            try:
                if hasattr(obj.active_material, "sna_kiri3dgs_lq__hq"):
                    obj.active_material.sna_kiri3dgs_lq__hq = "HQ Mode (Blended Alpha)"
                else:
                    self.report({'WARNING'}, "Kiri LQ/HQ 머티리얼 속성을 찾지 못했습니다.")
            except Exception as e:
                self.report({'WARNING'}, f"HQ 전환 실패: {e}")
            try:
                if hasattr(scene.eevee, "taa_samples"):
                    scene.eevee.taa_samples = 1
                if hasattr(scene.eevee, "taa_render_samples"):
                    scene.eevee.taa_render_samples = 1
            except Exception as e:
                self.report({'WARNING'}, f"샘플 설정 실패: {e}")
            try:
                scene.view_settings.view_transform = 'Standard'
                scene.view_settings.look = 'Medium Contrast'

            except Exception:
                pass
            msg = f"Prepared: {obj.name} | Engine={scene.render.engine} | HQ | samples=1/1 | ViewTransform=Standard | Look=Medium Contrast"
        else:  # EDIT mode
            try:
                if hasattr(obj.active_material, "sna_kiri3dgs_lq__hq"):
                    obj.active_material.sna_kiri3dgs_lq__hq = "LQ Mode (Dithered Alpha)"
                else:
                    self.report({'WARNING'}, "Kiri LQ/HQ 머티리얼 속성을 찾지 못했습니다.")
            except Exception as e:
                self.report({'WARNING'}, f"LQ 전환 실패: {e}")
            msg = f"Prepared: {obj.name} | Engine={scene.render.engine} | LQ"

        # Refresh 3D view
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        settings.render_mode = self.mode

        self.report({'INFO'}, msg)
        return {'FINISHED'}
