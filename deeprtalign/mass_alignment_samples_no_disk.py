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

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import os
import shutil
import pkg_resources
import random

class MatchingNetwork(nn.Module):
	def __init__(self):
		super().__init__()
		self.linear1 = nn.Sequential(
			nn.Linear(40, 5000),
			nn.Sigmoid(),
			
			nn.Linear(5000, 5000),
			nn.Sigmoid(),
			
			nn.Linear(5000, 5000),
			nn.Sigmoid()
			)

		self.fc1 = nn.Sequential(
			nn.Linear(5000, 1),
			nn.Sigmoid()
			)

	def forward(self, x):
		output = self.linear1(x)
		output = self.fc1(output)
		
		return output

def mass_alignment(pre_result,result,total_fraction_number,total_sample_number,max_mz,max_time,max_log_intensity,percent):
	pd.set_option('mode.chained_assignment', None)
	total_number=len(pre_result)
	mass_name_number=0
	for mass_name in pre_result.keys():
		mass_df=pre_result[mass_name]
		mass_name_number=mass_name_number+1
		print('step_5:',mass_name_number,mass_name,total_number)
		sample_fraction_list=mass_df[['sample','fraction']].value_counts()
		if len(sample_fraction_list)<(total_sample_number*total_fraction_number*percent):
			continue
		
		sample_list=mass_df[['sample']].value_counts()
		if len(sample_list)<2:
			continue
		
		mass_df.sort_values(by='Ttime',ascending=False,inplace=True)
		r_n_1=random.randint(0, len(sample_list)-1)
		sample_decoy_1=sample_list.index[r_n_1][0]
		mass_df_decoy_1=mass_df[mass_df['sample']==sample_decoy_1].copy()
		mass_df_decoy_1.loc[:,'sample']='decoy_sample_1'
		mass_df_decoy_1.loc[:,'Ttime']=mass_df_decoy_1['Ttime'].apply(lambda x: 40-x if x<40 else 120-x)
		mass_df_decoy_1.loc[:,'Ttime']=mass_df_decoy_1['Ttime'].apply(lambda x: 80-x)
		sample_decoy_2=sample_list.index[r_n_1][0]
		mass_df_decoy_2=mass_df[mass_df['sample']==sample_decoy_2].copy()
		mass_df_decoy_2.loc[:,'sample']='decoy_sample_2'
		mass_df_decoy=pd.concat([mass_df_decoy_1,mass_df_decoy_2],ignore_index=True)
		
		mass_df.loc[:,'status']='unuse'
		mass_df.loc[:,'group']=-1
		mass_df.loc[:,'mz_error']=-1
		mass_df.loc[:,'score']=0
		
		mass_df_decoy.loc[:,'status']='unuse'
		mass_df_decoy.loc[:,'group']=-1
		mass_df_decoy.loc[:,'mz_error']=-1
		mass_df_decoy.loc[:,'score']=0
		
		aligned_result,aligned_result_score,aligned_result_mz_error=get_aligned_result(mass_name,mass_df,max_mz,max_time,max_log_intensity)
	
		for group in aligned_result.index:
			for sample in list(aligned_result.columns):
				sample_index=aligned_result.loc[group][sample]
				score=aligned_result_score.loc[group][sample]
				mz_error=aligned_result_mz_error.loc[group][sample]
				if np.isnan(sample_index):
					continue
				mass_df.loc[sample_index,'group']=group
				mass_df.loc[sample_index,'status']='use'
				mass_df.loc[sample_index,'score']=score
				mass_df.loc[sample_index,'mz_error']=mz_error
		
		
		#sample_list=mass_df_decoy[['sample','fraction']].value_counts()
		
		aligned_result,aligned_result_score,aligned_result_mz_error=get_aligned_result(mass_name,mass_df_decoy,max_mz,max_time,max_log_intensity)
	
		for group in aligned_result.index:
			for sample in list(aligned_result.columns):
				sample_index=aligned_result.loc[group][sample]
				score=aligned_result_score.loc[group][sample]
				mz_error=aligned_result_mz_error.loc[group][sample]
				if np.isnan(sample_index):
					continue
				mass_df_decoy.loc[sample_index,'group']=group
				mass_df_decoy.loc[sample_index,'status']='use'
				mass_df_decoy.loc[sample_index,'score']=score
				mass_df_decoy.loc[sample_index,'mz_error']=mz_error
		
		mass_df=pd.concat([mass_df,mass_df_decoy],ignore_index=True)
		mass_df.sort_values(by='Ttime',ascending=True,inplace=True)
		grouped=mass_df.groupby('sample')
		for sample,mass_df_sample in grouped:
			n=0
			while n<len(mass_df_sample):
				status=mass_df_sample.iloc[n]['status']
				if status=='unuse':
					n=n+1
					continue
				index=mass_df_sample.iloc[[n]].index[0]
				scores=[]
				for m in range(n-2,n+3):
					if m<0 or m>=len(mass_df_sample):
						scores.append(0)
					else:
						score=mass_df_sample.iloc[m]['score']
						if m==n:
							score=6*score
						scores.append(score)
				mass_df.loc[index,'adj_score']=np.mean(scores)
				n=n+1
		result[mass_name]=mass_df
	return result

