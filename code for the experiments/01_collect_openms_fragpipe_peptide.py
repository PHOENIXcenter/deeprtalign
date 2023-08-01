# -*- coding: utf-8 -*-
"""
Created on Fri May  5 10:33:26 2023

@author: liuyi
"""

import pandas as pd
import os

precision=10

#features collected by openms's FeatureFinderCentroided, and use
openms_folder='openms_result'

#MSFragger result (psm.tsv)
peptide_folder='fragpipe_output_without_MBR_20230411'

result_folder='openms_result_ecoli_bg_ed'

if not os.path.exists(result_folder):
	os.mkdir(result_folder)

n=0
total_number=len(os.listdir(openms_folder))

for file in os.listdir(openms_folder):
	n=n+1
	print(n,file,total_number)
	#oepnms results have some useless lines that need to be eliminated first
	openms_df=pd.read_csv(openms_folder+'/'+file,sep='\t',header=3,index_col=False)
	openms_df=openms_df.iloc[1:]
	openms_df.reset_index(drop=True,inplace=True)
	openms_df[['rt','mz','intensity','rt_start','rt_end']]=openms_df[['rt','mz','intensity','rt_start','rt_end']].astype(float)
	openms_df[['charge']]=openms_df[['charge']].astype(int)
	
	peptide_df=pd.read_csv(peptide_folder+'/'+file.split('.unknown')[0]+'/psm.tsv',sep='\t',converters={'Is Unique':str})
	peptide_df=peptide_df[peptide_df['Protein'].str.contains('ECOLI')]
	
	result_df=pd.DataFrame()
	for peptide_index in peptide_df.index:
		peptide_charge=peptide_df.loc[peptide_index]['Charge']
		peptide_mz=peptide_df.loc[peptide_index]['Observed M/Z']
		peptide_rt=peptide_df.loc[peptide_index]['Retention']
		peptide_peptide=peptide_df.loc[peptide_index]['Peptide']
		peptide_modi=peptide_df.loc[peptide_index]['Modified Peptide']
		peptide_protein=peptide_df.loc[peptide_index]['Protein']
		
		#matched features and peptide (10ppm, rt_start<peptide_rt<rt_end) 
		up_mz=peptide_mz+(precision/1000000*peptide_mz)
		down_mz=peptide_mz-(precision/1000000*peptide_mz)
		
		openms_peptide_df=openms_df[(openms_df['rt_start']<peptide_rt)&(openms_df['rt_end']>peptide_rt)]
		openms_peptide_df=openms_peptide_df[(openms_peptide_df['mz']<up_mz)&(openms_peptide_df['mz']>down_mz)]
		openms_peptide_df=openms_peptide_df[openms_peptide_df['charge']==peptide_charge]
		if len(openms_peptide_df)>0:
			best_time_diff=10000
			for openms_index in openms_peptide_df.index:
				openms_rt=openms_peptide_df.loc[openms_index]['rt']
				if abs(openms_rt-peptide_rt)<best_time_diff:
					best_time_diff=abs(openms_rt-peptide_rt)
					best_index=openms_index
			openms_peptide_df.loc[best_index,'rt_diff']=best_time_diff
			openms_peptide_df.loc[best_index,'peptide']=peptide_peptide
			openms_peptide_df.loc[best_index,'peptide_modi']=peptide_modi
			openms_peptide_df.loc[best_index,'protein']=peptide_protein
			if len(result_df)==0:
				result_df=openms_peptide_df.loc[[best_index]]
			else:
				result_df=pd.concat([result_df,openms_peptide_df.loc[[best_index]]],ignore_index=True)
		else:
			continue
	if len(result_df)==0:
		continue

	#If a feature corresponds to multiple peptides, only keep the peptide with closest RT	
	result_df.sort_values(by='rt_diff',ascending=True,inplace=True,ignore_index=True)
	result_df.drop_duplicates(['mz','rt','intensity'],keep='first',inplace=True,ignore_index=True)
	result_df.to_csv(result_folder+'/'+file.split('.unknown')[0]+'_ecoli.csv',index=False)