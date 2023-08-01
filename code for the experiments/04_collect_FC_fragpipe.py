# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 16:13:48 2023

@author: liuyi
"""
import pandas as pd
import math

sample_1='E4801_230402_200ng_293T_10ng_Ecoli_05xiRT_60min_DDA_R3 Intensity'
sample_2='E4801_230404_200ng_293T_25ng_Ecoli_05xiRT_60min_DDA_R3 Intensity'

result_name='25_10_R3_FC_fragpipe_MBR.csv'

result={'sample_1':[],'sample_2':[],'FC':[],'peptide_modi':[],'charge':[],'sample_1_intensity':[],'sample_2_intensity':[]}

file=r'K:\fragpipe_output_20230411\combined_modified_peptide.tsv'

df=pd.read_csv(file,sep='\t')

df=df[df['Entry Name'].str.contains('ECOLI')]
df=df[(df[sample_1]>0)&(df[sample_2]>0)]
for index in df.index:
	sample_1_intensity=df.loc[index][sample_1]
	sample_2_intensity=df.loc[index][sample_2]
	peptide=df.loc[index]['Modified Sequence']
	charges=df.loc[index]['Charges']
	if not charges.find(',')==-1:
		charges=charges.split(',')
		for charge in charges:
			result['sample_1'].append(sample_1)
			result['sample_2'].append(sample_2)
			result['FC'].append(math.log2(sample_2_intensity)-math.log2(sample_1_intensity))
			result['peptide_modi'].append(peptide)
			result['charge'].append(charge)
			result['sample_1_intensity'].append(sample_1_intensity)
			result['sample_2_intensity'].append(sample_2_intensity)
	else:
		result['sample_1'].append(sample_1)
		result['sample_2'].append(sample_2)
		result['FC'].append(math.log2(sample_2_intensity)-math.log2(sample_1_intensity))
		result['peptide_modi'].append(peptide)
		result['charge'].append(charges)
		result['sample_1_intensity'].append(sample_1_intensity)
		result['sample_2_intensity'].append(sample_2_intensity)
result_df=pd.DataFrame(result)
result_df.to_csv(result_name,index=False)