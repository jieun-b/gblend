import bpy
import os

class GBLEND_OT_render_scene(bpy.types.Operator):
    bl_idname = "gblend.render_scene"
    bl_label = "Render Scene"
    bl_description = "Render the scene using the active camera and output directory"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = getattr(scene, 'gblend_scene_settings', None)
        return (
            settings is not None and
            getattr(settings, 'render_mode', None) == 'RENDER' and
            scene.camera is not None
        )

    def execute(self, context):
        scene = context.scene
        paths = scene.gblend_project_paths
        
        output_dir = paths.output_dir

        # Fallback logic for output directory
        if not output_dir:
            blend_path = bpy.data.filepath
            if blend_path:
                output_dir = os.path.join(os.path.dirname(blend_path), "output")
            else:
                output_dir = bpy.app.tempdir or bpy.utils.resource_path('USER')
        else:
            os.makedirs(output_dir, exist_ok=True)
            
        # Set Blender's output path
        scene.render.filepath = output_dir + os.sep

        try:
            bpy.ops.render.render(animation=True, write_still=True)
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Rendered to {output_dir}")
        return {'FINISHED'}