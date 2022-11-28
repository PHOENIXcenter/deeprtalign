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

def mass_filter(file_dir,file,result_dir,min_time_diff):
	df=pd.read_csv(file_dir+'/'+file,converters={'Tmass':str})
	grouped=df.groupby(['sample','fraction'])
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
	df.to_csv(result_dir+'/'+file,index=False)
def run_mass_filter(processing_number,min_time_diff):
	file_dir='shift_result_bins'
	result_dir='shift_result_bins_filter'
	
	if not os.path.exists(result_dir):
		os.mkdir(result_dir)
	
	pool_arg=[]
	for file in os.listdir(file_dir):
		file_arg=[]
		file_arg.append(file_dir)
		file_arg.append(file)
		file_arg.append(result_dir)
		file_arg.append(min_time_diff)
		pool_arg.append(file_arg)
	print('step_4: running')
	pool=mp.Pool(processes=processing_number)
	pool.starmap_async(mass_filter,pool_arg)
	pool.close()
	pool.join()
	print('step_4: finish')