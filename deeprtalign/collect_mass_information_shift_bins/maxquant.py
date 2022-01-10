# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 16:28:49 2021

@author: leoicarus
"""
import pandas as pd
import os
import shutil

def collect_bins(bin_width,bin_precision):
	file_dir='shift_result'
	
	result_dir='shift_result_bins'
	
	bin_df=pd.DataFrame()

	if not os.path.exists(result_dir):
		os.mkdir(result_dir)
	
	for fraction in os.listdir(file_dir):
		for file in os.listdir(file_dir+'/'+fraction):
			print('step_3:',file,fraction)
			file_path=file_dir+'/'+fraction+'/'+file
			sample=file.split('.csv')[0]
			if len(bin_df)==0:
				df=pd.read_csv(file_path)
				df.sort_values(by='Tmass',ascending=True,inplace=True)
				bin_begin=df.iloc[0]['Tmass']
				bin_end=df.iloc[-1]['Tmass']
				bin_1=bin_begin-bin_width
				bin_2=bin_begin+bin_width
				bin_id=0
				bin_list={'bin_id':[],'bin_1':[],'bin_2':[]}
				while bin_2<bin_end:
					bin_list['bin_id'].append(bin_id)
					bin_list['bin_1'].append(str(round(bin_1,bin_precision)))
					bin_list['bin_2'].append(str(round(bin_2,bin_precision)))
					bin_1=bin_1+bin_width/2
					bin_2=bin_1+bin_width
					bin_id=bin_id+1
				if bin_1<bin_end:
					bin_2=bin_end+bin_width
					bin_list['bin_id'].append(bin_id)
					bin_list['bin_1'].append(str(round(bin_1,bin_precision)))
					bin_list['bin_2'].append(str(round(bin_2,bin_precision)))
				bin_df=pd.DataFrame(bin_list)
				bin_1_f=[float(a)for a in bin_df['bin_1']]
				bin_2_f=[float(a)for a in bin_df['bin_2']]
				bin_df['bin_1_f']=bin_1_f
				bin_df['bin_2_f']=bin_2_f
				bin_number=len(bin_df)
				batch_size=int(bin_number/20)
			batch_number=0
			bin_index_begin=0
			while bin_index_begin+batch_size<bin_number:
				bin_df.loc[bin_index_begin:bin_index_begin+batch_size,'batch_number']=int(batch_number)
				bin_index_begin=bin_index_begin+batch_size+1
				batch_number=batch_number+1
			bin_df.loc[bin_index_begin:bin_number,'batch_number']=int(batch_number)
			file=open(file_path,'r')
			oneline=file.readline()
			title_line='sample,fraction,'+oneline
			while oneline:
				oneline=file.readline()
				if not oneline:
					break
				mass=oneline.split(',')[10].strip()
				bin_mass=bin_df[(bin_df['bin_1_f']<=float(mass))&(bin_df['bin_2_f']>float(mass))]
				if len(bin_mass)==0:
					continue
				for index in bin_mass.index:
					bin_1=bin_mass.loc[index]['bin_1']
					bin_2=bin_mass.loc[index]['bin_2']
					batch_number=bin_mass.loc[index]['batch_number']
					if not os.path.exists(result_dir+'/'+str(batch_number)):
						os.mkdir(result_dir+'/'+str(batch_number))
					if not os.path.exists(result_dir+'/'+str(batch_number)+'/'+bin_1+'_'+bin_2+'.csv'):
						result_file=open(result_dir+'/'+str(batch_number)+'/'+bin_1+'_'+bin_2+'.csv','a')
						result_file.write(title_line)
						result_file.close()
					result_file=open(result_dir+'/'+str(batch_number)+'/'+bin_1+'_'+bin_2+'.csv','a')
					result_file.write(sample+','+fraction+','+oneline)
					result_file.close()
	for son_path in os.listdir(result_dir):
		dir_path=os.path.join(result_dir,son_path)
		if os.path.isdir(dir_path):
			print(dir_path)
			for file in os.listdir(dir_path):
				file = os.path.join(dir_path, file)
				shutil.move(file, result_dir)
			os.rmdir(dir_path)

