# code for the experiments

## Overview

The code for comparing with other tools can be divided into four parts. Part 1: Match identified results to the features. Part 2: Find matched features in DeepRTAlign results and calculate the FC. Part 3: Find matched features in other tools and calculate the FC. Different identification tools (such as MSFragger and MaxQuant) and alignment tools (such as DeepRTAlign and OpenMS) have different output formats. For different software, you need to change the code to read the corresponding column (RT, m/z, charge, intensity). Here we compare with OpenMS results as an example. Part 4: Collect results from MBR tools. MBR tools (such as MaxQuant and MSFragger) do not need match results to features, we calculate the FC directly from quantitative results. Here we take the MSFragger as an example.

## Part 1:  Match identified results to the features
01_collect_openms_fragpipe_peptide.py

## Part 2:  Find matched features in DeepRTAlign results and calculate the FC
02_collect_deeprtalign_FC.py

## Part 3:  Find matched features in other tools and calculate the FC
03_collect_openms_align_FC.py

## Part 4:  Collect results from MBR tools
04_collect_FC_fragpipe.py