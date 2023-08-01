# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 16:28:49 2021

@author: leoicarus
"""
import pandas as pd
import math


def collect_bins(bin_width,bin_precision,pre_result):
	result={}
	total_fraction_number=len(pre_result)
	for fraction in list(pre_result.keys()):
		total_sample_number=len(pre_result[fraction])
		for sample_name in list(pre_result[fraction].keys()):
			print('step_3:',sample_name,fraction)
			sample=pre_result[fraction][sample_name]
			sample.loc[:,'sample']=sample_name
			sample.loc[:,'fraction']=fraction
			
			for index in sample.index:
				mass=sample.loc[index]['Tmz']
				mass_f=round(float(mass),bin_precision)
				bin_1_f=mass_f-bin_width+(1/math.pow(10,bin_precision))
				while bin_1_f<=mass_f:
					bin_2_f=bin_1_f+bin_width
					bin_1=str(round(bin_1_f,bin_precision))
					bin_2=str(round(bin_2_f,bin_precision))
					batch_number=int(bin_1_f*math.pow(10,bin_precision)/1000)
					new_key=bin_1+'_'+bin_2
					if not batch_number in result.keys():
						result[batch_number]={}
					if not new_key in result[batch_number].keys():
						result[batch_number][new_key]=sample.loc[[index]]
					else:
						result[batch_number][new_key]=pd.concat([result[batch_number][new_key],sample.loc[[index]]],ignore_index=True)
					bin_1_f=bin_1_f+(1/math.pow(10,bin_precision))
	result_all={}
	for batch_number in result.keys():
		result_all.update(result[batch_number])
	return result_all,total_fraction_number,total_sample_number

