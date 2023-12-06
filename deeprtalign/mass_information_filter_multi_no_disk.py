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

import pandas as pd
import multiprocessing as mp
import os
import platform

def mass_filter(mass_name,df,min_time_diff):
	result={}
	grouped=df.groupby(['sample','fraction','charge'])
	for name,group in grouped:
		group_sort=group.sort_values(by='intensity',ascending=False).copy()
		while len(group_sort)>0:
			m=0
			for index in group_sort.index:
				if m==0:
					index_begin=index
					time_begin=group_sort.loc[index_begin]['Ttime']
					m=m+1
					group_sort.drop(index,axis=0,inplace=True)
				else:
					time=group_sort.loc[index]['Ttime']
					if abs(time-time_begin)<min_time_diff:
						m=m+1
						group_sort.drop(index,axis=0,inplace=True)
						df.drop(index,axis=0,inplace=True)
	result[mass_name]=df
	return result
def run_mass_filter(processing_number,min_time_diff,pre_result):
	if processing_number==-1:
		processing_number=mp.cpu_count()
	if platform.system().lower()=='windows' and processing_number>60:
		processing_number=60
	pool_arg=[]
	for mass_name in pre_result.keys():
		df=pre_result[mass_name]
		file_arg=[]
		file_arg.append(mass_name)
		file_arg.append(df)
		file_arg.append(min_time_diff)
		pool_arg.append(file_arg)
	result_dict={}
	print('step_4: running')
	pool=mp.Pool(processes=processing_number)
	result=pool.starmap(mass_filter,pool_arg)
	pool.close()
	pool.join()
	print('step_4: finish')
	for result_dict_1 in result:
		result_dict.update(result_dict_1)
	return result_dict