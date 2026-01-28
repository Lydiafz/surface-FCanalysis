import nibabel as nib
import numpy as np
import os

def find_nearest_vertex(surface_coords, mni_coord):
    """
    Find the nearest vertex on the surface given MNI coordinates.
    """
    distances = np.linalg.norm(surface_coords - mni_coord, axis=1)
    return np.argmin(distances)

def create_spherical_roi(surface_coords, center_vertex, radius_mm):
    """
    Create a spherical ROI by finding vertices within a given radius.
    """
    distances = np.linalg.norm(surface_coords - surface_coords[center_vertex], axis=1)
    return np.where(distances <= radius_mm)[0]

def save_roi_as_func_gii(roi_vertices, output_path, num_vertices):
    """
    Save the ROI as a .func.gii file.
    """
    data = np.zeros(num_vertices, dtype=np.float32)  # Explicitly set dtype to float32
    data[roi_vertices] = 1  # Mark ROI vertices as 1
    gii = nib.gifti.GiftiImage(darrays=[nib.gifti.GiftiDataArray(data)])
    nib.save(gii, output_path)
    print(f"Saved ROI to {output_path}")

# Paths to surface files
left_surface_file = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis3/surface_atlas/tpl-fsLR_den-32k_hemi-L_midthickness.surf.gii"
right_surface_file = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis3/surface_atlas/tpl-fsLR_den-32k_hemi-R_midthickness.surf.gii"
output_dir = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis4/SeedROIs"
os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

# Load surface data for both hemispheres
try:
    left_surf = nib.load(left_surface_file)
    right_surf = nib.load(right_surface_file)
except FileNotFoundError as e:
    raise FileNotFoundError(f"Surface file not found: {e}")

left_surface_coords = left_surf.darrays[0].data  # Left hemisphere surface coordinates
right_surface_coords = right_surf.darrays[0].data  # Right hemisphere surface coordinates
num_vertices_left = left_surface_coords.shape[0]
num_vertices_right = right_surface_coords.shape[0]

# Define ROIs
roi_specs = [
    {"name": "left DLPFC", "mni": np.array([-38, 44, 26]), "radius": 5, "hemi": "L"},
    {"name": "right DLPFC", "mni": np.array([38, 44, 26]), "radius": 5, "hemi": "R"},
    {"name": "sgACC", "mni": np.array([2, 18, -8]), "radius": 3, "hemi": "Midline"},
    {"name": "lrACC", "mni": np.array([-3, 39, -2]), "radius": 3, "hemi": "L"},
    {"name": "rrACC", "mni": np.array([3, 39, -2]), "radius": 3, "hemi": "R"}
]

# Generate and save ROIs
for roi in roi_specs:
    try:
        if roi["hemi"] == "L":
            surface_coords = left_surface_coords
            num_vertices = num_vertices_left
        elif roi["hemi"] == "R":
            surface_coords = right_surface_coords
            num_vertices = num_vertices_right
        elif roi["hemi"] == "Midline":
            # Process both hemispheres for midline ROIs
            left_vertex = find_nearest_vertex(left_surface_coords, roi["mni"])
            right_vertex = find_nearest_vertex(right_surface_coords, roi["mni"])
            left_roi_vertices = create_spherical_roi(left_surface_coords, left_vertex, roi["radius"])
            right_roi_vertices = create_spherical_roi(right_surface_coords, right_vertex, roi["radius"])

            # Save left hemisphere midline ROI
            left_output_path = os.path.join(output_dir, f"{roi['name'].replace(' ', '_')}_L.func.gii")
            save_roi_as_func_gii(left_roi_vertices, left_output_path, num_vertices_left)

            # Save right hemisphere midline ROI
            right_output_path = os.path.join(output_dir, f"{roi['name'].replace(' ', '_')}_R.func.gii")
            save_roi_as_func_gii(right_roi_vertices, right_output_path, num_vertices_right)
            continue  # Skip the rest of the loop for midline ROIs

        # Find the nearest vertex
        nearest_vertex = find_nearest_vertex(surface_coords, roi["mni"])

        # Create a spherical ROI around the nearest vertex
        roi_vertices = create_spherical_roi(surface_coords, nearest_vertex, roi["radius"])

        # Define output path
        roi_filename = f"{roi['name'].replace(' ', '_')}_{roi['hemi']}.func.gii"
        output_path = os.path.join(output_dir, roi_filename)

        # Save the ROI
        save_roi_as_func_gii(roi_vertices, output_path, num_vertices)

    except Exception as e:
        print(f"Error processing ROI {roi['name']}: {e}")
