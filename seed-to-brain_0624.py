import os
import nibabel as nib
import numpy as np
from scipy.stats import pearsonr

# Define paths
functional_dir = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis3/Preprocessed_SurfaceData"  # Directory containing resampled dense timeseries files
roi_timeseries_dir = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis4/ROI_Ts/Seed_ROIs/lrACC"  # Directory containing ROI time series
output_dir = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis4/Seed_FCMap/lrACC"  # Directory to save FC maps

os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist

# Loop over all subjects
subjects = [d.split("_")[0] for d in os.listdir(functional_dir) if d.endswith("_task-rest_space-fsLR_den-91k_desc-denoisedSmoothed_bold.dtseries.nii")]
for subject in subjects:
    print(f"Processing subject: {subject}")

    # Define paths for subject's functional data
    func_file = f"{subject}_task-rest_space-fsLR_den-91k_desc-denoisedSmoothed_bold.dtseries.nii"
    func_path = os.path.join(functional_dir, func_file)

    # Define path for subject's ROI time series
    roi_timeseries_file = f"{subject}_lrACC_timeseries.txt"
    roi_timeseries_path = os.path.join(roi_timeseries_dir, roi_timeseries_file)

    if not os.path.exists(roi_timeseries_path):
        print(f"No ROI time series found for {subject}. Skipping.")
        continue

    # Load the ROI time series (assumes a single-column text file)
    roi_timeseries = np.loadtxt(roi_timeseries_path)  # Shape: (time_points,)

    # Load subject's functional data
    cifti = nib.load(func_path)
    cifti_data = cifti.get_fdata()  # Shape: (time_points, brain_vertices)

    # Check if ROI time series length matches functional data time points
    if roi_timeseries.shape[0] != cifti_data.shape[0]:
        print(f"Time series length mismatch for {subject}. Skipping.")
        continue

    # Compute seed-to-voxel FC (correlation) incrementally
    num_vertices = cifti_data.shape[1]
    correlation_map = np.zeros(num_vertices)
    for vertex in range(num_vertices):
        if np.std(cifti_data[:, vertex]) == 0 or np.std(roi_timeseries) == 0:
            correlation_map[vertex] = np.nan  # Assign NaN for undefined correlation
        else:
            correlation_map[vertex], _ = pearsonr(roi_timeseries, cifti_data[:, vertex])

    # Update the CIFTI header to reflect the new data shape
    new_cifti_header = cifti.header.copy()
    new_cifti_header.matrix[0].number_of_series_points = 1  # Set the number of time points to 1

    # Save the FC map as a new CIFTI file
    output_file = os.path.join(output_dir, f"{subject}_lrACC_fc.dtseries.nii")
    new_cifti = nib.Cifti2Image(correlation_map[None, :], new_cifti_header, cifti.nifti_header)
    new_cifti.to_filename(output_file)

    print(f"Saved FC map for subject {subject}: {output_file}")
