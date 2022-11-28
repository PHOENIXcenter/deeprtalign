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
from deeprtalign import mass_information_filter
from deeprtalign import collect_mass_alignment
import argparse
import shutil

def run(method,file_dir,sample_file,processing_number=1,percent=0.2,bin_width=0.03,bin_precision=2):
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
	collect_time_shift.collect_shift()
	if method=='Dinosaur':
		import deeprtalign.collect_mass_information_shift_bins.dinosaur
		deeprtalign.collect_mass_information_shift_bins.dinosaur.collect_bins(bin_width,bin_precision)
	if method=='XICFinder':
		import deeprtalign.collect_mass_information_shift_bins.xicfinder
		deeprtalign.collect_mass_information_shift_bins.xicfinder.collect_bins(bin_width,bin_precision)
	if method=='OpenMS':
		import deeprtalign.collect_mass_information_shift_bins.openms
		deeprtalign.collect_mass_information_shift_bins.openms.collect_bins(bin_width,bin_precision)
	if method=='MaxQuant':
		import deeprtalign.collect_mass_information_shift_bins.maxquant
		deeprtalign.collect_mass_information_shift_bins.maxquant.collect_bins(bin_width,bin_precision)
	mass_information_filter.mass_filter()
	if processing_number>1:
		from deeprtalign import mass_alignment_samples_multi
		mass_alignment_samples_multi.run_alignment(processing_number,percent)
	else:
		from deeprtalign import mass_alignment_samples
		mass_alignment_samples.run_alignment(percent)
	collect_mass_alignment.collect_information(bin_precision,bin_width)
	shutil.rmtree('pre_result')
	shutil.rmtree('shift_result')
	shutil.rmtree('shift_result_bins')
	shutil.rmtree('shift_result_bins_filter')
	shutil.rmtree('mass_align_all')
	
parser = argparse.ArgumentParser()
parser.add_argument('--method', '-m', help='the feature extraction method, support Dinosaur, XICFinder, OpenMS and MaxQuant',required=True,choices=['Dinosaur','XICFinder','OpenMS','MaxQuant'])
parser.add_argument('--file_dir', '-f', help='the data folder', required=True)
parser.add_argument('--sample_file', '-s', help='the sample file', required=True)
parser.add_argument('--processing_number', '-pn', help='processing number, choose according to the number of CPUs', default=1)
parser.add_argument('--percent', '-pt', help='skip the bins with sample numbers below the percent of total sample numbers ', default=0.5)
parser.add_argument('--bin_width', '-bw', help='the bin width, choose according to the feature extraction step', default=0.03)
parser.add_argument('--bin_precision', '-bp', help='the decimal place of bins, choose according to the feature extraction step', default=2)
args = parser.parse_args()
	
if __name__ == '__main__':
	run(args.method,args.file_dir,args.sample_file,args.processing_number,args.percent,args.bin_width,args.bin_precision)