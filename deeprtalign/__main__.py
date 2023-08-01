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
from deeprtalign import collect_time_shift_no_disk
from deeprtalign import collect_mass_information_shift_bins_no_disk
from deeprtalign import collect_mass_alignment_no_disk

import argparse
import shutil
import os

def run(method,file_dir,sample_file,processing_number=1,percent=0,time_window=1,bin_width=0.03,bin_precision=2,dict_size=1024,min_time_diff=0,max_time=5,max_log_intensity=3,disk_mode=0,keep_temp=0,begin_step=1,fdr=0.01,mz_col=0,rt_col=1,intensity_col=2,charge_col=3,keep_best=1):
	if disk_mode==0:
		if method=='Dinosaur':
			import deeprtalign.pre_step_no_disk.dinosaur_no_disk
			result=deeprtalign.pre_step_no_disk.dinosaur_no_disk.pre_step(file_dir,sample_file,bin_precision)
		if method=='XICFinder':
			import deeprtalign.pre_step_no_disk.xicfinder_no_disk
			result=deeprtalign.pre_step_no_disk.xicfinder_no_disk.pre_step(file_dir,sample_file,bin_precision)
		if method=='OpenMS':
			import deeprtalign.pre_step_no_disk.openms_no_disk
			result=deeprtalign.pre_step_no_disk.openms_no_disk.pre_step(file_dir,sample_file,bin_precision)
		if method=='MaxQuant':
			import deeprtalign.pre_step_no_disk.maxquant_no_disk
			result=deeprtalign.pre_step_no_disk.maxquant_no_disk.pre_step(file_dir,sample_file,bin_precision)
		if method=='TXT':
			import deeprtalign.pre_step_no_disk.other_txt_no_disk
			result=deeprtalign.pre_step_no_disk.other_txt_no_disk.pre_step(file_dir,sample_file,bin_precision,mz_col,rt_col,intensity_col,charge_col)
		if method=='CSV':
			import deeprtalign.pre_step_no_disk.other_csv_no_disk
			result=deeprtalign.pre_step_no_disk.other_csv_no_disk.pre_step(file_dir,sample_file,bin_precision,mz_col,rt_col,intensity_col,charge_col)
			
		result=collect_time_shift_no_disk.collect_shift(time_window,result)
		
		result,total_fraction_number,total_sample_number=collect_mass_information_shift_bins_no_disk.collect_bins(bin_width,bin_precision,result)
		
		if not min_time_diff==0:
			if processing_number>1:
				from deeprtalign import mass_information_filter_multi_no_disk
				result=mass_information_filter_multi_no_disk.run_mass_filter(processing_number,min_time_diff,result)
			else:
				from deeprtalign import mass_information_filter_no_disk
				result=mass_information_filter_no_disk.mass_filter(min_time_diff,result)
		else:
			print('step_4: done')
		
		
		if processing_number>1:
			from deeprtalign import mass_alignment_samples_multi_no_disk
			result=mass_alignment_samples_multi_no_disk.run_alignment(processing_number,max_time,max_log_intensity,percent,total_fraction_number,total_sample_number,result)
		else:
			from deeprtalign import mass_alignment_samples_no_disk
			result=mass_alignment_samples_no_disk.run_alignment(max_time,max_log_intensity,percent,total_fraction_number,total_sample_number,result)
		
		collect_mass_alignment_no_disk.collect_information(bin_precision,bin_width,percent,result,fdr,keep_best)
		
		if keep_temp==0:
			os.remove('mass_align_all_information/information_all.csv')
		
	else:
		if begin_step<=1:
			if method=='Dinosaur':
				import deeprtalign.pre_step.dinosaur
				deeprtalign.pre_step.dinosaur.pre_step(file_dir,sample_file,bin_precision)
			if method=='XICFinder':
				import deeprtalign.pre_step.xicfinder
				deeprtalign.pre_step.xicfinder.pre_step(file_dir,sample_file,bin_precision)
			if method=='OpenMS':
				import deeprtalign.pre_step.openms
				deeprtalign.pre_step.openms.pre_step(file_dir,sample_file,bin_precision)
			if method=='MaxQuant':
				import deeprtalign.pre_step.maxquant
				deeprtalign.pre_step.maxquant.pre_step(file_dir,sample_file,bin_precision)
			if method=='TXT':
				import deeprtalign.pre_step.other_txt
				result=deeprtalign.pre_step.other_txt.pre_step(file_dir,sample_file,bin_precision,mz_col,rt_col,intensity_col,charge_col)
			if method=='CSV':
				import deeprtalign.pre_step.other_csv
				result=deeprtalign.pre_step.other_csv.pre_step(file_dir,sample_file,bin_precision,mz_col,rt_col,intensity_col,charge_col)
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
				print('step_4: done')
				shutil.copytree('shift_result_bins', 'shift_result_bins_filter')
		if begin_step<=5:
			if processing_number>1:
				from deeprtalign import mass_alignment_samples_multi
				mass_alignment_samples_multi.run_alignment(processing_number,max_time,max_log_intensity,percent)
			else:
				from deeprtalign import mass_alignment_samples
				mass_alignment_samples.run_alignment(max_time,max_log_intensity,percent)
		if begin_step<=6:
			collect_mass_alignment.collect_information(bin_precision,bin_width,percent,fdr,keep_best)
		if keep_temp==0:
			shutil.rmtree('pre_result')
			shutil.rmtree('shift_result')
			shutil.rmtree('shift_result_bins')
			shutil.rmtree('shift_result_bins_filter')
			shutil.rmtree('shift_result_bins_filter_done')
			shutil.rmtree('mass_align_all')
			os.remove('mass_align_all_information/information_all.csv')
