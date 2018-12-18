import os
import nipype.interfaces.afni as afni
import nipype.interfaces.ants as ants
import nipype.interfaces.fsl as fsl
import scipy.io as sio
import nibabel as nb

dataset = "rita_1"
study = "RFGVS033"
scan = "8"

data_dir = "/home/julia/projects/fast_rsfmri/%s/"%(dataset)
in_file = data_dir + "converted/%s/%s_%s/%s_%s_fixed.nii.gz"%(study, study, scan, study, scan)
mean_file = data_dir + "processed/%s/func_mean.nii.gz"%scan
bias_file = data_dir + "processed/%s/func_bias_corr.nii.gz"%scan
mask_file = data_dir + "processed/%s/func_mask.nii.gz"%scan
ts_file = data_dir + "processed/%s/func.nii.gz"%scan

if not os.path.isdir(data_dir + "processed/%s"%scan):
    os.makedirs(data_dir + "processed/%s"%scan)

print("Swap dimensions")


print("Compute mean")
mean = fsl.MeanImage(dimension='T',
                     in_file=in_file,
                     out_file=mean_file)
mean.run()

print("Bias field correction")
biasfield = ants.N4BiasFieldCorrection(dimension=2,
                                       n_iterations=[150,100,50,30],
                                       convergence_threshold=1e-11,
                                       bspline_fitting_distance = 10,
                                       bspline_order = 4,
                                       shrink_factor = 2,
                                       input_image = mean_file,
                                       output_image= bias_file)
biasfield.run()

print("Compute mask")
mask = afni.Automask(outputtype='NIFTI_GZ', in_file=bias_file, out_file=mask_file)
mask.run()

print("Fixing headers, saving data")
aff = nb.load(in_file).affine
orig_data = nb.load(in_file).get_data()
bias_data = nb.load(bias_file).get_data()
mask_data = nb.load(mask_file).get_data()
nb.save(nb.Nifti1Image(mask_data, aff), mask_file)
nb.save(nb.Nifti1Image(bias_data, aff), bias_file)
nb.save(nb.Nifti1Image(orig_data, aff), ts_file)

os.remove("func_bias_corr_masked.nii.gz")
