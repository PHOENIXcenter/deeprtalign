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

import os
import math
import xlrd
import pandas as pd

def sample_pretreat(filepath,sample,fraction,result,bin_precision):
	df=pd.read_csv(filepath,sep='\t')
	#drop_negative=df[df['charge']==1].index
	#df.drop(drop_negative,inplace=True)
	Tmz=df['mz']
	df.loc[:,'Tmz']=Tmz
	df.loc[:,'intensity']=df['intensitySum']
	df.loc[:,'rt_start']=df['rtStart']
	df.loc[:,'time']=df['rtApex']
	df.loc[:,'rt_end']=df['rtEnd']
	sum_of_intensity=df['intensity'].sum()
	Tintensity=[math.log2(a)for a in df['intensity']]
	Tintensity10=[math.log10(a)for a in df['intensity']]
	df.loc[:,'Tintensity']=Tintensity
	df.loc[:,'Tintensity10']=Tintensity10
	Pintensity=[a/sum_of_intensity for a in df['intensity']]
	df.loc[:,'Pintensity']=Pintensity
	drop_zero=df[df['Tintensity']<=0].index
	df.drop(drop_zero,inplace=True)
	#Tmass=[str(round(c*float(d)-c*1.007276,2)) for c,d in zip(df['charge'],df['Tmz'])]
	Tmass=[str(round(a,bin_precision))for a in df['mz']]
	df.loc[:,'Tmass']=Tmass
	if fraction in result.keys():
		result[fraction][sample]=df
	else:
		result[fraction]={}
		result[fraction][sample]=df
	return result


def pre_step(file_dir,sample_file,bin_precision):
	workbook = xlrd.open_workbook(sample_file)
	booksheet = workbook.sheet_by_index(0)
	file_class_dics = {}
	file_fraction_dics = {}
	rows = booksheet.nrows
	for i in range(rows):
		raw_name = booksheet.cell_value(i,0).split('.')[0]
		sample_name = str(booksheet.cell_value(i,1))
		fraction_name = str(booksheet.cell_value(i,2))
		file_class_dics[raw_name] = sample_name
		file_fraction_dics[raw_name] = fraction_name
	result={}
	for file in os.listdir(file_dir):
		if not file.split('.')[0] in file_class_dics.keys():
				print('file not in list!')
				continue
		print('step_1:',file)
		sample=file_class_dics[file.split('.')[0]]
		fraction=file_fraction_dics[file.split('.')[0]]
		result=sample_pretreat(file_dir+'/'+file,sample,fraction,result,bin_precision)
	return result
