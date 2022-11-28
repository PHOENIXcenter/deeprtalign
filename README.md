# DeepRTAlign v1.1.3

## Overview

DeepRTAlign is a deep learning-based retention time alignment tool for large cohort LC-MS data analysis.

## Installation

1. Install Python3
2. Install Pytorch CPU version, please refer to https://pytorch.org/
3. Download `deeprtalign-1.1.3-py3-none-any.whl` from github
4. Use `pip deeprtalign-1.1.3-py3-none-any.whl` to install deeprtalign

## Getting Started

1. Feature lists and sample list should be prepared before running DeepRTAlign. Feature lists are the output of feature extraction tools (DeepRTAlign supports Dinosaur, OpenMS, MaxQuant and XICFinder). The sample list is an excel file recording the correspondences between feature files  and sample names. You can find the test data in the example_files folder. Note that if you use MaxQuant as the feature extraction tool, you should use the allPeptides.txt as the input file or files, and the sample list should correspond to the first column of allPeptides.txt file. DO NOT use "allPeptdes.txt" as the file name in sample list if you use MaxQuant.

2. You can get the help information by command`python -m deeprtalign -h`, the basic arguments are as follows:

   ```
     --method {Dinosaur,XICFinder,OpenMS,MaxQuant}, -m {Dinosaur,XICFinder,OpenMS,MaxQuant}
                           the feature extraction method, support Dinosaur, XICFinder, OpenMS and MaxQuant
     --file_dir FILE_DIR, -f FILE_DIR
                           the data folder contain feature lists
     --sample_file SAMPLE_FILE, -s SAMPLE_FILE
                           the sample file
   ```

   As an example, to handle the Dinosaur test data in example_files folder, you can create a new folder and put the file_dir (containing result files from feature extraction tool ) and sample_file in, switch the working directory to this folder, then use command `python -m deeprtalign -m Dinosaur -f file_dir -s sample_file.xlsx ` .

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
                        min, the time window used to filter the XIC, only keep
                        the highest XIC
   --keep_temp KEEP_TEMP, -kt KEEP_TEMP
                        if keep the temp files, 0 remove, 1 keep
   --begin_step BEGIN_STEP, -bs BEGIN_STEP
                        begin from any step
   ```
   
   processing_number (int, default 1) depends on your hardware. percent (float:0-1, default 0) is a threshold, DeepRTAlign will skip the bins with sample numbers below the percent of total sample numbers. time_window (float, default 1) depends on your chromatography, 1 min is the parameter we used in training and suitable for most situations. bin_width (float, default 0.03) and bin_precision (int, default 2) depends on your feature extraction parameters. dict_size(int , default 1024) depends on your memory size, default 1024MB. If you want to keep the temp files, set the keep_temp (int, default 0) to 1. You can begin from any begin_step (int, default 1).
   
3. The results will output to the mass_align_all_information folder. In order to avoid a single file from being too large, a single result file contains at most 1,000 groups. Each group contains the features from different samples aligned by DeepRTAlign.

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
### Other columns
Other columns are intermediate results and can be ignored.
## Note

Do not run the different projects under a same folder, the results will be overwritten.

## License

GPLv3 (General Public License version 3.0), details in the LICENSE file.

## Contacts

For any questions involving DeepRTAlign, please contact us by email.

**Yi Liu**, leoicarus@163.com

**Cheng Chang**, changchengbio@163.com or changcheng@ncpsb.org.cn
