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

def sample_pretreat(filepath,sample,fraction,result_dir,bin_precision,mz_col,rt_col,intensity_col,charge_col):
	file=open(filepath,'r')
	file.readline()
	XICs={'charge':[],'time':[],'intensity':[],'mz':[]}
	while True: 
		oneline=file.readline()
		if not oneline:
			break
		n=1
		i=0
		j=0
		while j<len(oneline):
			if oneline[j]==',' or j==len(oneline)-1:
				if n==mz_col:
					XICs['mz'].append(float(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==rt_col:
					XICs['time'].append(float(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==intensity_col:
					XICs['intensity'].append(float(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==charge_col:
					XICs['charge'].append(float(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				n=n+1
				j=j+1
				i=j
			else:
				j=j+1
	try:
		df=pd.DataFrame(XICs)
	except:
		print(filepath+' is not complete!')
		erro_files=open('erro_files.txt','a')
		erro_files.write(filepath+'\n')
		erro_files.close()
		return False
	df=pd.DataFrame(XICs)
	drop_negative=df[(df['intensity']<0)].index
	df.drop(drop_negative,inplace=True)
	Tmz=df['mz']
	df.loc[:,'Tmz']=Tmz
	base=189346000000
	sum_of_intensity=df['intensity'].sum()
	Tintensity=[math.log2(a/sum_of_intensity*base)for a in df['intensity']]
	Tintensity10=[math.log10(a/sum_of_intensity*base)for a in df['intensity']]
	Pintensity=[a/sum_of_intensity for a in df['intensity']]
	#intensity=[(a/sum_of_intensity*base)for a in df['intensity']]
	#df.loc[:,'intensity']=intensity
	df.loc[:,'Tintensity']=Tintensity
	df.loc[:,'Tintensity10']=Tintensity10
	df.loc[:,'Pintensity']=Pintensity
	drop_zero=df[df['Tintensity']<=0].index
	df.drop(drop_zero,inplace=True)
	#Tmass=[str(round(c*float(d)-c*1.007276,2)) for c,d in zip(df['charge'],df['Tmz'])]
	Tmass=[str(round(a,bin_precision))for a in df['mz']]
	df.loc[:,'Tmass']=Tmass
	if not os.path.exists(result_dir):
		os.mkdir(result_dir)
	if not os.path.exists(result_dir+'/'+fraction):
		os.mkdir(result_dir+'/'+fraction)
	df.to_csv(result_dir+'/'+fraction+'/'+sample+'.csv',index=False)
	file.close()
	return True

def pre_step(file_dir,sample_file,bin_precision,mz_col,rt_col,intensity_col,charge_col):
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
	result_dir='pre_result'
	for file in os.listdir(file_dir):
		if not file.split('.')[0] in file_class_dics.keys():
				print('file not in list!')
				continue
		print('step_1:',file)
		sample=file_class_dics[file.split('.')[0]]
		fraction=file_fraction_dics[file.split('.')[0]]
		sample_pretreat(file_dir+'/'+file,sample,fraction,result_dir,bin_precision,mz_col,rt_col,intensity_col,charge_col)

