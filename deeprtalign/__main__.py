# -*- coding: utf-8 -*-
# Copyright © 2021 Yi Liu and Cheng Chang
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

from deeprtalign import collect_time_shift
from deeprtalign import collect_mass_alignment
import argparse
import shutil

def run(method,file_dir,sample_file,processing_number=1,percent=0,time_window=1,bin_width=0.03,bin_precision=2,dict_size=1024,min_time_diff=0,keep_temp=0,begin_step=1):
	if begin_step<=1:
		if method=='Dinosaur':
			import deeprtalign.pre_step.dinosaur
			deeprtalign.pre_step.dinosaur.pre_step(file_dir,sample_file)
		if method=='XICFinder':
			import deeprtalign.pre_step.xicfinder
			deeprtalign.pre_step.xicfinder.pre_step(file_dir,sample_file)
		if method=='OpenMS':
			import deeprtalign.pre_step.openms
			deeprtalign.pre_step.openms.pre_step(file_dir,sample_file)
		if method=='MaxQuant':
			import deeprtalign.pre_step.maxquant
			deeprtalign.pre_step.maxquant.pre_step(file_dir,sample_file)
	if begin_step<=2:
		collect_time_shift.collect_shift(time_window)
	if begin_step<=3:
		if method=='Dinosaur':
			import deeprtalign.collect_mass_information_shift_bins.dinosaur
			deeprtalign.collect_mass_information_shift_bins.dinosaur.collect_bins(bin_width,bin_precision,dict_size)
		if method=='XICFinder':
			import deeprtalign.collect_mass_information_shift_bins.xicfinder
			deeprtalign.collect_mass_information_shift_bins.xicfinder.collect_bins(bin_width,bin_precision,dict_size)
		if method=='OpenMS':
			import deeprtalign.collect_mass_information_shift_bins.openms
			deeprtalign.collect_mass_information_shift_bins.openms.collect_bins(bin_width,bin_precision,dict_size)
		if method=='MaxQuant':
			import deeprtalign.collect_mass_information_shift_bins.maxquant
			deeprtalign.collect_mass_information_shift_bins.maxquant.collect_bins(bin_width,bin_precision,dict_size)
	if begin_step<=4:
		if not min_time_diff==0:
			if processing_number>1:
				from deeprtalign import mass_information_filter_multi
				mass_information_filter_multi.run_mass_filter(processing_number,min_time_diff)
			else:
				from deeprtalign import mass_information_filter
				mass_information_filter.mass_filter(min_time_diff)
		else:
			shutil.copytree('shift_result_bins', 'shift_result_bins_filter')
	if begin_step<=5:
		if processing_number>1:
			from deeprtalign import mass_alignment_samples_multi
			mass_alignment_samples_multi.run_alignment(processing_number,percent)
		else:
			from deeprtalign import mass_alignment_samples
			mass_alignment_samples.run_alignment(percent)
	if begin_step<=6:
		collect_mass_alignment.collect_information(bin_precision,bin_width,percent)
	if keep_temp==0:
		shutil.rmtree('pre_result')
		shutil.rmtree('shift_result')
		shutil.rmtree('shift_result_bins')
		shutil.rmtree('shift_result_bins_filter')
		shutil.rmtree('shift_result_bins_filter_done')
		shutil.rmtree('mass_align_all')
	
parser = argparse.ArgumentParser()
parser.add_argument('--method', '-m', type=str, help='the feature extraction method, support Dinosaur, XICFinder, OpenMS and MaxQuant',required=True,choices=['Dinosaur','XICFinder','OpenMS','MaxQuant'])
parser.add_argument('--file_dir', '-f', type=str, help='the data folder', required=True)
parser.add_argument('--sample_file', '-s', type=str, help='the sample file', required=True)
parser.add_argument('--processing_number', '-pn', type=int, help='processing number, choose according to the number of CPUs', default=1)
parser.add_argument('--percent', '-pt', type=float, help='skip the bins with sample numbers below the percent of total sample numbers ', default=0)
parser.add_argument('--time_window', '-tw', type=float, help='min, the time window in the coarse alignment step', default=1)
parser.add_argument('--bin_width', '-bw', type=float, help='the bin width, choose according to the feature extraction step', default=0.03)
parser.add_argument('--bin_precision', '-bp', type=int, help='the decimal place of bins, choose according to the feature extraction step', default=2)
parser.add_argument('--dict_size', '-ds', type=int, help='the dict size, choose according to the memory size', default=1024)
parser.add_argument('--min_time_diff', '-mtd', type=float, help='min, the time window used to filter the XIC, only keep the highest XIC', default=0)
parser.add_argument('--keep_temp', '-kt', type=int, help='if keep the temp files, 0 remove, 1 keep', default=0)
parser.add_argument('--begin_step', '-bs', type=int, help='begin from any step', default=1)
args = parser.parse_args()
	
if __name__ == '__main__':
	run(args.method,args.file_dir,args.sample_file,args.processing_number,args.percent,args.time_window,args.bin_width,args.bin_precision,args.dict_size,args.min_time_diff,args.keep_temp,args.begin_step)