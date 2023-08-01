# DeepRTAlign v1.2.0

## Overview

DeepRTAlign is a deep learning-based retention time alignment tool for large cohort LC-MS data analysis.

## Installation

1. Install Python3.
2. Install Pytorch CPU version, please refer to https://pytorch.org/.
3. Use `pip install deeprtalign` to install deeprtalign OR download `deeprtalign-1.2.0-py3-none-any.whl` from github, and use `pip install deeprtalign-1.2.0-py3-none-any.whl` to install deeprtalign. This step will take 3-4 minutes.

DeepRTAlign is not dependent on a specific operating system, we have tested it on Windows 10, Ubuntu 18.04 and macOS 12.1.

## Getting Started

1. Feature lists and sample list should be prepared before running DeepRTAlign. Feature lists are the output of feature extraction tools (DeepRTAlign supports Dinosaur, OpenMS, MaxQuant, XICFinder and any other text list containing m/z, charge, RT and Intensity information ). The sample list is an excel file recording the correspondences between feature files  and sample names. You can find the test data in the example_files folder. 

   Note that if you use MaxQuant as the feature extraction tool, you should use the allPeptides.txt as the input file or files, and the sample list should correspond to the first column of allPeptides.txt file. DO NOT use "allPeptdes.txt" as the file name in sample list if you use MaxQuant. If you use the old version of MaxQuant (<2.0),please check the 7th column, delete the "Resolution" column if you see it (in MaxQuant v2.0, "Resolution" column is not exists, so we have changed corresponding code).

2. You can get the help information by command`deeprtalign -h`, the basic arguments are as follows:

   ```
   --method {Dinosaur,XICFinder,OpenMS,MaxQuant,TXT,CSV}, -m {Dinosaur,XICFinder,OpenMS,MaxQuant,TXT,CSV}
                           the feature extraction method, support Dinosaur,
                           XICFinder, OpenMS, MaxQuant and any other text list containing m/z, charge, RT and Intensity information
   --file_dir FILE_DIR, -f FILE_DIR
                           the data folder
   --sample_file SAMPLE_FILE, -s SAMPLE_FILE
                           the sample file
   ```

      As an example, to handle the Dinosaur test data in example_files folder, you can create a new folder and put the file_dir (containing result files from feature extraction tool ) and sample_file in, switch the working directory to this folder, then use command `deeprtalign -m Dinosaur -f file_dir -s sample_file.xlsx ` . On a normal computer, this will take about 30 minutes. We strongly recommend users to use the `-pn` parameter according to the CPU core numbers. This will make it run much faster.

      If you choose TXT method (txt file separated by '\t') or CSV method (txt file separated by ','), you must provide optional arguments `--mz_col` `--charge_col` `--rt_col` `--intensity_col`.

      optional arguments:
      
   ```
   --processing_number PROCESSING_NUMBER, -pn PROCESSING_NUMBER
                           processing number, choose according to the number of
                           CPUs
   --percent PERCENT, -pt PERCENT
                           skip the bins with sample numbers below the percent of
                           total sample numbers
   --time_window TIME_WINDOW, -tw TIME_WINDOW
                           min, the time window in the coarse alignment step
   --bin_width BIN_WIDTH, -bw BIN_WIDTH
                           the bin width, choose according to the feature
                           extraction step
   --bin_precision BIN_PRECISION, -bp BIN_PRECISION
                           the decimal place of bins, choose according to the
                           feature extraction step
   --dict_size DICT_SIZE, -ds DICT_SIZE
                           the dict size, choose according to the memory size
   --min_time_diff MIN_TIME_DIFF, -mtd MIN_TIME_DIFF
                           min, the time window used to filter the feature, only keep
                           the highest feature
   --max_time MAX_TIME, -mt MAX_TIME
                           min, the time threshold used to filter the feature, only
                           align features within the threshold
   --max_log_intensity MAX_LOG_INTENSITY, -mli MAX_LOG_INTENSITY
                           log2 intensity value, the intensity threshold used to
                           filter the feature, only align XICs within the threshold
   --disk_mode DISK_MODE, -dm DISK_MODE
                           if use disk mode,disk mode is slower, but can keep the
                           temp files, 0 do not use disk mode, 1 use disk mode
   --keep_temp KEEP_TEMP, -kt KEEP_TEMP
                           if keep the temp files, 0 remove, 1 keep
   --begin_step BEGIN_STEP, -bs BEGIN_STEP
                           begin from any step
   --fdr FDR, -fd FDR    the FDR cutoff
   --mz_col MZ_COL, -mz MZ_COL
                           mz column location, count from 1, for TXT or CSV method
   --rt_col RT_COL, -rt RT_COL
                           rt column location, count from 1, for TXT or CSV method
   --intensity_col INTENSITY_COL, -int INTENSITY_COL
                           intensity column location, count from 1, for TXT or CSV method
   --charge_col CHARGE_COL, -cha CHARGE_COL
                           charge column location, count from 1, for TXT or CSV method
   --keep_best KEEP_BEST, -kb KEEP_BEST
                           0 keep all the candidate results, 1 only keep the best
                           result for each feature
   ```  
   processing_number (int, default 1) depends on your hardware. percent (float:0-1, default 0) is a threshold, DeepRTAlign will skip the bins with sample numbers below the percent of total sample numbers. time_window (float, default 1) depends on your chromatography, 1 min is the parameter we used in training and is suitable for most situations. bin_width (float, default 0.03) and bin_precision (int, default 2) depends on your feature extraction parameters, bin_width is the m/z window size, and bin_precision is the number of decimal places used in this step. Only the features in the same m/z window will be aligned, default values are suitable for most situations. dict_size (int, default 1024) depends on your memory size, default 1024MB. min_time_diff (float, default 0) is the time window (min) used to used to filter the feature, only keep the highest feature within a time window. max_time (float, default 5) and max_log_intensity (float, default 3) are used for reducing calculation. disk_mode will write temp files on your disk, and is not used by default. If you want to keep the temp files, set the keep_temp (int, default 0) to 1. In disk_mode, you can begin from any begin_step (int, default 1). step 1: preprocessing of input files, step 2: coarse alignment, step 3: bining, step 4: filtering, step 5: alignment, step 6: generating result file. fdr (float, 0-1, default 0.01) is the threshold used in quality control part. mz_col, rt_col, intensity_col and charge_col are used in TXT method and CSV method, please note they are counted from 1. A feature may exist in multiple groups after alignment and quality control, keep_best=1 (default) will only keey the group with the highest adj_score for each feature, or you can set keep_best=0, and keep all candidates.  
