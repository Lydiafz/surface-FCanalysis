import os
import nibabel as nib
import numpy as np

functional_dir = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis3/Preprocessed_SurfaceData"
roi_timeseries_dir = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/Analysis4/ROI_Ts/Seed_ROIs/lDLPFC"
output_dir = "/BICNAS2/lyfang/BIC_project/STR_rTMS/FC_analysis/wb_sbc/seed_FCMap"

os.makedirs(output_dir, exist_ok=True)

subjects = [
    f.split("_")[0]
    for f in os.listdir(functional_dir)
    if f.endswith("_task-rest_space-fsLR_den-91k_desc-denoisedSmoothed_bold.dtseries.nii")
]

for subject in subjects:
    print(f"Processing {subject}")

    func_path = os.path.join(
        functional_dir,
        f"{subject}_task-rest_space-fsLR_den-91k_desc-denoisedSmoothed_bold.dtseries.nii"
    )

    seed_ts_path = os.path.join(
        roi_timeseries_dir,
        f"{subject}_lDLPFC_timeseries.txt"
    )

    if not os.path.exists(seed_ts_path):
        print(f"Missing seed TS for {subject}, skipping")
        continue

    seed_ts = np.loadtxt(seed_ts_path)

    cifti = nib.load(func_path)
    data = cifti.get_fdata()          # (T, V)
    data = data.T                     # (V, T)

    if seed_ts.shape[0] != data.shape[1]:
        print(f"Length mismatch for {subject}, skipping")
        continue

    # ---------- Z-score ----------
    seed_std = seed_ts.std()
    if seed_std == 0:
        print(f"Seed TS has zero variance for {subject}, skipping")
        continue

    seed_z = (seed_ts - seed_ts.mean()) / seed_std

    data_mean = data.mean(axis=1, keepdims=True)
    data_std  = data.std(axis=1, keepdims=True)

    valid = data_std[:, 0] > 0   # mask zero-variance vertices

    data_z = np.zeros_like(data)
    data_z[valid] = (data[valid] - data_mean[valid]) / data_std[valid]

    # ---------- Correlation (vectorized) ----------
    r = np.zeros(data.shape[0])
    r[valid] = np.dot(data_z[valid], seed_z) / (seed_z.size - 1)

    # ---------- Fisher z ----------
    z = np.zeros_like(r)
    z[valid] = np.arctanh(np.clip(r[valid], -0.999999, 0.999999))

    # ---------- Build *dscalar* header  ----------
    scalar_axis = nib.cifti2.cifti2_axes.ScalarAxis(["seedFC_z"])
    brain_axis  = cifti.header.get_axis(1)

    out_img = nib.Cifti2Image(
        z[np.newaxis, :],
        header=(scalar_axis, brain_axis),
        nifti_header=cifti.nifti_header
    )

    out_file = os.path.join(output_dir, f"{subject}_lDLPFC_fc_z.dscalar.nii")
    nib.save(out_img, out_file)

    print(f"Saved: {out_file}")