def get_arg_and_run():
	parser = argparse.ArgumentParser()
	parser.add_argument('--method', '-m', type=str, help='the feature extraction method, support Dinosaur, XICFinder, OpenMS, MaxQuant and and any other text list containing m/z, charge, RT and Intensity information',required=True,choices=['Dinosaur','XICFinder','OpenMS','MaxQuant','TXT','CSV'])
	parser.add_argument('--file_dir', '-f', type=str, help='the data folder', required=True)
	parser.add_argument('--sample_file', '-s', type=str, help='the sample file', required=True)
	parser.add_argument('--processing_number', '-pn', type=int, help='processing number, choose according to the number of CPUs', default=1)
	parser.add_argument('--percent', '-pt', type=float, help='skip the bins with sample numbers below the percent of total sample numbers ', default=0)
	parser.add_argument('--time_window', '-tw', type=float, help='min, the time window in the coarse alignment step', default=1)
	parser.add_argument('--bin_width', '-bw', type=float, help='the bin width, choose according to the feature extraction step', default=0.03)
	parser.add_argument('--bin_precision', '-bp', type=int, help='the decimal place of bins, choose according to the feature extraction step', default=2)
	parser.add_argument('--dict_size', '-ds', type=int, help='the dict size, choose according to the memory size', default=1024)
	parser.add_argument('--min_time_diff', '-mtd', type=float, help='min, the time window used to filter the XIC, only keep the highest XIC', default=0)
	parser.add_argument('--max_time', '-mt', type=float, help='min, the time threshold used to filter the XIC, only align XICs within the threshold', default=5)
	parser.add_argument('--max_log_intensity', '-mli', type=float, help='log2 intensity value, the intensity threshold used to filter the XIC, only align XICs within the threshold', default=3)
	parser.add_argument('--disk_mode', '-dm', type=int, help='if use disk mode,disk mode is slower, but can keep the temp files, 0 do not use disk mode, 1 use disk mode', default=0)
	parser.add_argument('--keep_temp', '-kt', type=int, help='if keep the temp files, 0 remove, 1 keep', default=0)
	parser.add_argument('--begin_step', '-bs', type=int, help='begin from any step', default=1)
	parser.add_argument('--fdr', '-fd', type=float, help='the FDR cutoff', default=0.01)
	parser.add_argument('--mz_col', '-mz', type=int, help='mz column location, count from 1, for TXT or CSV method', default=0)
	parser.add_argument('--rt_col', '-rt', type=int, help='rt column location, count from 1, for TXT or CSV method', default=1)
	parser.add_argument('--intensity_col', '-int', type=int, help='intensity column location, count from 1, for TXT or CSV method', default=2)
	parser.add_argument('--charge_col', '-cha', type=int, help='charge column location, count from 1, for TXT or CSV method', default=3)
	parser.add_argument('--keep_best', '-kb', type=int, help='0 keep all the candidate results, 1 only keep the best result for each feature', default=1)
	args = parser.parse_args()
	run(args.method,args.file_dir,args.sample_file,args.processing_number,args.percent,args.time_window,args.bin_width,args.bin_precision,args.dict_size,args.min_time_diff,args.max_time,args.max_log_intensity,args.disk_mode,args.keep_temp,args.begin_step,args.fdr,args.mz_col,args.rt_col,args.intensity_col,args.charge_col,args.keep_best)


