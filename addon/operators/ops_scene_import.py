import bpy
import os
import re
from ..core import setup_cameras


class GBLEND_OT_scene_import(bpy.types.Operator):
    """Import 3DGS splats (PLY) and reference cameras"""
    bl_idname = "gblend.import_scene"
    bl_label = "Import Scene (PLY + Cameras)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        paths = context.scene.paths
        return bool(getattr(paths, "ply_path", "") and os.path.exists(paths.ply_path))

    def _find_import_operator(self):
        """Find Kiri import operator name dynamically"""
        import_ops = [n for n in dir(bpy.ops.sna) if n.startswith("import_ply_as_splats_")]
        return sorted(import_ops)[0] if import_ops else None

    def _get_import_kwargs(self, op, ply_path):
        """Build kwargs for Kiri import operator"""
        try:
            props = {p.identifier for p in op.get_rna_type().properties}
        except Exception:
            props = set()

        directory, filename = os.path.dirname(ply_path), os.path.basename(ply_path)

        if {"filepath", "directory", "files"} <= props:
            return dict(filepath=ply_path, directory=directory, files=[{"name": filename}])
        if {"filepath"} <= props:
            return dict(filepath=ply_path)
        if {"directory", "files"} <= props:
            return dict(directory=directory, files=[{"name": filename}])

        # fallback: first path-like property
        pathlike = [p for p in props if re.search(r"(file|path|dir)", p, re.I)]
        return {pathlike[0]: ply_path} if pathlike else {}

    def _ensure_view3d_context(self, scene):
        """Find a valid VIEW_3D context override"""
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == "VIEW_3D":
                    for region in area.regions:
                        if region.type == "WINDOW":
                            return dict(window=win, screen=win.screen, area=area, region=region, scene=scene)
        return {}

    def execute(self, context):
        scene = context.scene
        paths = scene.paths
        ply_path = getattr(paths, "ply_path", "")

        if not (ply_path and os.path.exists(ply_path)):
            self.report({'ERROR'}, "Invalid PLY path.")
            return {'CANCELLED'}

        # Find Kiri import operator
        opname = self._find_import_operator()
        if not opname:
            self.report({'ERROR'}, "Kiri import operator not found. Please open the Kiri panel once.")
            return {'CANCELLED'}
        op = getattr(bpy.ops.sna, opname)

        # Build kwargs for operator
        kwargs = self._get_import_kwargs(op, ply_path)

        # Ensure VIEW_3D context
        ov = self._ensure_view3d_context(scene)
        ctx = bpy.context.temp_override(**ov) if ov else bpy.context.temp_override()

        # Run import
        try:
            with ctx:
                if kwargs:
                    op("EXEC_DEFAULT", **kwargs)
                else:
                    self.report({'ERROR'}, f"Import operator does not support file args (id={opname})")
                    return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {e}")
            return {'CANCELLED'}

        # Set default mode on imported object
        imported_obj = next(
            (obj for obj in reversed(scene.objects) if hasattr(obj, "sna_kiri3dgs_active_object_update_mode")),
            None,
        )
        if imported_obj:
            imported_obj.sna_kiri3dgs_active_object_update_mode = "Enable Camera Updates"

        # Refresh viewport
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()
                if area.type == "VIEW_3D":
                    for space in area.spaces:
                        if space.type == "VIEW_3D":
                            space.shading.type = "MATERIAL"

        # Load cameras
        json_path = getattr(paths, "camera_path", "")
        image_dir = os.path.join(getattr(paths, "data_dir", ""), "images")

        if not os.path.exists(json_path):
            self.report({'ERROR'}, f"Camera JSON not found: {json_path}")
            return {'CANCELLED'}
        if not os.path.isdir(image_dir):
            self.report({'ERROR'}, f"Image folder not found: {image_dir}")
            return {'CANCELLED'}

        parent_collection = bpy.data.collections.get("Collection")
        if parent_collection is None:
            self.report({'ERROR'}, "Default 'Collection' not found in scene")
            return {'CANCELLED'}

        setup_cameras(json_path, image_dir, parent_collection)

        self.report({'INFO'}, "Scene imported successfully (PLY + Cameras).")
        return {'FINISHED'}
