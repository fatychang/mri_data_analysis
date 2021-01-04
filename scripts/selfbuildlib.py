# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 15:03:57 2020

@author: Chang
"""



import pandas as pd
import collections
import numpy as np


'''
Convert the acc to list data type
'''
def convert_acc_to_list(df):
    df.reset_index(drop=True, inplace=True)
    
    for idx, val in enumerate(df["acc."]):
        lst_acc = []
        if len(str(val)) == 8:
            lst_acc.append(str(val))
            df["acc."].loc[idx] = lst_acc
        elif len(str(val)) > 8 and len(str(val)) < 17:
            lst_acc.append(str(val)[0:8])
            df["acc."].loc[idx] = lst_acc
        elif len(str(val)) == 17:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            df["acc."].loc[idx] = lst_acc
        elif len(str(val)) == 26:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            lst_acc.append(val[18:26])
            df["acc."].loc[idx] = lst_acc
        elif len(str(val)) == 35:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            lst_acc.append(val[18:26])
            lst_acc.append(val[27:35])
            df["acc."].loc[idx] = lst_acc
        elif len(str(val)) == 44:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            lst_acc.append(val[18:26])
            lst_acc.append(val[27:35])
            lst_acc.append(val[36:44])
            df["acc."].loc[idx] = lst_acc
        else:
            print("[ERR] Something wrong at idex: {}".format(idx))
    return df
 


'''
Convert the physical and psychological ability level to numberic value
and calculate the ability level by multiplying these two features.
Return and overwrite the data in the dataset.
'''
def cal_level_of_coorperation(df):    
    for i in range(0, df.shape[0]):
        # phycial ability (1-5)
        if df.physical_ability.iloc[i] == 'spinal nursing':
            df.physical_ability.iloc[i] = 1;
        if df.physical_ability.iloc[i] == 'more assistance.(trolley, bed transfer)':
            df.physical_ability.iloc[i] = 2;
        if df.physical_ability.iloc[i] == 'some assistance. (2 man assist)':
            df.physical_ability.iloc[i] = 3;
        if df.physical_ability.iloc[i] == 'some assistance. (1 man assist)':
            df.physical_ability.iloc[i] = 4;
        if df.physical_ability.iloc[i] == 'ambulant. min assistance':
            df.physical_ability.iloc[i] = 5;
            
        # Psychological Ability Level (1-3)
        if df.psychological_ability.iloc[i] == 'uncooperative, uncommunicative':
            df.psychological_ability.iloc[i] = 1;
        if df.psychological_ability.iloc[i] == 'uncooperative, communicative':
            df.psychological_ability.iloc[i] = 2;
        if df.psychological_ability.iloc[i] == 'cooperative':
            df.psychological_ability.iloc[i] = 3;
        
        # Level of coorperation (phy * Psy)
        df.level_cooperation.iloc[i] = df.physical_ability.iloc[i]* df.psychological_ability.iloc[i]        
    return df

'''
Classify the patient ability level to High, Moderate or Low based on the abaility level score
'''
def classify_patient_level(df):
    for i in range(0, df.shape[0]):
        if(df.level_cooperation.iloc[i] > 10):
            df.class_level.iloc[i] = 'high'
        elif(df.level_cooperation.iloc[i] < 6):
            df.class_level.iloc[i] = 'low'      
        else:
            df.class_level.iloc[i] = 'moderate'
    return df

'''
Classify the patient to eight junior or senior based on their age
'''
def classify_patient_age(df, thres):
    for i in range(0, df.shape[0]):
        if(df.age.iloc[i] >= thres):
            df.class_age.iloc[i] = 'senior'
        else:
            df.class_age.iloc[i] = 'junior'
    return df

'''
Read the excel file and return as a dataframe.
The date will be added as an additional feature in the database.
Arguments:
    - loc: file location (relative) and file name
Return:
    - df: data in the pandas dataframe
'''
def read_data(loc):
    xls = pd.ExcelFile(loc)
    dict_data = pd.read_excel(xls, sheet_name=None, ignore_index=True)
    
    ## Add in date to the dataset
    for key, value in dict_data.items():
        date = [key] * value.shape[0]
        value['date'] = date
    
    ## Extract the 'option' and the 'rule' sheet in the dictionary
    dict_rule = {key: dict_data[key] for key in dict_data.keys() & {'option', 'rule'}}
    del dict_data['option']
    del dict_data['rule']
    
    ## Create the dataframe for the remaining data
    df_data = pd.concat(dict_data, ignore_index=True)
    
    return df_data, dict_data

'''
Find the duplicated account number and extract them to a new dataframe
Arguments:
    - df: dataframe
    - ls_acc: a list stores all account number
Returns: 
    - df: dataframe (remove the duplicated cases)
    - df_duplicated: dataframe stores those duplicated cases
'''
def find_duplicates(df, ls_acc):
    # find the duplicated account which shows more than once in the list
    duplicates = [item for item, count in collections.Counter(ls_acc).items() if count > 1]
    
    # extract the duplicated rows
    ls_idx = [False]*df.shape[0]
    for val in duplicates:
        for i in range (df.shape[0]):
            if val in df["acc."][i]:
                ls_idx[i] = True
    df_dup = df[ls_idx]
    df_data = df[~np.array(ls_idx)]
    
    #reset the index
    df_dup.reset_index(drop=True, inplace=True)
    df_data.reset_index(drop=True, inplace=True)
    
    return df, df_dup

'''
Remove unused columns
'''
def remove_unused_cols(df, col_name):
    df.drop(col_name, axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df

'''
Calculate the number of orders by extracting the number of / in the account column
''' 
def calculate_num_orders(df):
    num = 0
    for val in df["acc."]:

        num += len(val)
    return num
  
'''
datetime - datetime and return minute interval
'''  
def minute_interval(start, end):
     reverse = False
     if start > end:
          start, end = end, start
          reverse = True

     delta = (end.hour - start.hour)*60 + end.minute - start.minute + (end.second - start.second)/60.0
     if reverse:
          delta = 24*60 - delta
     return delta
    
'''
Make sure all the input are small letter
Arguement:
    - df: dataset in dataframe
    - col: the column name which need to be converted (checked)
Return:
    - df: modified dataset    
'''
def all_small(df, cols):
    for col in cols:
        df[col] = df[col].str.lower()
    return df
    
'''
Calculate the duration
Argument:
    - df: dataframe
    - start_col: column name of the starting time
    - end_col: column name of the end time
    - new_col: new column name to store the duration
'''  
def calculate_duration(df, end_col, start_col, new_col):
    for i in range (df.shape[0]):              
        start = df[start_col][i]
        end = df[end_col][i]
        df[new_col][i] = minute_interval(start, end)
    return df
    
        # start = df_data["transfer strat_time"][index]
        # end = df_data["transfer end_time"][index]
        # df_data['in_room_minute'][index] = lib.minute_interval(start, end)

    
    