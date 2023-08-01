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

def collect_shift(time_window,pre_result):
	result={}
	
	fraction_1=list(pre_result.keys())[0]
	anchor_sample=list(pre_result[fraction_1].keys())[0]
	
	
	
	for fraction in list(pre_result.keys()):
		anchor=pre_result[fraction][anchor_sample]
		anchor.sort_values(by='time',ascending=True,inplace=True)
		time_total=anchor.iloc[-1]['time']-anchor.iloc[0]['time']
		anchor['Ttime']=anchor['time'].apply(lambda x:x/time_total*80)
		
		if fraction in result.keys():
			result[fraction][anchor_sample]=anchor.copy()
		else:
			result[fraction]={}
			result[fraction][anchor_sample]=anchor.copy()
		anchor.sort_values(by='intensity',ascending=False,inplace=True)
		anchor.drop_duplicates(['Tmass'],keep='first',inplace=True)
		for sample_name in list(pre_result[fraction].keys()):
			if sample_name==anchor_sample:
				continue
			else:
				print('step_2:',fraction,sample_name)
				sample_result=pd.DataFrame()
				sample=pre_result[fraction][sample_name]
				sample.sort_values(by='time',ascending=True,inplace=True)
				time_total=sample.iloc[-1]['time']-sample.iloc[0]['time']
				sample['Ttime']=sample['time'].apply(lambda x:x/time_total*80)
				sample_sort=sample.sort_values(by='intensity',ascending=False)
				sample_drop=sample_sort.drop_duplicates(['Tmass'],keep='first')
				df = pd.merge(anchor, sample_drop, on=['Tmass'], how='inner')
				df['shift']=df.apply(lambda x:int(x['Ttime_x']-x['Ttime_y']),axis=1)
				df.sort_values(by='Ttime_y',ascending=True,inplace=True)
				time_begin=int(df.iloc[0]['Ttime_y'])
				time_end=int(df.iloc[-1]['Ttime_y'])+time_window
				time_1=time_begin-1
				time_2=time_1+time_window
				average_time_shift=0
				while time_2<=time_end:
					df_12=df[(df['Ttime_y']>=time_1)&(df['Ttime_y']<time_2)]
					if not len(df_12)==0:
						mode_time=df_12['shift'].mode().iloc[0]
						df_12=df[(df['shift']>mode_time-5)&(df['shift']<mode_time+5)]
						average_time_shift=df_12['shift'].mean(axis=0)
					sample_12=sample[(sample['Ttime']>=time_1)&(sample['Ttime']<time_2)].copy()
					if len(sample_12)==0:
						time_1=time_1+time_window
						time_2=time_2+time_window
						continue
					sample_12['Ttime']=sample_12.apply(lambda x:x['Ttime']+average_time_shift,axis=1)
					if len(sample_result)==0:
						sample_result=sample_12
					else:
						sample_result=pd.concat([sample_result,sample_12],ignore_index=True,sort=False)
					time_1=time_1+time_window
					time_2=time_2+time_window
				if fraction in result.keys():
					result[fraction][sample_name]=sample_result.copy()
				else:
					result[fraction]={}
					result[fraction][sample_name]=sample_result.copy()
	return result