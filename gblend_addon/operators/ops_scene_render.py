import bpy
import os

class GBLEND_OT_scene_render(bpy.types.Operator):
    """Render the scene with selected output types"""
    bl_idname = "gblend.render_scene"
    bl_label = "Render Scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = getattr(scene, 'gblend_scene_settings', None)
        return (
            settings
            and getattr(settings, 'render_mode', '') == 'RENDER'
            and scene.camera is not None
        )

    def execute(self, context):
        scene = context.scene
        settings = scene.gblend_scene_settings
        paths = getattr(scene, "gblend_project_paths", None)

        output_dir = getattr(paths, "output_dir", "") if paths else ""
        if not output_dir:
            blend_path = bpy.data.filepath
            if blend_path:
                output_dir = os.path.join(os.path.dirname(blend_path), "output")
            else:
                output_dir = bpy.app.tempdir or bpy.utils.resource_path("USER")

        os.makedirs(output_dir, exist_ok=True)

        if settings.save_rgb:
            self._render_rgb(scene, os.path.join(output_dir, "rgb"))
        if settings.save_depth:
            self._render_depth(scene, os.path.join(output_dir, "depth"))
        if settings.save_normal:
            self._render_normal(scene, os.path.join(output_dir, "normal"))
        if settings.save_segmentation:
            self._render_segmentation(scene, os.path.join(output_dir, "segmentation"))

        self.report({'INFO'}, f"Rendering finished (saved in {output_dir})")
        return {'FINISHED'}
    
    def _render_rgb(self, scene, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(out_dir, "rgb_")
        bpy.ops.render.render(animation=True, write_still=True)

    def _render_depth(self, scene, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        rlayers = tree.nodes.new("CompositorNodeRLayers")
        normalize = tree.nodes.new("CompositorNodeNormalize")
        output = tree.nodes.new("CompositorNodeOutputFile")
        output.base_path = out_dir
        output.file_slots[0].path = "depth_"

        tree.links.new(rlayers.outputs["Depth"], normalize.inputs[0])
        tree.links.new(normalize.outputs[0], output.inputs[0])

        bpy.ops.render.render(animation=True, write_still=True)

    def _render_normal(self, scene, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        rlayers = tree.nodes.new("CompositorNodeRLayers")
        output = tree.nodes.new("CompositorNodeOutputFile")
        output.base_path = out_dir
        output.file_slots[0].path = "normal_"

        tree.links.new(rlayers.outputs["Normal"], output.inputs[0])

        bpy.ops.render.render(animation=True, write_still=True)

    def _render_segmentation(self, scene, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        rlayers = tree.nodes.new("CompositorNodeRLayers")
        output = tree.nodes.new("CompositorNodeOutputFile")
        output.base_path = out_dir
        output.file_slots[0].path = "seg_"

        tree.links.new(rlayers.outputs["IndexOB"], output.inputs[0])

        bpy.ops.render.render(animation=True, write_still=True)