import bpy
import os
import re
from gblend_addon.core import setup_cameras

class GBLEND_OT_kiri_import_direct(bpy.types.Operator):
    bl_idname = "gblend.kiri_import_direct"
    bl_label = "Import PLY via Kiri (Direct)"
    bl_description = "Import PLY as Splats via Kiri Engine using gblend_project_paths.ply_path (no dialog)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        paths = context.scene.gblend_project_paths
        p = getattr(paths, "ply_path", "")
        return bool(p and os.path.exists(p))

    def execute(self, context):
        scene = context.scene
        paths = scene.gblend_project_paths
        ply_path = getattr(paths, "ply_path", "")
        if not (ply_path and os.path.exists(ply_path)):
            self.report({'ERROR'}, "PLY 경로가 비어있거나 파일이 없습니다.")
            return {'CANCELLED'}

        # 1) Kiri 서브메뉴 Import로(네 환경에선 0이 Import)
        try:
            scene["sna_kiri3dgs_interface_active_sub_interface_mode"] = 0
        except Exception:
            pass

        # 2) import 본체 오퍼레이터 찾기
        import_ops = [n for n in dir(bpy.ops.sna) if n.startswith("import_ply_as_splats_")]
        if not import_ops:
            self.report({'ERROR'}, "Kiri import 오퍼레이터가 등록되지 않았습니다. Kiri 패널을 한 번 열어주세요.")
            return {'CANCELLED'}
        opname = sorted(import_ops)[0]
        op = getattr(bpy.ops.sna, opname)

        # 3) 프로퍼티 확인
        try:
            props = {p.identifier for p in op.get_rna_type().properties}
        except Exception:
            props = set()

        directory, filename = os.path.dirname(ply_path), os.path.basename(ply_path)
        kwargs = {}
        # 표준 파일선택 프로퍼티 우선
        if {"filepath", "directory", "files"} <= props:
            kwargs = dict(filepath=ply_path, directory=directory, files=[{"name": filename}])
        elif {"filepath"} <= props:
            kwargs = dict(filepath=ply_path)
        elif {"directory", "files"} <= props:
            kwargs = dict(directory=directory, files=[{"name": filename}])
        else:
            # 커스텀 키를 쓰는 경우가 있을 수 있어 한 번 더 시도
            pathlike = [p for p in props if re.search(r'(file|path|dir)', p, re.I)]
            if pathlike:
                kwargs = {pathlike[0]: ply_path}

        # 4) VIEW_3D 컨텍스트 보장
        def find_view3d_override():
            for win in bpy.context.window_manager.windows:
                for area in win.screen.areas:
                    if area.type == 'VIEW_3D':
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                return dict(window=win, screen=win.screen, area=area, region=region, scene=scene)
            return {}
        ov = find_view3d_override()
        ctx = bpy.context.temp_override(**ov) if ov else bpy.context.temp_override()

       # 5) 실행
        try:
            with ctx:
                if kwargs:
                    res = op('EXEC_DEFAULT', **kwargs)  # 파일창 없이 바로 임포트
                else:
                    self.report({'ERROR'}, f"Kiri import 오퍼레이터가 파일 경로 인자를 지원하지 않습니다. (id={opname})")
                    return {'CANCELLED'}
        except TypeError as e:
            self.report({'ERROR'}, f"직접 임포트 실패: {e}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"임포트 중 예외: {e}")
            return {'CANCELLED'}

        # Set default mode to 'Enable Camera Updates' on the imported object
        imported_obj = None
        for obj in reversed(scene.objects):
            if hasattr(obj, "sna_kiri3dgs_active_object_update_mode"):
                imported_obj = obj
                break
        if imported_obj:
            imported_obj.sna_kiri3dgs_active_object_update_mode = "Enable Camera Updates"

        # 6) 화면 갱신
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()
                # Set viewport shading to MATERIAL (Material Preview)
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'MATERIAL'
        self.report({'INFO'}, f"Kiri import 실행 완료: {opname}")


        # camera load
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

        setup_cameras(
            json_path,
            image_dir,
            parent_collection,
        )

        camera_collection = bpy.data.collections.get("Cameras")
        if camera_collection:
            camera_collection.hide_viewport = True
            camera_collection.hide_render = True

        self.report({'INFO'}, "Cameras loaded successfully.")
        return {'FINISHED'}