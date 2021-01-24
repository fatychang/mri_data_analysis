# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 14:44:38 2021

This script is for data clean up.
Input the raw dataset (.xlsx) and generate a new .xlsx with a extended file name _clean

The process included in the data cleanup process are listed as below:
    1. Ensure all value are in small letter
    2. Calculate the taotl "in-room" time (transfer_end - transfer_start)

@author: Chang
"""

import selfbuildlib as lib

###########################
### read the excel file ###
########################### 
directory = "../data/raw/"
file_name = "11-Jan-16-Jan"
df_data, dict_data = lib.read_data(directory+file_name+".xlsm")

# reset the index
df_data.reset_index(drop=True, inplace=True)


###########################
### feature engineering ###
###########################

## Remove rows where the acc. value is nan
df_data = df_data[df_data["acc"].notna()]

# reset the index
df_data.reset_index(drop=True, inplace=True)

## Covert the value in col to lower letter
lower_let_col = ["gender", "patient_type", "order", "contrast", "operator",
                 "successful", "sedation",  "precaution", "implants"]

df_data = lib.all_small(df_data, lower_let_col)

## Calculate the patient ability level
df_data = lib.cal_level_of_coorperation(df_data) 
  
## Classify patient ability level to High(11-15), Moderate(6-10) or Low(1-5)
# add a new column in the dataframe
new_feature = [""]*df_data.shape[0]
df_data["ability_class"] = new_feature
df_data = lib.classify_patient_level(df_data, "ability_class")

## Classify age to Junior and Senior
df_data["age_class"] = new_feature
ageThres = 70
# classify patient to either junior or senior based on the threshold
df_data = lib.classify_patient_age(df_data, ageThres, "age_class")

## Add day into the dataset
df_data = lib.add_day_to_dataset(df_data)


## Calcuate idle time
df_data = lib.calculate_idle_time(df_data, 'idle_time')


#########################
### Find recall cases ###
########################
# conver the account number to list
df_data = lib.convert_acc_to_list(df_data)
all_acc = []
for val in df_data["acc"]:
    for i in range(len(val)):
        all_acc.append(val[i])

# find the duplicates
df_data, df_recall, duplicates = lib.find_duplicates(df_data, all_acc)
df_data["recall"] = ["n"]*df_data.shape[0]


# add a column named as recall (the second scan)
index = df_recall.index
for i in index:
    df_data.recall.iloc[i] = 'y'

#######################
### Output new xlsx ###
#######################
output_file_loc = "../data/clean/"
df_data.to_excel(output_file_loc+file_name+"_clean.xlsx")
