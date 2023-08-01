# -*- coding: utf-8 -*-
"""
Created on Fri May  5 10:33:26 2023

@author: liuyi
"""
import pandas as pd
import math

peptide_file_1='openms_result_ecoli_bg_ed/E4801_230403_200ng_293T_15ng_Ecoli_05xiRT_60min_DDA_R1_ecoli.csv'
peptide_file_2='openms_result_ecoli_bg_ed/E4801_230402_200ng_293T_10ng_Ecoli_05xiRT_60min_DDA_R1_ecoli.csv'


file='mass_align_all_information/information_target.csv'

result_name='15_10_R1_Ecoli_deeprtalign_FC_openms_information_target_0.01_20230712.csv'

sample_1='480_1_15_R1'
sample_2='480_1_10_R1'

peptide_df_1=pd.read_csv(peptide_file_1)
peptide_df_2=pd.read_csv(peptide_file_2)
peptide_df=pd.concat([peptide_df_1,peptide_df_2],ignore_index=True)

result={'sample_1':[],'sample_2':[],'FC':[],'peptide':[],'peptide_modi':[],'charge':[],'sample_1_mz':[],'sample_1_rt':[],'sample_1_intensity':[],'sample_2_mz':[],'sample_2_rt':[],'sample_2_intensity':[],'adj_score':[]}

groups=[]

df=pd.read_csv(file)

total_num=len(peptide_df)
n=0
for index in peptide_df.index:
	n=n+1
	print(n,'/',total_num)
	sample_mz=peptide_df.loc[index]['mz']
	sample_rt=peptide_df.loc[index]['rt']/60
	sample_intensity=peptide_df.loc[index]['intensity']
	peptide=peptide_df.loc[index]['peptide']
	peptide_modi=peptide_df.loc[index]['peptide_modi']
	charge=peptide_df.loc[index]['charge']
	
	#use 0.01 window (mz,rt,intensity) to find the same feature
	df_sample=df[(df['mz']>sample_mz-0.01)&(df['mz']<sample_mz+0.01)]
	df_sample=df_sample[(df_sample['time']>sample_rt-0.01)&(df_sample['time']<sample_rt+0.01)]
	df_sample=df_sample[(df_sample['intensity']>sample_intensity-0.01)&(df_sample['intensity']<sample_intensity+0.01)]
	df_sample=df_sample[df_sample['charge']==charge]
	
	if len(df_sample)>0:
		for df_sample_index in df_sample.index:
			group=df_sample.loc[df_sample_index]['group']
			if group in groups:
				continue
			groups.append(group)
			df_group=df[df['group']==group]
			if len(group)<2:
				continue
			if not (sample_1 in list(df_group['sample']) and sample_2 in list(df_group['sample'])):
				continue
			for group_index in df_group.index:
				sample=df_group.loc[group_index]['sample']
				if sample==sample_1:
					sample_1_mz=df_group.loc[group_index]['mz']
					sample_1_rt=df_group.loc[group_index]['time']
					sample_1_intensity=df_group.loc[group_index]['intensity']
					sample_1_score=df_group.loc[group_index]['intensity']
					adj_score=df_group.loc[group_index]['adj_score']
				if sample==sample_2:
					sample_2_mz=df_group.loc[group_index]['mz']
					sample_2_rt=df_group.loc[group_index]['time']
					sample_2_intensity=df_group.loc[group_index]['intensity']
			FC=math.log2(sample_1_intensity)-math.log2(sample_2_intensity)
			result['sample_1'].append(sample_1)
			result['sample_2'].append(sample_2)
			result['FC'].append(FC)
			result['peptide'].append(peptide)
			result['peptide_modi'].append(peptide_modi)
			result['charge'].append(charge)
			result['sample_1_mz'].append(sample_1_mz)
			result['sample_1_rt'].append(sample_1_rt)
			result['sample_1_intensity'].append(sample_1_intensity)
			result['sample_2_mz'].append(sample_2_mz)
			result['sample_2_rt'].append(sample_2_rt)
			result['sample_2_intensity'].append(sample_2_intensity)
			result['adj_score'].append(adj_score)
result_df=pd.DataFrame(result)
result_df.drop_duplicates(['sample_1_mz','sample_1_rt','sample_2_mz','sample_2_rt'],inplace=True)
result_df.to_csv(result_name,index=False)