singularity run --bind /BICNAS2/lyfang/BIC_project/STR_rTMS/derivatives:/data, \
                --bind /BICNAS2/lyfang/BIC_project/STR_rTMS/XCP_D_output:/out, \
                --bind /BICNAS2/lyfang/BIC_project/STR_rTMS:/license \
                  /group/singularity-SIF/xcp_d_0.8.0.sif \
                  /data /out participant \
                  --mode linc \
                  --low-mem \
                  --input-type fmriprep \
                  --combine-runs \
                  --nuisance-regressors 36P \
                  --min-coverage 0.5 \
                  --warp-surfaces-native2std \
                  --file-format cifti \
                  --fs-license-file /license/license.txt \
                  --min-time 100 --dummy-scans 0 --bpf-order 2 --lower-bpf 0.01 --upper-bpf 0.08 \
                  --head-radius auto --fd-thresh 0.3
