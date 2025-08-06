import os
import bpy
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree, KDTree

from .utils import (
    apply_rotation_to_points,
    compute_rotation_matrix_between,
    apply_rotation_to_object,
    translate_object_along_z,
    get_camera_ray_from_pixel
)
from .vis import visualize_points, draw_sampled_points, draw_rays_from_pixels
from .ransac_utils import fit_ransac_plane_3D

def estimate_ground_z(obj, percentile=20):
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    z_values = np.array([v.z for v in verts])
    threshold = np.percentile(z_values, percentile)
    z_filtered = z_values[z_values <= threshold]

    if len(z_filtered) == 0:
        print("[WARN] No points below percentile threshold")
        return np.min(z_values)

    ground_z = np.median(z_filtered)
    return ground_z

def filter_dense_points(points, radius=0.3, min_neighbors=8):
        tree = cKDTree(points)
        mask = np.array([
            len(tree.query_ball_point(p, r=radius)) >= min_neighbors
            for p in points
        ])
        return points[mask]

def sample_ground_points_from_mask(obj, cam, mask, max_points_per_mask=100, radius=0.5):
    if not isinstance(mask, np.ndarray):
        print("[WARN] Mask is not a numpy array")
        return []

    ys, xs = np.where(mask > 127)
    coords = list(zip(xs, ys))
    if len(coords) == 0:
        return []

    sampled_indices = np.random.choice(len(coords), min(max_points_per_mask, len(coords)), replace=False)
    sampled_pixels = [coords[i] for i in sampled_indices]
    print(f"[INFO] Sampled {len(sampled_pixels)} pixels from mask array")

    width = cam.data["width"]
    height = cam.data["height"]
    pixel_scale_x = width / mask.shape[1]
    pixel_scale_y = height / mask.shape[0]
    scaled_pixels = [(x * pixel_scale_x, y * pixel_scale_y) for (x, y) in sampled_pixels]

    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    points = np.array([v.to_tuple() for v in verts])
    tree = KDTree(points)

    candidate_points = set()
    for i, px in enumerate(scaled_pixels):
        try:
            ray_origin, ray_dir = get_camera_ray_from_pixel(cam, px)
        except Exception as e:
            print(f"[WARN] Failed to compute ray at pixel {px}: {e}")
            continue

        for t in np.linspace(0.5, 10.0, 20):
            probe = ray_origin + t * ray_dir
            indices = tree.query_ball_point(probe, r=radius)
            for idx in indices[:2]:
                pt = tuple(points[idx])
                candidate_points.add(pt)

    candidate_points = np.array(list(candidate_points))
    candidate_points = np.round(candidate_points, 4)
    candidate_points = np.unique(candidate_points, axis=0)

    if len(candidate_points) == 0:
        print("[WARN] No candidate points found")
        return candidate_points

    filtered_points = filter_dense_points(candidate_points, radius=0.3, min_neighbors=8)

    print(f"[INFO] Number of candidate_points before filtering: {len(candidate_points)}")
    print(f"[INFO] Number of candidate_points after filtering: {len(filtered_points)}")

    return filtered_points


def extract_candidates_from_mask(obj, cameras, mask_dict):
    all_candidates = []

    camera_dict = {
        cam.name.replace("_cam", ""): cam
        for cam in cameras
        if cam.name.endswith("_cam")
    }

    for image_path, mask_path in mask_dict.items():
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        if base_name not in camera_dict:
            print(f"[WARN] No camera found for {base_name}")
            continue

        cam = camera_dict[base_name]
        try:
            mask = np.array(Image.open(mask_path).convert("L"))
        except Exception as e:
            print(f"[WARN] Failed to read mask: {mask_path} ({e})")
            continue

        candidates = sample_ground_points_from_mask(obj, cam, mask)
        all_candidates.extend(candidates)

    print(f"[INFO] Total candidate points from masks: {len(all_candidates)}")
    return np.array(all_candidates)

def setup_ground(cameras, animated_camera=None, obj_name="point_cloud", mask_dict=None):
    try:
        obj = bpy.data.objects[obj_name]
    except KeyError:
        print(f"[ERROR] Failed to find object: {obj_name}")
        return

    if mask_dict:
        print(f"[INFO] Extracting candidate points from masks...")
        candidate_points = extract_candidates_from_mask(obj, cameras, mask_dict)
    else:
        candidate_points = []

    if len(candidate_points) < 10:
        print(f"[WARN] Not enough candidate points for ground estimation ({len(candidate_points)})")
        return

    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    points = np.array([v.to_tuple() for v in verts])

    floor_normal = fit_ransac_plane_3D(points, candidate_points)
    rot_mat = compute_rotation_matrix_between(floor_normal, np.array([0, 0, 1]))
    apply_rotation_to_object(obj, rot_mat)

    candidate_points = apply_rotation_to_points(candidate_points, rot_mat)
    # visualize_points(candidate_points)

    mean_z = estimate_ground_z(obj)
    translate_object_along_z(obj, mean_z)

    for cam_obj in cameras:
        cam_obj.matrix_world = rot_mat @ cam_obj.matrix_world
        cam_obj.location.z -= mean_z

    if animated_camera:
        animated_camera.matrix_world = rot_mat @ animated_camera.matrix_world
        animated_camera.location.z -= mean_z