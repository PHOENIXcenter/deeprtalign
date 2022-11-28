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
import torch.nn.functional as F
from torch import optim
import torch.utils.data as Data
import numpy as np
import pandas as pd
import os
import shutil
import multiprocessing as mp
import pkg_resources

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

def get_np_from_df(df,dimension,intensity,time):
	mass_np=np.empty((dimension,2))
	df=df.sort_values(by='Ttime',ascending=True)
	df.reset_index(drop=True,inplace=True)
	mass_df=df[df['Tintensity']==intensity]
	best_index=mass_df.index[0]
	if not len(mass_df)==1:
		time_diff_best=10000
		for index in mass_df.index:
			mass_time=mass_df.loc[index]['Ttime']
			time_diff=abs(mass_time-time)
			if time_diff<time_diff_best:
				time_diff_best=time_diff
				best_index=index
	middle_dimension=dimension//2
	for m in range(middle_dimension+1):
		if best_index-m>=0:
			intensity=df.loc[best_index-m]['Tintensity']
			time=df.loc[best_index-m]['Ttime']
			mass_np[middle_dimension-m]=np.array([intensity,time])
		else:
			mass_np[middle_dimension-m]=np.array([0,0])
		if best_index+m<len(df):
			intensity=df.loc[best_index+m]['Tintensity']
			time=df.loc[best_index+m]['Ttime']
			mass_np[middle_dimension+m]=np.array([intensity,time])
		else:
			mass_np[middle_dimension+m]=np.array([0,0])
	return mass_np

