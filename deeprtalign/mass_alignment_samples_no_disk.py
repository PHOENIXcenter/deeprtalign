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

def mass_alignment(pre_result,result,total_fraction_number,total_sample_number,max_mz,max_time,max_log_intensity,max_sample_number,percent):
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
		
		sample_list=mass_df['sample'].value_counts().index.tolist()
		if len(sample_list)<2:
			continue
		
		mass_df.sort_values(by='Ttime',ascending=False,inplace=True)
		
		score_result=get_aligned_result(mass_name,mass_df,max_mz,max_time,max_log_intensity,max_sample_number)
		score_result_decoy_all=pd.DataFrame()
		for sample_decoy in sample_list:
			sample_decoy_1=sample_decoy
			mass_df_decoy_1=mass_df[mass_df['sample']==sample_decoy_1].copy()
			mass_df_decoy_1.loc[:,'sample']='decoy_sample_1'
			mass_df_decoy_1.loc[:,'Ttime']=mass_df_decoy_1['Ttime'].apply(lambda x: 40-x if x<40 else 120-x)
			mass_df_decoy_1.loc[:,'Ttime']=mass_df_decoy_1['Ttime'].apply(lambda x: 80-x)
			sample_decoy_2=sample_decoy
			mass_df_decoy_2=mass_df[mass_df['sample']==sample_decoy_2].copy()
			mass_df_decoy_2.loc[:,'sample']='decoy_sample_2'
			mass_df_decoy=pd.concat([mass_df_decoy_1,mass_df_decoy_2],ignore_index=True)
			score_result_decoy=get_aligned_result(mass_name,mass_df_decoy,max_mz,max_time,max_log_intensity,max_sample_number)
			if len(score_result_decoy_all)==0:
				score_result_decoy_all=score_result_decoy
			else:
				score_result_decoy_all=pd.concat([score_result_decoy_all,score_result_decoy],ignore_index=True)
		
		score_result=pd.concat([score_result,score_result_decoy_all],ignore_index=True)
		result[mass_name]=score_result
	return result

def get_aligned_result(mass_name,mass_df,max_mz,max_time,max_log_intensity,max_sample_number):
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
			valid=0
			while m<len(group):
				time_m=group.iloc[m]['Ttime']
				if abs(time_m-time_n)>max_time:
					break
				sample_m=group.iloc[m]['sample']
				if sample_n==sample_m:
					m=m+1
					continue
				mz_m=group.iloc[m]['Tmz']
				if abs((mz_n-mz_m)/mz_m*1000000)>max_mz:
					m=m+1
					continue
				intensity_m=group.iloc[m]['Tintensity']
				if abs(intensity_m-intensity_n)>max_log_intensity:
					m=m+1
					continue
				next_index=group.iloc[[m]].index[0]
				next_sample_df=sample_group_dic[sample_m+'_'+str(name[0])+'_'+str(name[1])]
				k=next_sample_df.index.get_loc(next_index)
				next_sample_mass_df=next_sample_df.iloc[k-2:k+3]
				matrix,score_result=get_input_matrix(begin_sample_mass_df,next_sample_mass_df,matrix,score_result,dimension)
				m=m+1
				valid=valid+1
				if (not max_sample_number==-1) and (valid>=max_sample_number):
					break
			n=n+1
	score_result=pd.DataFrame(score_result)
	if len(matrix)==0:
		return score_result
	matrix=torch.tensor(matrix,dtype=torch.float32)
	output=net(matrix)
	output=output.view([len(score_result)])
	score=1-output.detach().numpy()
	score_result.loc[:,'score']=score
	score_result.loc[:,'mass_name']=mass_name
	
	return score_result



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


def run_alignment(max_mz,max_time,max_log_intensity,percent,total_fraction_number,total_sample_number,max_sample_number,pre_result):
	result={}
	pd.set_option('mode.chained_assignment', None)
	
	result=mass_alignment(pre_result,result,total_fraction_number,total_sample_number,max_mz,max_time,max_log_intensity,max_sample_number,percent)
	return pre_result,result