def get_aligned_result(mass_name,mass_df,max_mz,max_time,max_log_intensity):
	pd.set_option('mode.chained_assignment', None)
	params_file = pkg_resources.resource_filename('deeprtalign', 'data/params.pt')
	net = MatchingNetwork()
	net.load_state_dict(torch.load(params_file,map_location=torch.device('cpu')))
	dimension=5
	
	

	matrix=[]
	score_result={'sample_1_index':[],'sample_2_index':[],'sample_1':[],'sample_2':[],'fraction':[],'charge':[],'mz_error':[],'Ttime_diff':[]}
	mass_df.sort_values(by='Ttime',ascending=True,inplace=True)
	sample_grouped=mass_df.groupby(['sample','fraction','charge'])
	sample_group_dic={}
	mass_decoy_0=float(mass_name.split('_')[0])-0.1
	df_null_0=mass_df.iloc[[0]].copy()
	df_null_0.index=['null']
	df_null_0.loc['null','time']=0
	df_null_0.loc['null','mz']=0
	df_null_0.loc['null','Ttime']=-10
	df_null_0.loc['null','Tmz']=mass_decoy_0
	
	mass_decoy_1=float(mass_name.split('_')[0])-0.1
	df_null_1=mass_df.iloc[[-1]].copy()
	df_null_1.index=['null']
	df_null_1.loc['null','time']=0
	df_null_1.loc['null','mz']=0
	df_null_1.loc['null','Ttime']=90
	df_null_1.loc['null','Tmz']=mass_decoy_1
	for name,sample_group in sample_grouped:
		key_name=name[0]+'_'+str(name[1])+'_'+str(name[2])
		sample_df=pd.concat([df_null_0,sample_group])
		sample_df=pd.concat([df_null_0,sample_df])
		sample_df=pd.concat([sample_df,df_null_1])
		sample_df=pd.concat([sample_df,df_null_1])
		sample_group_dic[key_name]=sample_df
	
	grouped=mass_df.groupby(['fraction','charge'])
	for name,group in grouped:
		n=0
		while n<len(group):
			sample_n=group.iloc[n]['sample']
			mz_n=group.iloc[n]['Tmz']
			time_n=group.iloc[n]['Ttime']
			intensity_n=group.iloc[n]['Tintensity']
			begin_index=group.iloc[[n]].index[0]
			begin_sample_df=sample_group_dic[sample_n+'_'+str(name[0])+'_'+str(name[1])]
			j=begin_sample_df.index.get_loc(begin_index)
			begin_sample_mass_df=begin_sample_df.iloc[j-2:j+3]
			
			m=n+1
			while m<len(group):
				sample_m=group.iloc[m]['sample']
				mz_m=group.iloc[m]['Tmz']
				time_m=group.iloc[m]['Ttime']
				intensity_m=group.iloc[m]['Tintensity']
				if sample_n==sample_m:
					m=m+1
					continue
				if abs(time_m-time_n)>max_time:
					break
				if abs(intensity_m-intensity_n)>max_log_intensity:
					m=m+1
					continue
				if abs((mz_n-mz_m)/mz_m*1000000)>max_mz:
					m=m+1
					continue
				next_index=group.iloc[[m]].index[0]
				next_sample_df=sample_group_dic[sample_m+'_'+str(name[0])+'_'+str(name[1])]
				k=next_sample_df.index.get_loc(next_index)
				next_sample_mass_df=next_sample_df.iloc[k-2:k+3]
				matrix,score_result=get_input_matrix(begin_sample_mass_df,next_sample_mass_df,matrix,score_result,dimension)
				m=m+1
			n=n+1
	aligned_result=pd.DataFrame()
	aligned_result_score=pd.DataFrame()
	aligned_result_mz_error=pd.DataFrame()
	if len(matrix)==0:
		return aligned_result,aligned_result_score,aligned_result_mz_error
	matrix=torch.tensor(matrix,dtype=torch.float32)
	output=net(matrix)
	score_result=pd.DataFrame(score_result)
	output=output.view([len(score_result)])
	score=1-output.detach().numpy()
	score_result.loc[:,'score']=score
	#score_result_target=score_result[score_result['score']>0.5]
	score_result_target=score_result
	score_result_target.sort_values(by='Ttime_diff',ascending=True,inplace=True,ignore_index=True)
	score_result_target.sort_values(by='score',ascending=False,inplace=False,ignore_index=True)
	group_num=0
	

	for index in score_result_target.index:
		score=score_result_target.loc[index]['score']
		mz_error=score_result_target.loc[index]['mz_error']
		sample_1_index=score_result_target.loc[index]['sample_1_index']
		sample_2_index=score_result_target.loc[index]['sample_2_index']
		sample_1=score_result_target.loc[index]['sample_1']
		sample_2=score_result_target.loc[index]['sample_2']
		aligned_result.loc[group_num,sample_1]=sample_1_index
		aligned_result.loc[group_num,sample_2]=sample_2_index
		aligned_result_score.loc[group_num,sample_1]=score
		aligned_result_score.loc[group_num,sample_2]=score
		aligned_result_mz_error.loc[group_num,sample_1]=mz_error
		aligned_result_mz_error.loc[group_num,sample_2]=mz_error
		group_num=group_num+1
	
	total_number=len(aligned_result)-1
	
	index=1
	while index<total_number:
		best_index=index
		for sample in list(aligned_result.loc[[index]].notnull().columns):
			sample_index=aligned_result.loc[index][sample]
			if sample_index in list(aligned_result[sample])[0:index]:
				group_index=aligned_result[aligned_result[sample]==sample_index].iloc[[0]].index[0]
				if group_index<best_index:
					best_index=group_index
		if best_index<index:
			for sample in list(aligned_result.columns):
					sample_index=aligned_result.loc[index][sample]
					score=aligned_result_score.loc[index][sample]
					mz_error=aligned_result_mz_error.loc[index][sample]
					if np.isnan(sample_index):
						continue
					if np.isnan(aligned_result.loc[best_index][sample]):
						aligned_result.loc[group_index,sample]=sample_index
						aligned_result_score.loc[group_index,sample]=score
						aligned_result_mz_error.loc[group_index,sample]=mz_error
			aligned_result.drop(index,axis=0,inplace=True)
			aligned_result_score.drop(index,axis=0,inplace=True)
			aligned_result_mz_error.drop(index,axis=0,inplace=True)
		index=index+1
	aligned_result.reset_index(inplace=True,drop=True)
	aligned_result_score.reset_index(inplace=True,drop=True)
	aligned_result_mz_error.reset_index(inplace=True,drop=True)
	
	total_number=len(aligned_result)-1
	
	index=1
	while index<total_number:
		best_index=index
		for sample in list(aligned_result.loc[[index]].notnull().columns):
			sample_index=aligned_result.loc[index][sample]
			if sample_index in list(aligned_result[sample])[0:index]:
				group_index=aligned_result[aligned_result[sample]==sample_index].iloc[[0]].index[0]
				if group_index<best_index:
					best_index=group_index
		if best_index<index:
			for sample in list(aligned_result.columns):
					sample_index=aligned_result.loc[index][sample]
					score=aligned_result_score.loc[index][sample]
					mz_error=aligned_result_mz_error.loc[index][sample]
					if np.isnan(sample_index):
						continue
					if np.isnan(aligned_result.loc[best_index][sample]):
						aligned_result.loc[best_index,sample]=sample_index
						aligned_result_score.loc[best_index,sample]=score
						aligned_result_mz_error.loc[best_index,sample]=mz_error
						aligned_result.loc[index,sample]=np.nan
						aligned_result_score.loc[index,sample]=np.nan
						aligned_result_mz_error.loc[index,sample]=np.nan
						if aligned_result.loc[[index]].notnull().count().sum()<2:
							aligned_result.drop(index,axis=0,inplace=True)
							aligned_result_score.drop(index,axis=0,inplace=True)
							aligned_result_mz_error.drop(index,axis=0,inplace=True)
						continue
					if aligned_result.loc[best_index][sample]==sample_index:
						aligned_result.loc[index,sample]=np.nan
						aligned_result_score.loc[index,sample]=np.nan
						aligned_result_mz_error.loc[index,sample]=np.nan
						if aligned_result.loc[[index]].notnull().count().sum()<2:
							aligned_result.drop(index,axis=0,inplace=True)
							aligned_result_score.drop(index,axis=0,inplace=True)
							aligned_result_mz_error.drop(index,axis=0,inplace=True)
						continue
		index=index+1
	aligned_result.dropna(how='all',inplace=True)
	aligned_result_score.dropna(how='all',inplace=True)
	aligned_result_mz_error.dropna(how='all',inplace=True)
	aligned_result.reset_index(inplace=True,drop=True)
	aligned_result_score.reset_index(inplace=True,drop=True)
	aligned_result_mz_error.reset_index(inplace=True,drop=True)
	
	total_number=len(aligned_result)-1
	
	index=1
	while index<total_number:
		best_index=index
		for sample in list(aligned_result.loc[[index]].notnull().columns):
			sample_index=aligned_result.loc[index][sample]
			if sample_index in list(aligned_result[sample])[0:index]:
				group_index=aligned_result[aligned_result[sample]==sample_index].iloc[[0]].index[0]
				if group_index<best_index:
					best_index=group_index
		if best_index<index:
			for sample in list(aligned_result.columns):
					sample_index=aligned_result.loc[index][sample]
					score=aligned_result_score.loc[index][sample]
					mz_error=aligned_result_mz_error.loc[index][sample]
					if np.isnan(sample_index):
						continue
					if np.isnan(aligned_result.loc[best_index][sample]):
						aligned_result.loc[best_index,sample]=sample_index
						aligned_result_score.loc[best_index,sample]=score
						aligned_result_mz_error.loc[best_index,sample]=mz_error
						aligned_result.loc[index,sample]=np.nan
						aligned_result_score.loc[index,sample]=np.nan
						aligned_result_mz_error.loc[index,sample]=np.nan
						if aligned_result.loc[[index]].notnull().count().sum()<2:
							aligned_result.drop(index,axis=0,inplace=True)
							aligned_result_score.drop(index,axis=0,inplace=True)
							aligned_result_mz_error.drop(index,axis=0,inplace=True)
						continue
					if aligned_result.loc[best_index][sample]==sample_index:
						aligned_result.loc[index,sample]=np.nan
						aligned_result_score.loc[index,sample]=np.nan
						aligned_result_mz_error.loc[index,sample]=np.nan
						if aligned_result.loc[[index]].notnull().count().sum()<2:
							aligned_result.drop(index,axis=0,inplace=True)
							aligned_result_score.drop(index,axis=0,inplace=True)
							aligned_result_mz_error.drop(index,axis=0,inplace=True)
						continue
		index=index+1
	aligned_result.dropna(how='all',inplace=True)
	aligned_result_score.dropna(how='all',inplace=True)
	aligned_result_mz_error.dropna(how='all',inplace=True)
	aligned_result.reset_index(inplace=True,drop=True)
	aligned_result_score.reset_index(inplace=True,drop=True)
	aligned_result_mz_error.reset_index(inplace=True,drop=True)
	
	aligned_result.sort_index(ascending=False,inplace=True,ignore_index=True)
	aligned_result_score.sort_index(ascending=False,inplace=True,ignore_index=True)
	aligned_result_mz_error.sort_index(ascending=False,inplace=True,ignore_index=True)
	
	return aligned_result,aligned_result_score,aligned_result_mz_error



