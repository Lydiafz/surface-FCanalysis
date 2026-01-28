#!/bin/bash

set -e  # Exit the script if any command fails
set -x  # Enable debugging to print each command before execution

#--fmriprep settings--#
bids_root_dir="/BICNAS2/lyfang/BIC_project/STR_rTMS"
raw_path="/BICNAS2/lyfang/BIC_project/STR_rTMS/rawdata"
fs_subj_dir="/usr/local/freesurfer/7.4.1"
work_dir="/BICNAS2/lyfang/BIC_project/STR_rTMS/work"
derivatives_dir="/BICNAS2/lyfang/BIC_project/STR_rTMS/derivatives"
nthreads=16
ompnthreads=8

# Find subject folders
folders=$(find "$raw_path" -type d -name "sub-*")

# Populate subjects array
subjects=()
for f in $folders; do
  b=$(basename "$f")
  subjects+=("${b:4}")  # Append subject ID (substring starting at index 4)
done

# Verify subjects array is populated
if [ ${#subjects[@]} -eq 0 ]; then
  echo "No subjects found. Exiting."
  exit 1
fi
echo "Subjects to process: ${subjects[@]}"

#--Processing fmriprep one by one--#
for subject in "${subjects[@]}"; do
    # Check if output for the subject already exists in derivatives directory
    if [ -d "${derivatives_dir}/fmriprep/sub-${subject}" ]; then
        echo "Subject ${subject} has already been processed. Skipping."
        continue
    fi

    # Print the subject being processed
    echo "Processing subject: $subject"

    # Unset PYTHONPATH to avoid conflicts
    unset PYTHONPATH

    # Run the singularity fmriprep command
    singularity run -B $HOME/.cache/templateflow:/opt/templateflow,$bids_root_dir:/mnt/proj,$fs_subj_dir:/mnt/fs_dir,$work_dir:/mnt/work /group/singularity-SIF/fmriprep_24.0.0.sif \
    /mnt/proj/rawdata/ /mnt/proj/derivatives \
    participant \
    --participant-label ${subject} \
    -w /mnt/work \
    --fs-license-file /mnt/fs_dir/license.txt \
    --output-spaces MNI152NLin6Asym:res-2 fsaverage:res-native fsLR:den-32k \
    --cifti-output \
    --write-graph \
    --nthreads $nthreads \
    --omp-nthreads $ompnthreads \
    --verbose

    echo "Completed processing for subject: $subject"
done

echo "All subjects processed."
