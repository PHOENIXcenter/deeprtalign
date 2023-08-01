# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 16:28:49 2021

@author: leoicarus
"""
import os
import shutil
import math
import tracemalloc

def collect_bins(bin_width,bin_precision,dict_size):
	file_dir='shift_result'
	
	result_dir='shift_result_bins'
	
	if not os.path.exists(result_dir):
		os.mkdir(result_dir)
	
	shift_result={}
	tracemalloc.start()
	for fraction in os.listdir(file_dir):
		for file in os.listdir(file_dir+'/'+fraction):
			print('step_3:',file,fraction)
			file_path=file_dir+'/'+fraction+'/'+file
			sample=file.split('.csv')[0]
			file=open(file_path,'r')
			n=0
			for oneline in file:
				n=n+1
				if n==1:
					title_line='sample,fraction,'+oneline
					continue
				mass=oneline.split(',')[12].strip()
				mass_f=round(float(mass),bin_precision)
				bin_1_f=mass_f-bin_width+(1/math.pow(10,bin_precision))
				while bin_1_f<=mass_f:
					bin_2_f=bin_1_f+bin_width
					bin_1=str(round(bin_1_f,bin_precision))
					bin_2=str(round(bin_2_f,bin_precision))
					batch_number=int(bin_1_f*math.pow(10,bin_precision)/1000)
					new_key=result_dir+'/'+str(batch_number)+'/'+bin_1+'_'+bin_2+'.csv'
					if new_key in shift_result:
						shift_result[new_key]=shift_result[new_key]+sample+','+fraction+','+oneline
					else:
						shift_result[new_key]=sample+','+fraction+','+oneline
					bin_1_f=bin_1_f+(1/math.pow(10,bin_precision))
				current, peak = tracemalloc.get_traced_memory()
				if current>dict_size*1024*1024:
					for key in shift_result:
						if not os.path.exists(key.split('/')[0]+'/'+key.split('/')[1]):
							os.mkdir(result_dir+'/'+key.split('/')[1])
						if not os.path.exists(key):
							result_file=open(key,'a')
							result_file.write(title_line)
							result_file.close()
						result_file=open(key,'a')
						result_file.write(shift_result[key])
						result_file.close()
					shift_result={}
	for key in shift_result:
		if not os.path.exists(key.split('/')[0]+'/'+key.split('/')[1]):
			os.mkdir(key.split('/')[0]+'/'+key.split('/')[1])
		if not os.path.exists(key):
			result_file=open(key,'a')
			result_file.write(title_line)
			result_file.close()
		result_file=open(key,'a')
		result_file.write(shift_result[key])
		result_file.close()
	shift_result={}
	tracemalloc.stop()
	for son_path in os.listdir(result_dir):
		dir_path=os.path.join(result_dir,son_path)
		if os.path.isdir(dir_path):
			print(dir_path)
			for file in os.listdir(dir_path):
				file = os.path.join(dir_path, file)
				shutil.move(file, result_dir)
			os.rmdir(dir_path)