def get_input_matrix(begin_sample_mass_df,next_sample_mass_df,matrix,score_result,dimension):
	pd.set_option('mode.chained_assignment', None)
	begin_sample=begin_sample_mass_df.iloc[2]['sample']
	next_sample=next_sample_mass_df.iloc[2]['sample']
	begin_fraction=begin_sample_mass_df.iloc[2]['fraction']
	begin_charge=begin_sample_mass_df.iloc[2]['charge']
	begin_Ttime=begin_sample_mass_df.iloc[2]['Ttime']
	next_Ttime=next_sample_mass_df.iloc[2]['Ttime']
	begin_mz=begin_sample_mass_df.iloc[2]['Tmz']
	next_mz=next_sample_mass_df.iloc[2]['Tmz']

	score_result['sample_1_index'].append(begin_sample_mass_df.iloc[[2]].index[0])
	score_result['sample_2_index'].append(next_sample_mass_df.iloc[[2]].index[0])
	score_result['sample_1'].append(begin_sample)
	score_result['sample_2'].append(next_sample)
	score_result['fraction'].append(begin_fraction)
	score_result['charge'].append(begin_charge)
	score_result['mz_error'].append(abs(begin_mz-next_mz))
	score_result['Ttime_diff'].append(abs(begin_Ttime-next_Ttime))
	
	mass_np_1=begin_sample_mass_df.iloc[0:5][['Ttime','Tmz']].values
	mass_np_2=next_sample_mass_df.iloc[0:5][['Ttime','Tmz']].values

	base_1=np.array([5,0.03])
	base_2=np.array([80,1500])

	cycle_1=abs(np.expand_dims(mass_np_1[2],0).repeat(5,axis=0)-mass_np_2)
	cycle_1=cycle_1/base_1
	re_cycle_1=cycle_1.reshape(10)
	cycle_2=abs(np.expand_dims(mass_np_2[2],0).repeat(5,axis=0)-mass_np_1)
	cycle_2=cycle_2/base_1
	re_cycle_2=cycle_2.reshape(10)
	mass_np_1=mass_np_1/base_2
	mass_np_2=mass_np_2/base_2
	re_mass_np_1=mass_np_1.reshape(10)
	re_mass_np_2=mass_np_2.reshape(10)
	cycle=np.hstack((re_cycle_1,re_cycle_2,re_mass_np_1,re_mass_np_2))
	if len(matrix)==0:
		matrix=np.array([cycle])
	else:
		matrix=np.append(matrix,[cycle],axis=0)
	return matrix,score_result


def run_alignment(max_mz,max_time,max_log_intensity,percent,total_fraction_number,total_sample_number,pre_result):
	result={}
	pd.set_option('mode.chained_assignment', None)
	
	result=mass_alignment(pre_result,result,total_fraction_number,total_sample_number,max_mz,max_time,max_log_intensity,percent)
	return result