import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view


class GBLEND_OT_camera_cull(bpy.types.Operator):
    """Cull mesh faces not visible from the animated camera over sampled frames"""
    bl_idname = "gblend.cull_camera"
    bl_label = "Camera Cull"
    bl_options = {'REGISTER', 'UNDO'}

    padding: bpy.props.FloatProperty(
        name="Padding (NDC)", default=0.20, min=0.0, max=0.5
    )
    closer_than_m: bpy.props.FloatProperty(
        name="Closer Than (m)", default=0.0, min=0.0
    )
    sample_frames: bpy.props.IntProperty(
        name="Sample Frames", default=5, min=3, max=9
    )
    use_timeline_range: bpy.props.BoolProperty(
        name="Use Timeline Range", default=True
    )

    @classmethod
    def poll(cls, context):
        scene_name = getattr(context.scene.gblend_scene_settings, "scene_name", "")
        return bool(scene_name and scene_name in bpy.data.objects)

    def execute(self, context):
        scene = context.scene
        settings = scene.gblend_scene_settings

        cam = bpy.data.objects.get("Animated Camera")
        if cam and cam.type == 'CAMERA':
            scene.camera = cam
            self.report({'INFO'}, f"Scene camera set to {cam.name}")
        else:
            self.report({'WARNING'}, "Animated Camera not found or not a camera object")
            cam = scene.camera
        if cam is None or cam.type != 'CAMERA':
            self.report({'ERROR'}, "No valid camera to cull with.")
            return {'CANCELLED'}

        obj_name = getattr(settings, "scene_name", "") or ""
        obj = bpy.data.objects.get(obj_name) if obj_name else context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "대상 오브젝트를 찾지 못했습니다.")
            return {'CANCELLED'}

        try:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            obj.sna_kiri3dgs_active_object_enable_active_camera = True
        except Exception:
            pass

        me = obj.data

        f0, f1 = int(scene.frame_start), int(scene.frame_end)
        if not self.use_timeline_range:
            f1 = f0 + self.sample_frames - 1
        n = max(3, int(self.sample_frames))
        frames = [int(round(f0 + i * (f1 - f0) / (n - 1))) for i in range(n)]

        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        if not bm.faces:
            bm.free()
            self.report({'INFO'}, "No faces to cull.")
            return {'CANCELLED'}

        obj_mw = obj.matrix_world
        xmin, xmax = -self.padding, 1.0 + self.padding
        ymin, ymax = -self.padding, 1.0 + self.padding

        near, far = cam.data.clip_start, cam.data.clip_end
        pad_near = max(self.closer_than_m, 0.2 * near)
        pad_far = 0.05 * far

        visible_face = [False] * len(bm.faces)

        for fr in frames:
            scene.frame_set(fr)
            cam_inv = cam.matrix_world.inverted()

            for fi, f in enumerate(bm.faces):
                if visible_face[fi]:
                    continue
                for v in f.verts:
                    w = obj_mw @ v.co
                    z_cam = -(cam_inv @ w).z
                    if z_cam < max(self.closer_than_m, near - pad_near):
                        continue
                    if z_cam > (far + pad_far):
                        continue
                    ndc = world_to_camera_view(scene, cam, w)
                    if xmin <= ndc.x <= xmax and ymin <= ndc.y <= ymax:
                        visible_face[fi] = True
                        break

        culled = [f for fi, f in enumerate(bm.faces) if not visible_face[fi]]
        if culled:
            bmesh.ops.delete(bm, geom=culled, context='FACES')

        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')

        bm.to_mesh(me)
        bm.free()
        me.update()

        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        self.report(
            {'INFO'},
            f"CameraCull(light): removed {len(culled)} faces "
            f"(frames={frames}, pad={self.padding}, near={self.closer_than_m}m)"
        )
        return {'FINISHED'}