3. The results will output to the mass_align_all_information folder.If you set kt to 0 (default), there will be only one file in the mass_align_all_information folder: information_target.csv (target results after QC). If you set kt to 1, there will be two files in the mass_align_all_information folder: information_target.csv (target results after QC) and information_all.csv (results before QC, and containing decoy samples).

## Result Description
In result files, each line represent a feature, the meaning of each column is as follows.
### Main columns
- sample: the sample name corresponding to this feature.
- fraction: the fraction corresponding to this feature.
- time: the RT (min) corresponding to this feature.
- mz: the m/z corresponding to this feature.
- charge: the charge corresponding to this feature.
- intensity: the intensity corresponding to this feature.
- group: the group name corresponding to this feature, aligned features share the same group name.
- mz_error: the m/z difference of aligned pairs.
- score: the score of aligned pairs.
- adj_score: the score of aligned pairs considering the adjacent pairs, it is the mean of the current feature score and the scores of two adjacent features (RT dimension) before and after it.

In the default workflow, adj_score will be used for quality control and for drop duplicate features if keep_best is set to 1 (default). This workflow works well in most cases. But when the samples are quite different, or there are too many features with the almost same m/z, the default workflow usually report very few results. In this case,  mz_error and score are better choices for filtering the results, we recommend setting FDR to 1, and select features with smaller mz_erro from the results with score greater than 0.5.

### Other columns
Other columns are intermediate results and can be ignored.
## Note

Do not run the different projects under a same folder, the results will be overwritten.

## Demo
The demo are in the example_files folder. We use part of features in UPS2-Y dataset as examples. On a normal computer, each work will take about 30 minutes. We strongly recommend users to use the `-pn` parameter according to the CPU core numbers. This will make it run much faster.
We provide Dinosaur, MaxQuant, OpenMS and XICFinder results for user to test DeepRTAlign.

To handle the Dinosaur test data in example_files folder, you can create a new folder and put the file_dir (containing result files from feature extraction tool ) and sample_file in, switch the working directory to this folder, then use command `deeprtalign -m Dinosaur -f file_dir -s sample_file.xlsx `. The results will output to the mass_align_all_information folder.

To handle the MaxQuant test data in example_files folder, you can create a new folder and put the file_dir (containing result files from feature extraction tool ) and sample_file in, switch the working directory to this folder, then use command `deeprtalign -m MaxQuant -f file_dir -s sample_file.xlsx `. The results will output to the mass_align_all_information folder.

To handle the OpenMS test data in example_files folder, you can create a new folder and put the file_dir (containing result files from feature extraction tool ) and sample_file in, switch the working directory to this folder, then use command `deeprtalign -m OpenMS -f file_dir -s sample_file.xlsx `. The results will output to the mass_align_all_information folder.

To handle the XICFinder test data in example_files folder, you can create a new folder and put the file_dir (containing result files from feature extraction tool ) and sample_file in, switch the working directory to this folder, then use command `deeprtalign -m XICFinder -f file_dir -s sample_file.xlsx `. The results will output to the mass_align_all_information folder.

Expected output is in expected_output folder.

## Code for the experiments
Code for comparing with other alignment tools are in this folder.

## License

GPLv3 (General Public License version 3.0), details in the LICENSE file.

## Contacts

For any questions involving DeepRTAlign, please contact us by email.

**Yi Liu**, leoicarus@163.com

**Cheng Chang**, changchengbio@163.com or changcheng@ncpsb.org.cn
