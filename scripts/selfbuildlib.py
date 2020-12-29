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
    
    return df_data

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
Clean dataset before using. The cleaning process includes the following steps:
    1. Remove unused columns
    2. Remove rows with nan.
    3. Calculate the patient ability level
    4. Group the patient by their age range
    5. Extract unsuccessful cases
    6. Convert acc data type
    7. Extract recall
    8. Make sure all inputs are in small letter
Arguments:
    - df: dataframe stored the data
    - col_name: the name of the columns intended to be removed
    - ageThres: the threshold used to group the patients to either junior or senior
Return:
    - df: returned data
'''
# df = df_data
# col_name = ["remark"]
# ageThres = 70
def clean_data(df, col_name, ageThres):
    # 1. Remove unused columns
    df.drop(col_name, axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    ## (for database)
    ## Remove the last column in the dataset (untended added by the radiographer for 30-Nov-2-Jan.xlsx)
    df.drop(df.columns[-1], axis=1, inplace=True)
    
    # 2. Remove rows with nan.
    df = df[df["acc."].notna()]

    
    # 3. Calculate the patient ability level
    df = cal_level_of_coorperation(df)   
    # Classify patient ability level to High(11-15), Moderate(6-10) or Low(1-5)
    # add a new column in the dataframe
    new_feature = ['']*df.shape[0]
    df['class_level'] = new_feature
    # classify patient ability level to one of the group
    df = classify_patient_level(df)
    
    # 4. ## Classify age to Junior and Senior
    df['class_age'] = new_feature
    # classify patient to either junior or senior based on the threshold
    df = classify_patient_age(df, ageThres)
    
    # 8. Make sure all inputs are in small letter
    df = all_small(df, 'gender')
    df = all_small(df, 'patient_type')
    df = all_small(df, 'order')
    df = all_small(df, 'contrast')
    df = all_small(df, 'operator')
    df = all_small(df, 'implants')
    df = all_small(df, 'successful')
    df = all_small(df, 'sedation')
    

    
    # 6. Convert acc data type
    df = convert_acc_to_list(df)
    
    # remove rows (ONLY for database data)
    label = [111, 126, 128, 171, 221]
    df.drop(index=label, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # 5. extrect the unsuccessful cases
    df_un = df[df.successful == 'n']
    df.drop(index = df_un.index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df_un.reset_index(drop=True, inplace=True)
    
    # 7. Extract recall (repeated acc number)
    all_acc = []
    for val in df["acc."]:
        print(val)
        for i in range(len(val)):
            all_acc.append(val[i])
    # extract the repeated acc number
    # duplicates = [item for item, count in collections.Counter(all_acc).items() if count > 1]
    # # extract the duplicated rows
    # df_duplicated = df[df["acc."] in duplicates]
    

            
    return df, df_un, all_acc
'''
Calculate the number of orders by extracting the number of / in the account column
Arguments:
    - df: dataframe stored the data
Return:
    - df: the number of order
''' 
def calculate_num_orders(df):
    additional = 0
    for val in df["acc."]:
        if type(val) == str:
            if len(val) in [17, 26, 35, 44, 53]:
                additional += len(val)%8
    return additional + df.shape[0]
  
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
def all_small(df, col):
    
    df[col] = df[col].str.lower()
    
    return df
    
    
    


    
    