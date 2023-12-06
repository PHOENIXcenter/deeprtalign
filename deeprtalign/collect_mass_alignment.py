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

def collect_information(bin_precision,bin_width,percent,cut,keep_best_feature,keep_best_group):
	folder='mass_align_all'
	
	result_folder='mass_align_all_information'
	if not os.path.exists(result_folder):
		os.mkdir(result_folder)
	
	
	total_number=len(os.listdir(folder))
	n=0
	for file in os.listdir(folder):
		n=n+1
		file_path=folder+'/'+file
		window=file.split('.csv')[0]
		print('step_6: first combining',n,window,total_number)
		file_df=pd.read_csv(file_path)
		if n==1:
			file_df.to_csv(result_folder+'/information_all.csv',index=False)
		else:
			file_df.to_csv(result_folder+'/information_all.csv',index=False,header=False,mode='a')
	df=pd.read_csv(result_folder+'/information_all.csv')
	df.sort_values(by='score',ascending=False,inplace=True)
	df.reset_index(inplace=True,drop=True)
	
	total_number=0
	decoy_number=0

	this_score=1
	df_decoy=df[((df['sample_1'].str.contains('decoy_sample'))|(df['sample_2'].str.contains('decoy_sample')))]
	for index in df_decoy.index:
		decoy_number=decoy_number+1
		total_number=index+1
		this_score=df_decoy.loc[index]['score']
		if total_number<1000:
			continue
		FDR=decoy_number/(total_number-decoy_number)
		if FDR>cut and total_number>1000:
			break
	df_target=df[~((df['sample_1'].str.contains('decoy_sample'))|(df['sample_2'].str.contains('decoy_sample')))]
	df_target=df_target[df_target['score']>this_score]
	
	grouped=df_target.groupby('mass_name')
	total_number=len(grouped)
	grouped_number=0
	for mass_name,group in grouped:
		grouped_number=grouped_number+1
		window=mass_name.split('.csv')[0]
		print('step_6: second combining',grouped_number,window,total_number)
		mass_name_df=pd.read_csv('shift_result_bins_filter_done/'+mass_name)
		all_index=[]
		group_list={}
		group_sample_list={}
		score_list={}
		group_number=0
		if keep_best_feature==1:
			for index in group.index:
				sample_1_index=group.loc[index]['sample_1_index']
				sample_2_index=group.loc[index]['sample_2_index']
				sample_1=group.loc[index]['sample_1']
				sample_2=group.loc[index]['sample_2']
				score=group.loc[index]['score']
				true_score=0
				if (sample_1_index in all_index) and (sample_2_index in all_index):
					for group_name in list(group_list):
						if sample_1_index in group_list[group_name]:
							group_name_1=group_name
						if sample_2_index in group_list[group_name]:
							group_name_2=group_name
					set_1=set(group_sample_list[group_name_1])
					set_2=set(group_sample_list[group_name_2])
					if len(set_1 & set_2)==0:
						group_list[group_name_1]=group_list[group_name_1]+group_list[group_name_2]
						del group_list[group_name_2]
						group_sample_list[group_name_1]=group_sample_list[group_name_1]+group_sample_list[group_name_2]
						del group_sample_list[group_name_2]
				if (sample_1_index in all_index) and not (sample_2_index in all_index):
					for group_name in list(group_list):
						if (sample_1_index in group_list[group_name]) and not (sample_2 in group_sample_list[group_name]):
							group_list[group_name].append(sample_2_index)
							group_sample_list[group_name].append(sample_2)
							all_index.append(sample_2_index)
							true_score=score
							break
				if (sample_2_index in all_index) and not (sample_1_index in all_index):
					for group_name in list(group_list):
						if (sample_2_index in group_list[group_name]) and not (sample_1 in group_sample_list[group_name]):
							group_list[group_name].append(sample_1_index)
							group_sample_list[group_name].append(sample_1)
							all_index.append(sample_1_index)
							true_score=score
							break
				if not ((sample_1_index in all_index) or (sample_2_index in all_index)):
					group_number=group_number+1
					group_name=mass_name.split('.csv')[0]+'_'+str(group_number)
					group_list[group_name]=[]
					group_list[group_name].append(sample_1_index)
					group_list[group_name].append(sample_2_index)
					group_sample_list[group_name]=[]
					group_sample_list[group_name].append(sample_1)
					group_sample_list[group_name].append(sample_2)
					all_index.append(sample_1_index)
					all_index.append(sample_2_index)
					true_score=score
	
				if sample_1_index in score_list:
					if true_score>score_list[sample_1_index]:
						score_list[sample_1_index]=true_score
				else:
					score_list[sample_1_index]=true_score
				if sample_2_index in score_list:
					if true_score>score_list[sample_2_index]:
						score_list[sample_2_index]=true_score
				else:
					score_list[sample_2_index]=true_score
		else:
			for index in group.index:
				sample_1_index=group.loc[index]['sample_1_index']
				sample_2_index=group.loc[index]['sample_2_index']
				score=group.loc[index]['score']
				true_score=0
				if (sample_1_index in all_index) and not  (sample_2_index in all_index):
					for group_name in group_list:
						if (sample_1_index in group_list[group_name]):
							group_list[group_name].append(sample_2_index)
							all_index.append(sample_2_index)
							true_score=score
				if (sample_2_index in all_index) and not (sample_1_index in all_index):
					for group_name in group_list:
						if (sample_2_index in group_list[group_name]) :
							group_list[group_name].append(sample_1_index)
							all_index.append(sample_1_index)
							true_score=score
				if not ((sample_1_index in all_index) or (sample_2_index in all_index)):
					group_number=group_number+1
					group_name=mass_name.split('.csv')[0]+'_'+str(group_number)
					group_list[group_name]=[]
					group_list[group_name].append(sample_1_index)
					group_list[group_name].append(sample_2_index)
					all_index.append(sample_1_index)
					all_index.append(sample_2_index)
					true_score=score
				if sample_1_index in score_list:
					if true_score>score_list[sample_1_index]:
						score_list[sample_1_index]=true_score
				else:
					score_list[sample_1_index]=true_score
				if sample_2_index in score_list:
					if true_score>score_list[sample_2_index]:
						score_list[sample_2_index]=true_score
				else:
					score_list[sample_2_index]=true_score
				
		mass_name_df.loc[:,'statu']='unuse'
		mass_name_df.loc[:,'score']=0
		for group_name in group_list:
			for sample_index in group_list[group_name]:
				mass_name_df.loc[sample_index,'statu']='use'
				mass_name_df.loc[sample_index,'group']=group_name
				mass_name_df.loc[sample_index,'score']=score_list[sample_index]
		mass_name_df=mass_name_df[mass_name_df['statu']=='use']
		if grouped_number==1:
			mass_name_df.to_csv(result_folder+'/information_target.csv',index=False)
		else:
			mass_name_df.to_csv(result_folder+'/information_target.csv',index=False,header=False,mode='a')

	df_target=pd.read_csv(result_folder+'/information_target.csv')
	df_target_grouped=df_target.groupby('group')
	grouped_number=0
	for names,group in df_target_grouped:
		feature_number=len(group)
		grouped_number=grouped_number+1
		for df_target_index in group.index:
			df_target.loc[df_target_index,'feature_number']=feature_number
	result=df_target
	if keep_best_group==1:
		result.sort_values(by=['feature_number','group'],ascending=False,inplace=True)
		result.drop_duplicates(['charge','time','intensity','mz'],keep='first',inplace=True)
	result.drop(['feature_number'],axis=1,inplace=True)
	result.sort_values(by='group',ascending=True,inplace=True)
	result_grouped=result.groupby('group')
	result_grouped_number=0
	m=0
	total_result_grouped_number=len(result_grouped)
	for mass_name,group in result_grouped:
		result_grouped_number=result_grouped_number+1
		print('step_6: last combining',result_grouped_number,mass_name,total_result_grouped_number)
		if len(group)<2:
			continue
		m=m+1
		if m==1:
			group.to_csv(result_folder+'/information_target.csv',index=False)
		else:
			group.to_csv(result_folder+'/information_target.csv',index=False,header=False,mode='a')