def mass_alignment(mass_folder,file,result_folder,total_sample_number,percent,done_mass_folder):
	params_file = pkg_resources.resource_filename('deeprtalign', 'data/params.pt')
	base_file = pkg_resources.resource_filename('deeprtalign', 'data/base.npy')
	net = MatchingNetwork()
	net.load_state_dict(torch.load(params_file,map_location=torch.device('cpu')))
	
	dimension=5
	
	base_1=np.load(base_file)
	base=base_1[0][2]
	
	mass_df=pd.read_csv(mass_folder+'/'+file,converters={'Tmass':str})

	sample_list=mass_df['sample'].value_counts()
	if len(sample_list)<(total_sample_number*percent):
		shutil.move(mass_folder+'/'+file, done_mass_folder)
		return 0
	sample_df=sample_list.to_frame(name='number')
	sample_df.sort_values(by='number',ascending=False,inplace=True)
	sample_df.reset_index(drop=False,inplace=True)
	sample_df.rename(columns={'index':'sample'},inplace=True)

	mass_df.sort_values(by='intensity',ascending=False,inplace=True)
	mass_df.reset_index(inplace=True,drop=True)
	mass_df['status']='unuse'
	mass_df['group']=-1
	
	sample_middle=int(len(sample_df)/2)
	sample_index=[]
	for k in range(len(sample_df)):
		if k==0:
			sample_index.append(sample_middle)
			continue
		if sample_middle-k>=0:
			sample_index.append(sample_middle-k)
		if sample_middle+k<len(sample_df):
			sample_index.append(sample_middle+k)
	sample_df=sample_df.reindex(sample_index)
	sample_df.reset_index(drop=True,inplace=True)
	
	group=0
	
	for sample_begin_index in sample_df.index:
		if sample_begin_index+1>= len(sample_df):
			break
		begin_sample=sample_df.loc[sample_begin_index]['sample']
		begin_sample_mass_df=mass_df[(mass_df['sample']==begin_sample)&(mass_df['status']=='unuse')]
		m=0
		for begin_index in begin_sample_mass_df.index:
			m=m+1
			mass_df.loc[begin_index,'status']='use'
			mass_df.loc[begin_index,'group']=group
			mass=begin_sample_mass_df.loc[begin_index]['Tmass']
			sample=begin_sample_mass_df.loc[begin_index]['sample']
			intensity=begin_sample_mass_df.loc[begin_index]['Tintensity']
			begin_time=begin_sample_mass_df.loc[begin_index]['Ttime']
			begin_charge=begin_sample_mass_df.loc[begin_index]['charge']
			fraction=int(begin_sample_mass_df.loc[begin_index]['fraction'].split('F')[-1])
			mass_df_sample=mass_df[(mass_df['sample']==sample)&(mass_df['fraction']=='F'+str(fraction))]
			mass_np_1=get_np_from_df(mass_df_sample,dimension,intensity,begin_time)
			mass_np_1=(mass_np_1-base)/base
			n=1
			while sample_begin_index+n< len(sample_df):
				next_sample=sample_df.loc[sample_begin_index+n]['sample']
				next_sample_mass_df=mass_df[(mass_df['sample']==next_sample)&(mass_df['status']=='unuse')]
				next_sample_mass_df=next_sample_mass_df[next_sample_mass_df['fraction']=='F'+str(fraction)]
				best_score=0
				best_next_index=-1
				for next_index in next_sample_mass_df.index:
					mass=next_sample_mass_df.loc[next_index]['Tmass']
					sample=next_sample_mass_df.loc[next_index]['sample']
					intensity=next_sample_mass_df.loc[next_index]['Tintensity']
					time=next_sample_mass_df.loc[next_index]['Ttime']
					next_charge=next_sample_mass_df.loc[next_index]['charge']
					if abs(begin_time-time)>5:
						continue
					fraction=int(next_sample_mass_df.loc[next_index]['fraction'].split('F')[-1])
					mass_df_sample=mass_df[(mass_df['sample']==sample)&(mass_df['fraction']=='F'+str(fraction))]
					mass_np_2=get_np_from_df(mass_df_sample,dimension,intensity,time)
					mass_np_2=(mass_np_2-base)/base
					cycle_1=np.expand_dims(mass_np_1[2],0).repeat(5,axis=0)-mass_np_2
					cycle_1=cycle_1.reshape(10)
					cycle_2=np.expand_dims(mass_np_2[2],0).repeat(5,axis=0)-mass_np_1
					cycle_2=cycle_2.reshape(10)
					re_mass_np_1=mass_np_1.reshape(10)
					re_mass_np_2=mass_np_2.reshape(10)
					cycle=np.hstack((cycle_1,cycle_2,re_mass_np_1,re_mass_np_2))
					cycle=torch.tensor(cycle,dtype=torch.float32)
					output = net(cycle)
					output = 1-output[0].tolist()
					if (output > best_score) and (output > 0.5):
						best_next_index=next_index
						break
				if best_next_index==-1:
					n=n+1
					continue
				mass_df.loc[best_next_index,'status']='use'
				mass_df.loc[best_next_index,'group']=group
				n=n+1
			group=group+1
	mass_df.to_csv(result_folder+'/'+file,index=False)
	shutil.move(mass_folder+'/'+file, done_mass_folder)
	return 1
	
def run_alignment(processing_number,percent):
	mass_folder='shift_result_bins_filter'
	done_mass_folder='shift_result_bins_filter_done'
	result_folder='mass_align_all'

	fraction_1=os.listdir('pre_result')[0]
	total_sample_number=len(os.listdir('pre_result/'+fraction_1))
	
	
	if not os.path.exists(result_folder):
		os.mkdir(result_folder)
	if not os.path.exists(done_mass_folder):
		os.mkdir(done_mass_folder)
	
	pool_arg=[]
	for file in os.listdir(mass_folder):
		file_arg=[]
		file_arg.append(mass_folder)
		file_arg.append(file)
		file_arg.append(result_folder)
		file_arg.append(total_sample_number)
		file_arg.append(percent)
		file_arg.append(done_mass_folder)
		pool_arg.append(file_arg)
	print('step_5: running')
	n=10000
	m=0
	while len(pool_arg)>n:
		m=m+1
		sub_pool_arg=pool_arg[:n]
		del pool_arg[:n]
		pool=mp.Pool(processes=processing_number,maxtasksperchild=10)
		result = pool.starmap_async(mass_alignment,sub_pool_arg)
		pool.close()
		pool.join()
		print('step_5:',str(m*n),'finish')
	pool=mp.Pool(processes=processing_number,maxtasksperchild=10)
	result = pool.starmap_async(mass_alignment,pool_arg)
	pool.close()
	pool.join()
	print('step_5: all finish')