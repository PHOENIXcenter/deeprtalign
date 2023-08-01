# -*- coding: utf-8 -*-
"""
Created on Fri May  5 09:20:08 2023

@author: leoicarus
"""
import pandas as pd
import math


folder='openms_result_ecoli_bg_ed'
file_1='E4801_230403_200ng_293T_15ng_Ecoli_05xiRT_60min_DDA_R3_ecoli.csv'
file_2='E4801_230402_200ng_293T_10ng_Ecoli_05xiRT_60min_DDA_R3_ecoli.csv'

align_file='openms_align_result/1_3.unknown'

result_name='15_10_R3_openms_align_FC.csv'

df1=pd.read_csv(folder+'/'+file_1)
df2=pd.read_csv(folder+'/'+file_2)

#oepnms results have some useless lines that need to be eliminated first
align_df=pd.read_csv(align_file,sep='\t',header=5,index_col=False)
align_df=align_df.iloc[3:]
align_df.reset_index(drop=True,inplace=True)
align_df=align_df[(align_df['intensity_0'].notna())&(align_df['intensity_1'].notna())]
align_df[['rt_0','mz_0','intensity_0','rt_1','mz_1','intensity_1']]=align_df[['rt_0','mz_0','intensity_0','rt_1','mz_1','intensity_1']].astype(float)
align_df[['charge_0','charge_1']]=align_df[['charge_0','charge_1']].astype(int)

result={'sample_1':[],'sample_2':[],'FC':[],'peptide':[],'peptide_modi':[],'charge':[],'sample_1_mz':[],'sample_1_rt':[],'sample_1_intensity':[],'sample_2_mz':[],'sample_2_rt':[],'sample_2_intensity':[]}
total_num=len(df1)
n=0
for sample_1_index in df1.index:
	n=n+1
	print(n,'file_1',total_num)
	peptide=df1.loc[sample_1_index]['peptide']
	peptide_modi=df1.loc[sample_1_index]['peptide_modi']
	charge=df1.loc[sample_1_index]['charge']
	sample_1_mz=df1.loc[sample_1_index]['mz']
	sample_1_rt=df1.loc[sample_1_index]['rt']
	sample_1_intensity=df1.loc[sample_1_index]['intensity']
	
	#use 0.01 window (mz,rt,intensity) to find the same feature
	align_df_sample_1=align_df[align_df['charge_0']==charge]
	align_df_sample_1=align_df_sample_1[(align_df_sample_1['mz_0']>sample_1_mz-0.01)&(align_df_sample_1['mz_0']<sample_1_mz+0.01)]
	align_df_sample_1=align_df_sample_1[(align_df_sample_1['rt_0']>sample_1_rt-0.01)&(align_df_sample_1['rt_0']<sample_1_rt+0.01)]
	align_df_sample_1=align_df_sample_1[(align_df_sample_1['intensity_0']>sample_1_intensity-0.01)&(align_df_sample_1['intensity_0']<sample_1_intensity+0.01)]
	
	if len(align_df_sample_1)>0:
		for align_df_index in align_df_sample_1.index:
			sample_1_mz=align_df_sample_1.loc[align_df_index]['mz_0']
			sample_1_rt=align_df_sample_1.loc[align_df_index]['rt_0']
			sample_1_intensity=align_df_sample_1.loc[align_df_index]['intensity_0']
			sample_2_mz=align_df_sample_1.loc[align_df_index]['mz_1']
			sample_2_rt=align_df_sample_1.loc[align_df_index]['rt_1']
			sample_2_intensity=align_df_sample_1.loc[align_df_index]['intensity_1']
			FC=math.log2(sample_1_intensity)-math.log2(sample_2_intensity)
			result['sample_1'].append(file_1)
			result['sample_2'].append(file_2)
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


total_num=len(df2)
n=0
for sample_2_index in df2.index:
	n=n+1
	print(n,'file_2',total_num)
	peptide=df2.loc[sample_2_index]['peptide']
	peptide_modi=df2.loc[sample_2_index]['peptide_modi']
	charge=df2.loc[sample_2_index]['charge']
	sample_2_mz=df2.loc[sample_2_index]['mz']
	sample_2_rt=df2.loc[sample_2_index]['rt']
	sample_2_intensity=df2.loc[sample_2_index]['intensity']
	
	align_df_sample_2=align_df[align_df['charge_1']==charge]
	align_df_sample_2=align_df_sample_2[(align_df_sample_2['mz_1']>sample_2_mz-0.01)&(align_df_sample_2['mz_1']<sample_2_mz+0.01)]
	align_df_sample_2=align_df_sample_2[(align_df_sample_2['rt_1']>sample_2_rt-0.01)&(align_df_sample_2['rt_1']<sample_2_rt+0.01)]
	align_df_sample_2=align_df_sample_2[(align_df_sample_2['intensity_1']>sample_2_intensity-0.01)&(align_df_sample_2['intensity_1']<sample_2_intensity+0.01)]
	
	if len(align_df_sample_2)>0:
		for align_df_index in align_df_sample_2.index:
			sample_1_mz=align_df_sample_2.loc[align_df_index]['mz_0']
			sample_1_rt=align_df_sample_2.loc[align_df_index]['rt_0']
			sample_1_intensity=align_df_sample_2.loc[align_df_index]['intensity_0']
			sample_2_mz=align_df_sample_2.loc[align_df_index]['mz_1']
			sample_2_rt=align_df_sample_2.loc[align_df_index]['rt_1']
			sample_2_intensity=align_df_sample_2.loc[align_df_index]['intensity_1']
			FC=math.log2(sample_1_intensity)-math.log2(sample_2_intensity)
			result['sample_1'].append(file_1)
			result['sample_2'].append(file_2)
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

result_df=pd.DataFrame(result)
result_df.drop_duplicates(['sample_1_mz','sample_1_rt','sample_2_mz','sample_2_rt'],inplace=True)
result_df.to_csv(result_name,index=False)