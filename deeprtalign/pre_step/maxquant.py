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

def sample_pretreat(filepath,sample,fraction,result_dir,file_class_dics,file_fraction_dics):
	file=open(filepath,'r')
	file.readline()
	i=0
	j=0
	XICs={'time':[],'mz':[],'charge':[],'intensity':[],'RT_length':[],'points':[],'scans':[],'peaks':[]}
	for oneline in file:
		n=1
		while j<len(oneline):
			if oneline[j]=='\t' or j==len(oneline)-1:
				if n==1:
					file_name=oneline[i:j]
					file_sample=file_class_dics[file_name]
					if not file_sample==sample:
						try:
							df=pd.DataFrame(XICs)
						except:
							print(filepath+' is not complete!')
							erro_files=open('erro_files.txt','a')
							erro_files.write(filepath+'\n')
							erro_files.close()
							return False
						df=pd.DataFrame(XICs)
						drop_negative=df[df['charge']==1].index
						df.drop(drop_negative,inplace=True)
						Tmz=[str(round(a,3))for a in df['mz']]
						df.loc[:,'Tmz']=Tmz
						sum_of_intensity=df['intensity'].sum()
						Tintensity=[math.log2(a)for a in df['intensity']]
						Tintensity10=[math.log10(a)for a in df['intensity']]
						df.loc[:,'Tintensity']=Tintensity
						Tmass=[str(round(a,2))for a in df['mz']]
						#Tmass=[str(round(c*float(d)-c*1.007276,2)) for c,d in zip(df['charge'],df['Tmz'])]
						df.loc[:,'Tmass']=Tmass
						df.loc[:,'Tintensity10']=Tintensity10
						Pintensity=[a/sum_of_intensity for a in df['intensity']]
						df.loc[:,'Pintensity']=Pintensity
						df.loc[:,'rt_start']=df['time']-df['RT_length']/2
						df.loc[:,'rt_end']=df['time']+df['RT_length']/2
						drop_zero=df[df['Tintensity']<=0].index
						df.drop(drop_zero,inplace=True)
						if not os.path.exists(result_dir):
							os.mkdir(result_dir)
						if not os.path.exists(result_dir+'/'+fraction):
							os.mkdir(result_dir+'/'+fraction)
						df.to_csv(result_dir+'/'+fraction+'/'+sample+'.csv',index=False)
						
						sample=file_sample
						fraction=file_fraction_dics[file_name]
						XICs={'time':[],'mz':[],'charge':[],'intensity':[],'RT_length':[],'points':[],'scans':[],'peaks':[]}
						
					n=n+1
					j=j+1
					i=j
					continue
				if n==3:
					XICs['charge'].append(int(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==4:
					XICs['mz'].append(float(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==8:
					XICs['points'].append(int(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==9:
					XICs['scans'].append(int(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==10:
					XICs['peaks'].append(int(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==16:
					XICs['time'].append(float(oneline[i:j]))
					n=n+1
					j=j+1
					i=j
					continue
				if n==17:
					XICs['RT_length'].append(float(oneline[i:j])/60)
					n=n+1
					j=j+1
					i=j
					continue
				if n==31:
					XICs['intensity'].append(float(oneline[i:j]))
					i=0
					j=0
					break
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
	#drop_negative=df[df['charge']==1].index
	#df.drop(drop_negative,inplace=True)
	Tmz=[str(round(a,3))for a in df['mz']]
	df.loc[:,'Tmz']=Tmz
	sum_of_intensity=df['intensity'].sum()
	Tintensity=[math.log2(a)for a in df['intensity']]
	Tintensity10=[math.log10(a)for a in df['intensity']]
	df.loc[:,'Tintensity']=Tintensity
	#Tmass=[str(round(c*float(d)-c*1.007276,2)) for c,d in zip(df['charge'],df['Tmz'])]
	Tmass=[str(round(a,2))for a in df['mz']]
	df.loc[:,'Tmass']=Tmass
	df.loc[:,'Tintensity10']=Tintensity10
	Pintensity=[a/sum_of_intensity for a in df['intensity']]
	df.loc[:,'Pintensity']=Pintensity
	df.loc[:,'rt_start']=df['time']-df['RT_length']/2
	df.loc[:,'rt_end']=df['time']+df['RT_length']/2
	drop_zero=df[df['Tintensity']<=0].index
	df.drop(drop_zero,inplace=True)
	if not os.path.exists(result_dir):
		os.mkdir(result_dir)
	if not os.path.exists(result_dir+'/'+fraction):
		os.mkdir(result_dir+'/'+fraction)
	df.to_csv(result_dir+'/'+fraction+'/'+sample+'.csv',index=False)
	file.close()
	return True


def pre_step(file_dir,sample_file):
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
	for raw_file in os.listdir(file_dir):
		print('step_1:',raw_file)
		file=open(file_dir+'/'+raw_file,'r')
		oneline=file.readline()
		oneline=file.readline()
		file_begin=oneline.split('\t')[0]
		sample=file_class_dics[file_begin]
		fraction=file_fraction_dics[file_begin]
		file.close()
		sample_pretreat(file_dir+'/'+raw_file,sample,fraction,result_dir,file_class_dics,file_fraction_dics)
