# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 15:03:57 2020

@author: Chang
"""



import pandas as pd
import collections
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


'''
Convert the acc to list data type
'''
def convert_acc_to_list(df):
    df.reset_index(drop=True, inplace=True)
    
    for idx, val in enumerate(df["acc"]):
        lst_acc = []
        if len(str(val)) == 8:
            lst_acc.append(str(val))
            df["acc"].loc[idx] = lst_acc
        elif len(str(val)) > 8 and len(str(val)) < 17:
            lst_acc.append(str(val)[0:8])
            df["acc"].loc[idx] = lst_acc
        elif len(str(val)) == 17:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            df["acc"].loc[idx] = lst_acc
        elif len(str(val)) == 26:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            lst_acc.append(val[18:26])
            df["acc"].loc[idx] = lst_acc
        elif len(str(val)) == 35:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            lst_acc.append(val[18:26])
            lst_acc.append(val[27:35])
            df["acc"].loc[idx] = lst_acc
        elif len(str(val)) == 44:
            lst_acc.append(val[0:8])
            lst_acc.append(val[9:17])
            lst_acc.append(val[18:26])
            lst_acc.append(val[27:35])
            lst_acc.append(val[36:44])
            df["acc"].loc[idx] = lst_acc
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
            df.psychological_ability.iloc[i] = 3;
        if df.psychological_ability.iloc[i] == 'cooperative':
            df.psychological_ability.iloc[i] = 5;
        
        # Level of coorperation (phy * Psy)
        df.level_cooperation.iloc[i] = df.physical_ability.iloc[i]* df.psychological_ability.iloc[i]        
    return df

'''
Classify the patient ability level to High, Moderate or Low based on the abaility level score
'''
def classify_patient_level(df, col_name):
    for i in range(0, df.shape[0]):
        if(df.level_cooperation.iloc[i] > 15):
            df[col_name].iloc[i] = 'high'
        elif(df.level_cooperation.iloc[i] < 10):
            df[col_name].iloc[i] = 'low'      
        else:
            df[col_name].iloc[i] = 'moderate'
    return df

'''
Classify the patient to eight junior or senior based on their age
'''
def classify_patient_age(df, thres, col_name):
    for i in range(0, df.shape[0]):
        if(df.age.iloc[i] >= thres):
            df[col_name].iloc[i] = 'senior'
        else:
            df[col_name].iloc[i] = 'junior'
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
    del dict_data['options']
    # del dict_data['rule']
    
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
        first_found = 0
        for i in range (df.shape[0]):
            if val in df["acc"][i]:
                if first_found == 1:
                    ls_idx[i] = True
                else:
                    first_found =1
    df_dup = df[ls_idx]
    df_data = df[~np.array(ls_idx)]
    
    #reset the index
    # df_dup.reset_index(drop=True, inplace=True)
    # df_data.reset_index(drop=True, inplace=True)
    
    return df, df_dup, duplicates

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
    for i in range(df.shape[0]):
        if df["num_orders"].iloc[i] == "single":
            num +=1
        elif df["num_orders"].iloc[i] == "two":
            num +=2
        elif df["num_orders"].iloc[i] == "three":
            num+=3
        else:
            print("there are others in the number of orders... please check")
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
    
'''
Add the day into the dataset
'''
def add_day_to_dataset(df):
    df['day'] = ['']*df.shape[0]
    date = df.date.unique()
    day = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']
    day_count = 0
    
    for i in range(df.shape[0]):
        if(df.date[i] == date[day_count]):
            df.day[i] = day[day_count]
        else:
            day_count +=1
            if day_count == len(day):
                break
            df.day[i] = day[day_count]
    
    return df

'''
Covert the number of orders to the numeric representation
'''
def convert_num_orders_to_numbers(df):
    df["num_orders_numeric"] = ['']*df.shape[0]    
    
    for i in range(df.shape[0]):
        if df["num_orders"].iloc[i] == "single":
            df["num_orders_numeric"].iloc[i] = 1
        elif df["num_orders"].iloc[i] == "two":
            df["num_orders_numeric"].iloc[i] = 2
        elif df["num_orders"].iloc[i] == "three":
            df["num_orders_numeric"].iloc[i] = 3
        else:
            print("there are others in the number of orders... please check")
    return df

'''
Calculate the idle time between two scans (same day)
'''    
def calculate_idle_time(df, col_name):
    df[col_name] = ['']*df.shape[0]    
    for i in range(df.shape[0]):
        if i == df.shape[0]-1:
            df.idle_time[i] = 0
            break
        if df.day[i] == df.day[i+1]: #same day
            start = df["transfer_end_time"][i]
            end = df["transfer_strat_time"][i+1]
            df[col_name][i] = minute_interval(start, end)
        else:
            df[col_name][i] = 0
    
    return df


################################################################################################################
################################################################################################################
#### For Database 

'''
Calculate the avg/ std of the number of orders on the day (Mon, Tue...)
@ retun avg and std
'''
def calculate_avg_std_order_by_days(df):
    uni = df.date.unique()
    tmp = np.zeros(uni.shape[0])
    ctr = 0
    for i in range (uni.shape[0]):
        tmp[ctr] = df[df.date == uni[i]].num_orders_numeric.sum()
        ctr +=1
    avg = tmp.mean()
    std = tmp.std()
    return avg, std

'''
Calculate the avg/ std of the idle time on the day (Mon, Tue...)
@ retun avg and std
'''
def calculate_avg_std_idle_time_by_days(df):
    uni = df.date.unique()
    tmp = np.zeros(uni.shape[0])
    ctr = 0
    for i in range (uni.shape[0]):
        tmp[ctr] = df[df.date == uni[i]].idle_time.sum()
        ctr +=1
    avg = tmp.mean()
    std = tmp.std()
    return avg, std

'''
Generate the average scan time for each scan type of a certain type of patient (in/out/icu/ucc patient).
The results are separated to four conditions (contrast? and age group) as below:
    - Condition1: (no contrast + Junior)
    - Condition2: (no contrast + Senior)
    - Condition3: (contrast + Junior)
    - Condition4: (contrast + Senior)
Note: Will only extract the single-scan order as the contrast is n or y
Arguement:
    - df_input: the extracted dataframe for the required patient type
    - all_type_scans: a series containing all the possible scan name
Return include the following:
    - df_result: a dataframe stores the result(avg, std, n) of four conditions with the scan type as index
    - (Not included at this moment, can be done in the future) dict_scan: a dictionary stores all the scan time of a particular scan type as the key
'''
def generate_result_four_conditions(df_input, all_type_scans, non_contrast):
    ## 4 condictions (contrast, age)
    # Condition1: (no contrast + Junior)
    df_c1 = df_input.loc[(df_input.contrast == 'n') & (df_input.age_class == 'junior')].reset_index(drop=True)
    dict_c1_scan, dict_c1_result = cal_time_based_on_order(df_c1, df_c1.order)
    # Condition2: (no contrast + Senior)
    df_c2 = df_input.loc[(df_input.contrast == 'n') & (df_input.age_class == 'senior')].reset_index(drop=True)
    dict_c2_scan, dict_c2_result = cal_time_based_on_order(df_c2, df_c2.order)
    # Condition3: (contrast + Junior)
    df_c3 = df_input.loc[(df_input.contrast == 'y') & (df_input.age_class == 'junior')].reset_index(drop=True)
    dict_c3_scan, dict_c3_result = cal_time_based_on_order(df_c3, df_c3.order)
    # Condition4: (contrast + Senior)
    df_c4 = df_input.loc[(df_input.contrast == 'y') & (df_input.age_class == 'senior')].reset_index(drop=True)
    dict_c4_scan, dict_c4_result = cal_time_based_on_order(df_c4, df_c4.order)
    
    ## create a new dataframe to store the result (output)
    column_name = ['scan_type', 'c1_mean', 'c1_std', 'c1_n', 'c2_mean', 'c2_std', 'c2_n', 'c3_mean', 'c3_std', 'c3_n', 'c4_mean', 'c4_std', 'c4_n']
    df_out = pd.DataFrame(columns=column_name)
    # add in the all the scans in the dataframe
    df_out = df_out.assign(scan_type = all_type_scans.index)    
    # set the scan_type as index
    df_out.set_index('scan_type', inplace=True)
   
    # df_out = pd.DataFrame()
    ## merge all the resulted dictionaries to one dataframe
    for key, value in dict_c1_result.items():
        df_out.loc[key, 0:3] = value
    for key, value in dict_c2_result.items():
        df_out.loc[key, 3:6] = value    
    for key, value in dict_c3_result.items():
        df_out.loc[key, 6:9] = value
    for key, value in dict_c4_result.items():
        df_out.loc[key, 9:12] = value       

    ## return
    # return df_out, dict_c1_result, dict_c2_result, dict_c3_result, dict_c4_result
    return df_out
    
'''
Create dictionaries to store the each scan time sorted by the type of scan (order)
NOTED: need to fix the scan time and transfer time thing (no transfer time here)
'''
def cal_time_based_on_order(df_dataInput, scans):
    dict_sortedData_scan = {key:[] for key in scans}
    dict_sortedData_transfer = {key:[] for key in scans}
    dict_result = {key:[] for key in scans}

    # create a dict to stores the scan time by the order (scan)
    for i in range (df_dataInput.shape[0]):
        key = df_dataInput.order[i]
        dict_sortedData_scan[key].append(df_dataInput.minutes[i])

    # # create a dict to stores the transfer time by the order (scan)
    # (HAVEN'T FINISH!!)
    # for i in range (df_dataInput.shape[0]):
    #     key = df_dataInput.order[i]
    #     dict_sortedData_transfer[key].append(df_dataInput.minutes[i])

        
    # calculate the mean, std and the number of data (in sequence) of the scan time of each order
    for key, value in dict_sortedData_scan.items():
        np_scanTime = np.array(dict_sortedData_scan[key])
        dict_result[key].append(np_scanTime.mean())
        dict_result[key].append(np_scanTime.std())
        dict_result[key].append(len(np_scanTime))
    # # calculate the mean, std and the number of data (in sequence) of the transfer time of each order      
    # for key, value in dict_sortedData_transfer.items():       
    #     np_transferTime = np.array(dict_sortedData_transfer[key])
    #     dict_result[key].append(np_transferTime.mean())
    #     dict_result[key].append(np_transferTime.std())
    #     dict_result[key].append(len(np_transferTime))       
    
    return dict_sortedData_scan, dict_result


'''
Generate the average scan time for each scan type 
Arguement:
    - df_input: the extracted dataframe for the required patient type
    - all_type_scans: a series containing all the possible scan name
Return include the following:
    - df_result: a dataframe stores the result(avg, std, n) of four conditions with the scan type as index
    - (Not included at this moment, can be done in the future) dict_scan: a dictionary stores all the scan time of a particular scan type as the key
'''
def generate_result(df_input, all_type_scans):
    
    dict_scan, dict_result = cal_time_based_on_order(df_input, df_input.order)
    
    ## create a new dataframe to store the result (output)
    column_name = ['scan_type', 'mean', 'std', 'n']
    df_out = pd.DataFrame(columns=column_name)
    # add in the all the scans in the dataframe
    df_out = df_out.assign(scan_type = all_type_scans.index)    
    # set the scan_type as index
    df_out.set_index('scan_type', inplace=True)

    # add data to dataframe
    for key, value in dict_result.items():
        df_out.loc[key, 0:3] = value
    
    return df_out


'''
Calculate the correlation between the level of coorperation and the transfer time
Arguement:
    - patient_type: ip, op, ucc or icu
    - score_type: physical_ability, psychological_ability or level_cooperation
'''
def score_y_coorelation(patient_type, score_type, y, df_input, write_directory, txt=""):
    #extract the corresponding sub-set
    df_input = df_input[df_input.patient_type == patient_type].reset_index(drop=True)
    N = df_input[df_input.patient_type == patient_type].shape[0]
    if N == 0:
        return
    plt.figure()
    sns.stripplot(data=df_input, x=score_type, y=y, jitter=0.15, size=10) 
    if y == "minutes":
        y = "scan_time"
    plt.title("{} score vs. {}: {} {} ({})".format(score_type, y, patient_type, txt, N))
    plt.xlabel("{}".format(score_type))
    plt.ylabel("Time (min.)")   
    
    plt.savefig(write_directory + 'Coorelation {} vs {} - {} patients {} {}).png'.format(score_type, y, patient_type, N, txt))
    
    return 0
    
