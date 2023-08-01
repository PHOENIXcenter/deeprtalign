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
import numpy as np
import math
import os
import re

def collect_information(bin_precision,bin_width,percent,pre_result,cut,keep_best):
	result_folder='mass_align_all_information'
	if not os.path.exists(result_folder):
		os.mkdir(result_folder)
		
	result_file=open(result_folder+'/information_all.csv','w')
	total_number=len(list(pre_result.keys()))
	n=0
	m=0
	for mass_name in list(pre_result.keys()):
		n=n+1
		window=mass_name
		print('step_6:',n,window,total_number)
		file_df=pre_result[mass_name]
		file_df=file_df[file_df['status']=='use']
		if len(file_df)==0:
			continue
		grouped=file_df.groupby('group')
		for name,group in grouped:
			window_group=window+'_'+str(name)
			group['group']=window_group
			for group_index in group.index:
				group_line=group.loc[[group_index]]
				m=m+1
				if m==1:
					result_s=group_line.to_string(justify='left',index=False)+'\n'
				else:
					result_s=group_line.to_string(justify='left',header=False,index=False)+'\n'
				result_s=re.sub(' +',',',result_s)
				result_s=re.sub(',\n','\n',result_s)
				result_s=re.sub('^,+','',result_s)
				result_file.write(result_s)
	result_file.close()
	df=pd.read_csv(result_folder+'/information_all.csv')
	df.sort_values(by='adj_score',ascending=False,inplace=True)
	df.reset_index(inplace=True,drop=True)
	
	total_number=0
	decoy_number=0
	df_decoy=df[(df['sample']=='decoy_sample_1')|(df['sample']=='decoy_sample_2')]
	
	this_adj_score=1
	for index in df_decoy.index:
		decoy_number=decoy_number+1
		total_number=index+1
		this_adj_score=df_decoy.loc[index]['adj_score']
		FDR=decoy_number/(total_number-decoy_number)
		if FDR>cut and total_number>1000:
			break
	df_target=df[(df['sample']!='decoy_sample_1')&(df['sample']!='decoy_sample_2')]
	df_target=df_target[df_target['adj_score']>this_adj_score]
	sample_number=len(df_target['sample'].value_counts())
	
	if len(df_target)==0:
		df_target.to_csv(result_folder+'/information_target.csv',index=False)
		return 0
	
	grouped=df_target.groupby('group')
	
	total_number=len(grouped)
	n=0
	for name,group in grouped:
		n=n+1
		print('step_6: first combining',n,'/',total_number)
		if len(group)<2:
			df_target.drop(list(group.index),inplace=True)
			continue
	if keep_best==1:
		df_target.sort_values(by='adj_score',ascending=False,inplace=True)
			
		group_list=[]
		
		grouped=df_target.groupby(['group'])
		align_df_result=pd.DataFrame()
		total_number=len(grouped)
		n=0
		for name,group in grouped:
			n=n+1
			print('step_6: second combining',n,'/',total_number)
			for index in group.index:
				this_mz=group.loc[index]['mz']
				this_intensity=group.loc[index]['intensity']
				this_time=group.loc[index]['time']
				this_sample=group.loc[index]['sample']
				this_feature=str(this_mz)+'_'+str(this_intensity)+'_'+str(this_time)+'_'+str(this_sample)
				if this_feature in group_list:
					group.drop(index,inplace=True)
					continue
			if len(group)<2:
				continue
			for index in group.index:
				this_mz=group.loc[index]['mz']
				this_intensity=group.loc[index]['intensity']
				this_time=group.loc[index]['time']
				this_sample=group.loc[index]['sample']
				this_feature=str(this_mz)+'_'+str(this_intensity)+'_'+str(this_time)+'_'+str(this_sample)
				group_list.append(this_feature)
			if len(align_df_result)==0:
				align_df_result=group
			else:
				align_df_result=pd.concat([align_df_result,group],sort=False,ignore_index=True)
		df_target=align_df_result
	df_target.to_csv(result_folder+'/information_target.csv',index=False)