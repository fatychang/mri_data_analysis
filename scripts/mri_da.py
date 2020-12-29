# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 15:51:14 2020
This script aims to analyze the mri scan time in different conditions
It is meant for analyzing all data from database.

This second version is modified after Lin Chen's discussion with her colleagues

@author: Chang
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#################
### functions ###
#################
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
Generate the average scan time for each scan type of a certain type of patient (in/out/icu/ucc patient).
The results are separated to four conditions (contrast? and age group) as below:
    - Condition1: (no contrast + Junior)
    - Condition2: (no contrast + Senior)
    - Condition3: (contrast + Junior)
    - Condition4: (contrast + Senior)
Arguement:
    - df_input: the extracted dataframe for the required patient type
    - all_type_scans: a series containing all the possible scan name
Return include the following:
    - df_result: a dataframe stores the result(avg, std, n) of four conditions with the scan type as index
    - (Not included at this moment, can be done in the future) dict_scan: a dictionary stores all the scan time of a particular scan type as the key
'''
def generate_result_four_conditions(df_input, all_type_scans):
    ## 4 condictions (contrast, age)
    # Condition1: (no contrast + Junior)
    df_c1 = df_input.loc[(df_input.contrast == 'N') & (df_input.class_age == 'junior')].reset_index(drop=True)
    dict_c1_scan, dict_c1_result = cal_time_based_on_order(df_c1, df_c1.order)
    # Condition2: (no contrast + Senior)
    df_c2 = df_input.loc[(df_input.contrast == 'N') & (df_input.class_age == 'senior')].reset_index(drop=True)
    dict_c2_scan, dict_c2_result = cal_time_based_on_order(df_c2, df_c2.order)
    # Condition3: (contrast + Junior)
    df_c3 = df_input.loc[(df_input.contrast == 'Y') & (df_input.class_age == 'junior')].reset_index(drop=True)
    dict_c3_scan, dict_c3_result = cal_time_based_on_order(df_c3, df_c3.order)
    # Condition4: (contrast + Senior)
    df_c4 = df_input.loc[(df_input.contrast == 'Y') & (df_input.class_age == 'senior')].reset_index(drop=True)
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
           
###########################
### read the excel file ###
########################### 
xls = pd.ExcelFile("../data/30-Nov-2-Jan.xlsx")
# xls = pd.ExcelFile("../data/fake.xlsx")
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


#####################
### overview data ###
#####################
# df_data.info()
# df_data.describe()


###########################
### feature engineering ###
###########################
## Remove unused columns in the dataset
undiscussed = ['remark']
df_data.drop(undiscussed, axis=1, inplace=True)
df_data.reset_index(drop=True)

## Remove the last column in the dataset (untended added by the radiographer for 30-Nov-2-Jan.xlsx)
df_data.drop(df_data.columns[-1], axis=1, inplace=True)

## Change the 'account' column name from acc. to acc
df_data.rename(columns={'acc.':'acc'}, inplace=True)

## Calculate the patient ability level
df_data = cal_level_of_coorperation(df_data)

## Remove nan. on 'account' column
df_data = df_data[df_data.acc.notna()]
# check how many non left in each column
df_data.isnull().sum()

## Classify patient ability level to High(11-15), Moderate(6-10) or Low(1-5)
# add a new column in the dataframe
new_feature = ['']*df_data.shape[0]
df_data['class_level'] = new_feature
# classify patient ability level to one of the three groups
df_data = classify_patient_level(df_data)
# print the number of patients in each group [DEBUG]
print("[INFO] The total number of patients in each group: ")
df_data.class_level.value_counts()

## Classify age to Junior and Senior
ageThres = 70
df_data['class_age'] = new_feature
# classify patient to either junior or senior based on the threshold
df_data = classify_patient_age(df_data, ageThres)
# print the number of patients in each group [DEBUG]
print("[INFO] The total number of patients in each group: ")
df_data.class_age.value_counts()


## Remove rows with any nan. value
df_data.dropna(axis=0, how='any', inplace=True)
df_data.reset_index(drop=True, inplace=True)
numDatapoints = df_data.shape[0]
numFeatures = df_data.shape[1]
print("[INFO] The total number of valid datapoints is {} with {} features recorded.".format(numDatapoints, numFeatures))


########################
### basic informaion ###
########################
## The number of patients in this dataset
numPatients = df_data.shape[0]
df_malePatient = df_data[df_data.gender == 'M']
df_femalePatient = df_data[df_data.gender == 'F']
numInpatients = df_data[df_data.patient_type == 'ip'].shape[0]
numOutpatients = df_data[df_data.patient_type == 'op'].shape[0]
numICUpatients = df_data[df_data.patient_type == 'icu'].shape[0]
numNormalPatients = df_data[df_data.contrast == 'N'].shape[0]
numContrastPatients = df_data[df_data.contrast == 'Y'].shape[0]
print("")
print("[INFO] The number of patients: {0}".format(numPatients))
print("[INFO] The number of male patients: {0}/{1}".format(df_malePatient.shape[0], numPatients))
print("[INFO] The number of female patients: {0}/{1}".format(df_femalePatient.shape[0], numPatients))
print("[INFO] The number of  inpatients : {0}/{1}".format(numInpatients, numPatients))
print("[INFO] The number of  outpatients : {0}/{1}".format(numOutpatients, numPatients))
print("[INFO] The number of  icu : {0}/{1}".format(numICUpatients, numPatients))
print("[INFO] The number of  patient without contrast : {0}/{1}".format(numNormalPatients, numPatients))
print("[INFO] The number of  patient with contrast : {0}/{1}".format(numContrastPatients, numPatients))

## age
avgAge = df_data['age'].mean()
avgAgeMale = df_data.age[df_data.gender == 'M'].mean()
avgAgeFemale = df_data.age[df_data.gender == 'F'].mean()
avgAvgInpatient = df_data.age[df_data.patient_type == 'ip'].mean()
avgAvgOutpatient = df_data.age[df_data.patient_type == 'op'].mean()
avgAvgICUpatient = df_data.age[df_data.patient_type == 'icu'].mean()
stdAge = df_data['age'].std()
stdAgeMale = df_data.age[df_data.gender == 'M'].std()
stdAgeFemale = df_data.age[df_data.gender == 'F'].std()
stdAgeInpatient = df_data.age[df_data.patient_type == 'ip'].std()
stdAgeOutpatient = df_data.age[df_data.patient_type == 'op'].std()
stdAgeICUpatient = df_data.age[df_data.patient_type == 'icu'].std()
print("\n\n")
print("\n\n===The age of patients===")
print("[INFO] The average age of all the patients: {0:.2f}+/-{1:.2f}".format(avgAge, stdAge))
print("[INFO] The average age of all the male patients: {0:.2f}+/-{1:.2f}".format(avgAgeMale, stdAgeMale))
print("[INFO] The average age of all the female patients: {0:.2f}+/-{1:.2f}".format(avgAgeFemale, stdAgeFemale))
print("[INFO] The average age of all the inpatients: {0:.2f}+/-{1:.2f}".format(avgAvgInpatient, stdAgeInpatient))
print("[INFO] The average age of all the outpatients: {0:.2f}+/-{1:.2f}".format(avgAvgOutpatient, stdAgeOutpatient))
print("[INFO] The average age of all the icu: {0:.2f}+/-{1:.2f}".format(avgAvgICUpatient, stdAgeICUpatient))


##############################
### filter by patient type ###
##############################
df_inpatient = df_data[df_data.patient_type == 'ip'].reset_index(drop=True)
df_outpatient = df_data[df_data.patient_type == 'op'].reset_index(drop=True)
df_icupatient = df_data[df_data.patient_type == 'icu'].reset_index(drop=True)
df_uccpatient = df_data[df_data.patient_type == 'ucc'].reset_index(drop=True)

df_cpatient = df_data[df_data.contrast == 'Y'].reset_index(drop=True)
df_nocpatient = df_data[df_data.contrast == 'N'].reset_index(drop=True)

##################################
### extract all types of scans ###
##################################
all_type_scans = df_data.order.value_counts()

# column name for the reslt dataframe
# column_name = ['scan_type', 'c1_mean', 'c1_std', 'c1_n', 'c2_mean', 'c2_std', 'c2_n', 'c3_mean', 'c3_std', 'c3_n', 'c4_mean', 'c4_std', 'c4_n']
# # create new dataframe to store result
# df_inpatient_result = pd.DataFrame(columns=column_name)
# df_outpatient_result = pd.DataFrame(columns=column_name)
# df_icupatient_result = pd.DataFrame(columns=column_name)
# df_uccpatient_result = pd.DataFrame(columns=column_name)
# # add in the all the scans in the dataframe
# df_inpatient_result = df_inpatient_result.assign(scan_type = all_type_scans.index)
# df_outpatient_result = df_inpatient_result.assign(scan_type = all_type_scans.index)
# df_icupatient_result = df_inpatient_result.assign(scan_type = all_type_scans.index)
# df_uccpatient_result = df_inpatient_result.assign(scan_type = all_type_scans.index)
# # set the scan_type as index
# df_inpatient_result.set_index('scan_type', inplace=True)
# df_outpatient_result.set_index('scan_type', inplace=True)
# df_icupatient_result.set_index('scan_type', inplace=True)
# df_uccpatient_result.set_index('scan_type', inplace=True)


#################
### inpatient ###
#################
# ## 12 condictions (contrast, level, age)
# # Condition1: (no contract + High + Junior)
# df_inpatient_noc_high_junior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_level == 'high') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# # Condition2: (no contract + High + Senior)
# df_inpatient_noc_high_senior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_level == 'high') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)
# # Condition3: (no contract + Moderate + Junior)
# df_inpatient_noc_mod_junior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_level == 'moderate') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# # Condition4: (no contract + Low + Junior)
# df_inpatient_noc_low_junior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_level == 'low') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# # Condition5: (no contract + Moderate + Senior)
# df_inpatient_noc_mod_senior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_level == 'moderate') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)
# # Condition6: (no contract + Low + Senior)
# df_inpatient_noc_low_senior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_level == 'low') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)
# # Condition7: (contract + High + Junior)
# df_inpatient_c_high_junior = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_level == 'high') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# # Condition8: (contract + High + Senior)
# df_inpatient_c_high_senior = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_level == 'high') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)
# # Condition9: (contract + Moderate + Junior)
# df_inpatient_noc_mod_juinor = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_level == 'moderate') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# # Condition10: (contract + Low + Junior)
# df_inpatient_c_low_juinor = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_level == 'low') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# # Condition11: (contract + Moderate + Senior)
# df_inpatient_c_mod_senior = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_level == 'moderate') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)
# # Condition12: (contract + Low + Senior)
# df_inpatient_c_low_senior = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_level == 'low') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)

# ## 4 condictions (contrast, age)
# # Condition1: (no contrast + Junior)
# df_inpatient_noc_junior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# dict_inpatient_noc_junior_data_scan, dict_inpatient_noc_junior_result = cal_time_based_on_order(df_inpatient_noc_junior, df_inpatient_noc_junior.order)
# # Condition2: (no contrast + Senior)
# df_inpatient_noc_senior = df_inpatient.loc[(df_inpatient.contrast == 'N') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)
# dict_inpatient_noc_senior_data_scan, dict_inpatient_noc_senior_result = cal_time_based_on_order(df_inpatient_noc_senior, df_inpatient_noc_senior.order)
# # Condition3: (contrast + Junior)
# df_inpatient_c_junior = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_age == 'junior')].reset_index(drop=True)
# dict_inpatient_c_junior_data_scan, dict_inpatient_c_junior_result = cal_time_based_on_order(df_inpatient_c_junior, df_inpatient_c_junior.order)
# # Condition4: (contrast + Senior)
# df_inpatient_c_senior = df_inpatient.loc[(df_inpatient.contrast == 'Y') & (df_inpatient.class_age == 'senior')].reset_index(drop=True)
# dict_inpatient_c_senior_data_scan, dict_inpatient_c_senior_result = cal_time_based_on_order(df_inpatient_c_senior, df_inpatient_c_senior.order)

# ## merge all the resulted dictionaries to one dataframe
# for key, value in dict_inpatient_noc_junior_result.items():
#     df_inpatient_result.loc[key, 0:3] = value
# for key, value in dict_inpatient_noc_senior_result.items():
#     df_inpatient_result.loc[key, 3:6] = value    
# for key, value in dict_inpatient_c_junior_result.items():
#     df_inpatient_result.loc[key, 6:9] = value
# for key, value in dict_inpatient_c_senior_result.items():
#     df_inpatient_result.loc[key, 9:12] = value    
    
# generate result for in/out/icu/ucc patient
# df_inpatient_result, dict_c1, dict_c2, dict_c3, dict_c4 = generate_result(df_inpatient, all_type_scans)
df_inpatient_result = generate_result_four_conditions(df_inpatient, all_type_scans)
df_outpatient_result = generate_result_four_conditions(df_outpatient, all_type_scans)
df_icupatient_result = generate_result_four_conditions(df_icupatient, all_type_scans)
df_uccpatient_result = generate_result_four_conditions(df_uccpatient, all_type_scans)

# generate result for contrast or no-contrast
df_cpatient_result = generate_result(df_cpatient, all_type_scans)
df_nocpatient_result = generate_result(df_nocpatient, all_type_scans)
    
# export to .xlsx 
df_inpatient_result.to_excel("../results/database/inpatient_result.xlsx")
df_outpatient_result.to_excel("../results/database/outpatient_result.xlsx")
df_icupatient_result.to_excel("../results/database/icupatient_result.xlsx")
df_uccpatient_result.to_excel("../results/database/uccpatient_result.xlsx")

df_cpatient_result.to_excel("../results/database/contrast_patient_result.xlsx")
df_nocpatient_result.to_excel("../results/database/non-contrast_patient_result.xlsx")
print("[INFO] Data successfully generated")