parser = argparse.ArgumentParser()
parser.add_argument('--method', '-m', type=str, help='the feature extraction method, support Dinosaur, XICFinder, OpenMS, MaxQuant and any other text list containing m/z, charge, RT and Intensity information',required=True,choices=['Dinosaur','XICFinder','OpenMS','MaxQuant','TXT','CSV'])
parser.add_argument('--file_dir', '-f', type=str, help='the data folder', required=True)
parser.add_argument('--sample_file', '-s', type=str, help='the sample file', required=True)
parser.add_argument('--processing_number', '-pn', type=int, help='processing number, choose according to the number of CPUs', default=1)
parser.add_argument('--percent', '-pt', type=float, help='skip the bins with sample numbers below the percent of total sample numbers ', default=0)
parser.add_argument('--time_window', '-tw', type=float, help='min, the time window in the coarse alignment step', default=1)
parser.add_argument('--bin_width', '-bw', type=float, help='the bin width, choose according to the feature extraction step', default=0.03)
parser.add_argument('--bin_precision', '-bp', type=int, help='the decimal place of bins, choose according to the feature extraction step', default=2)
parser.add_argument('--dict_size', '-ds', type=int, help='the dict size, choose according to the memory size', default=1024)
parser.add_argument('--min_time_diff', '-mtd', type=float, help='min, the time window used to filter the XIC, only keep the highest XIC', default=0)
parser.add_argument('--max_time', '-mt', type=float, help='min, the time threshold used to filter the XIC, only align XICs within the threshold', default=5)
parser.add_argument('--max_log_intensity', '-mli', type=float, help='log2 intensity value, the intensity threshold used to filter the XIC, only align XICs within the threshold', default=3)
parser.add_argument('--disk_mode', '-dm', type=int, help='if use disk mode,disk mode is slower, but can keep the temp files, 0 do not use disk mode, 1 use disk mode', default=0)
parser.add_argument('--keep_temp', '-kt', type=int, help='if keep the temp files, 0 remove, 1 keep', default=0)
parser.add_argument('--begin_step', '-bs', type=int, help='begin from any step', default=1)
parser.add_argument('--fdr', '-fd', type=float, help='the FDR cutoff', default=0.01)
parser.add_argument('--mz_col', '-mz', type=int, help='mz column location, count from 1, for TXT or CSV method', default=0)
parser.add_argument('--rt_col', '-rt', type=int, help='rt column location, count from 1, for TXT or CSV method', default=1)
parser.add_argument('--intensity_col', '-int', type=int, help='intensity column location, count from 1, for TXT or CSV method', default=2)
parser.add_argument('--charge_col', '-cha', type=int, help='charge column location, count from 1, for TXT or CSV method', default=3)
parser.add_argument('--keep_best', '-kb', type=int, help='0 keep all the candidate results, 1 only keep the best result for each feature', default=1)
args = parser.parse_args()
	
if __name__ == '__main__':
	run(args.method,args.file_dir,args.sample_file,args.processing_number,args.percent,args.time_window,args.bin_width,args.bin_precision,args.dict_size,args.min_time_diff,args.max_time,args.max_log_intensity,args.disk_mode,args.keep_temp,args.begin_step,args.fdr,args.mz_col,args.rt_col,args.intensity_col,args.charge_col,args.keep_best)