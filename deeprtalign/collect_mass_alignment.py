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
import os

def collect_information():
	folder='mass_align_all'
	
	result_folder='mass_align_all_information'
	if not os.path.exists(result_folder):
		os.mkdir(result_folder)
	
	
	result_df=pd.DataFrame()
	total_number=len(os.listdir(folder))
	n=0
	m=0
	k=1
	for file in os.listdir(folder):
		n=n+1
		m=m+1
		file_path=folder+'/'+file
		window=file.split('.csv')[0]
		print('step_6:',n,window,total_number)
		file_df=pd.read_csv(file_path,converters={'Tmass':str})
		file_df=file_df[file_df['status']=='use']
		grouped=file_df.groupby(['group'])
		for name,group in grouped:
			window_group=window+'_'+str(name)
			group['group']=window_group
			if len(group)<2:
				continue
			if len(result_df)==0:
				result_df=group
			else:
				result_df=pd.concat([result_df,group],ignore_index=True,sort=False)
		if total_number>10000:
			if m>10000:
				result_df.to_csv(result_folder+'/'+'information_'+str(k)+'.csv',index=False)
				result_df=pd.DataFrame()
				k=k+1
				m=0
	result_df.to_csv(result_folder+'/'+'information_'+str(k)+'.csv',index=False)