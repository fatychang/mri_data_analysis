# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 15:00:46 2020

This script aims to generate weekly report which provide the following information in that week
==Basic Information ==
- The number of patients
- Patient type (in/out/icu/ucc patients)
- The number of orders
- Demongraphic of the patients (gender, age, ability level)
- The number of failed cases
- The number of recalls

@author: Chang
"""

import selfbuildlib as lib

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import collections


###########################
### read the excel file ###
########################### 

# filename = "../data/23-28-Nov.xlsx"
# filename = "../data/30-Nov-26-Dec-new.xlsx"
filename = "../data/fake-data1.xlsx"
df_data, dict_data = lib.read_data(filename)

###########################
### feature engineering ###
###########################

## ONLY for this file'../data/30-Nov-26-Dec-new.xlsx'
if filename == '../data/30-Nov-26-Dec-new.xlsx':
    df_data.drop(df_data.columns[-1], axis=1, inplace=True)

## Remove rows where the acc. value is nan
df_data = df_data[df_data["acc."].notna()]

## Remove unused columns
unused_cols = ["remark"]
df_data = lib.remove_unused_cols(df_data, unused_cols)

## Covert the value in col to lower letter
lower_let_col = ['gender', 'patient_type', 'order', 'contrast', 'operator',
                 'successful', 'sedation',  'precaution', 'implants']
df_data = lib.all_small(df_data, lower_let_col)

## Convert the data type in acc. to list
df_data = lib.convert_acc_to_list(df_data)


# Calculate the patient ability level
df_data = lib.cal_level_of_coorperation(df_data)   
# Classify patient ability level to High(11-15), Moderate(6-10) or Low(1-5)
# add a new column in the dataframe
new_feature = ['']*df_data.shape[0]
df_data['ability_class'] = new_feature
# classify patient ability level to one of the group
df_data = lib.classify_patient_level(df_data, 'ability_class')

## Classify age to Junior and Senior
df_data['age_class'] = new_feature
ageThres = 70
# classify patient to either junior or senior based on the threshold
df_data = lib.classify_patient_age(df_data, ageThres, 'age_class')

## Add the day to the column
df_data['day'] = new_feature
date = df_data.date.unique()
day = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']
day_count = 0
# for i in range(df_data.shape[0]):
for i in range(14):
    if(df_data.date[i] == date[day_count]):
        df_data.day[i] = day[day_count]
        print(i, df_data.date[i])
    else:
        day_count +=1
        print(i, day_count)
        if day_count == len(day):
            print("here")
            break
        
        df_data.day[i] = day[day_count]

## ONLY for this file'../data/30-Nov-26-Dec-new.xlsx'
if filename == '../data/30-Nov-26-Dec-new.xlsx':
    label = [111, 126, 128, 171, 221] 
    df_data.drop(index=label, inplace=True)
    df_data.reset_index(drop=True, inplace=True)


## Create a new dataframe to store the original (without extracting the unsuccessful and recalled cases)
df_ori = df_data.copy()

## Extract the unsuccessful cases from the main database
df_un = df_data[df_data.successful == 'n']
df_data.drop(index = df_un.index, inplace=True)
df_data.reset_index(drop=True, inplace=True)
df_un.reset_index(drop=True, inplace=True)

## Calculate duration (in-room time) transfer_end - transfer_start
df_data["in_room_dur"] = ['']*df_data.shape[0]
df_data = lib.calculate_duration(df_data, "transfer end_time", "transfer strat_time", "in_room_dur")


## Extract cases which have been recalled (duplicated)
# create a list to store all the account number
all_acc = []
for val in df_data["acc."]:
    for i in range(len(val)):
        all_acc.append(val[i])
        
# create a new dataframe storing the duplicated (recall) cases
df_data, df_recall = lib.find_duplicates(df_data, all_acc)


#################
### df_recall ###
#################
# convert the acc. datatype from list back to str.
df_recall['acc.'] = [','.join(map(str, l)) for l in df_recall['acc.']]



############
### plot ###
############
sns.set()

## ONLY for this file'../data/30-Nov-26-Dec-new.xlsx'
if filename == '../data/30-Nov-26-Dec-new.xlsx':
    figloc = "../results/database/"
else:
    figloc = "../results/weekly report/"

def pie_draw_n(pct, allvals):
    absolute = round(pct/100.*np.sum(allvals))

    return "{:.1f}%\n({:})".format(pct, absolute)

def bar_autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

##########################
### Number of patients ###
##########################
# number of patients (total, unsuccessful, recall)
num_patients_database = df_data.shape[0]
num_patients_un = df_un.shape[0]
num_patients_recall = df_recall.nunique()['acc.']
num_patients = num_patients_database + num_patients_un + num_patients_recall
print("[RES] The number of patients:{}".format(num_patients))
print("[RES] The number of unsuccessful patients:{}".format(num_patients_un))
print("[RES] The number of recall patients:{}".format(num_patients_recall))

# number of patients (male)
num_patients_male_database = df_data[df_data.gender == 'm'].shape[0]
num_patients_male_un = df_un[df_un.gender == 'm'].shape[0]
num_patients_male_recall = df_recall[df_recall.gender == 'm'].nunique()['acc.']
num_patients_male = num_patients_male_database + num_patients_male_un + num_patients_male_recall
print("[RES] The number of male patients:{}".format(num_patients_male))

# number of patients (female)
num_patients_female_database = df_data[df_data.gender == 'f'].shape[0]
num_patients_female_un = df_un[df_un.gender == 'f'].shape[0]
num_patients_female_recall = df_recall[df_recall.gender == 'f'].nunique()['acc.']
num_patients_female = num_patients_female_database + num_patients_female_un + num_patients_female_recall
print("[RES] The number of female patients:{}".format(num_patients_female))

## figures
# pie chart - female v.s male patient
plt.figure()
data = [num_patients_male, num_patients_female]
plt.pie(x=data, labels=['male', 'female'], autopct=lambda pct: pie_draw_n(pct, data))
plt.title("The total number of patients:{}".format(num_patients))
plt.show()
plt.savefig(figloc + 'Number of patients - gender.png')

# pie chart - normal vs. unsuccessful vs. recall
plt.figure()
data = [num_patients_database, num_patients_un, num_patients_recall]
plt.pie(x=data, labels=['normal', 'successful', 'recall'], autopct=lambda pct: pie_draw_n(pct, data))
plt.title("The total number of patients:{}".format(num_patients))
plt.show()
plt.savefig(figloc + 'Number of patients - normal_un_recall.png')


########################
### Number of orders ###
########################
# calculate the number of orders
num_orders_database = lib.calculate_num_orders(df_data)
num_orders_inpatients = lib.calculate_num_orders(df_data[df_data.patient_type == 'ip'])
num_orders_outpatients = lib.calculate_num_orders(df_data[df_data.patient_type == 'op'])
num_orders_icupatients = lib.calculate_num_orders(df_data[df_data.patient_type == 'icu'])
num_orders_uccpatients = lib.calculate_num_orders(df_data[df_data.patient_type == 'ucc'])
print("[RES] The number of orders:{}".format(num_orders_database))
print("[RES] The number of inpatient orders:{}/{}".format(num_orders_inpatients, num_orders_database))
print("[RES] The number of outpatient orders:{}/{}".format(num_orders_outpatients, num_orders_database))
print("[RES] The number of icupatient orders:{}/{}".format(num_orders_icupatients, num_orders_database))
print("[RES] The number of uccpatient orders:{}/{}".format(num_orders_uccpatients, num_orders_database))

if num_orders_icupatients + num_orders_uccpatients == 0:
    data = [num_orders_inpatients, num_orders_outpatients]
    labels = ['inpatient', 'outpatient']
elif num_orders_icupatients != 0:
    if num_orders_uccpatients != 0:
        data = [num_orders_inpatients, num_orders_outpatients, num_orders_icupatients, num_orders_uccpatients]
        labels = ['inpatient', 'outpatient', 'icu', 'ucc']
    else:
        data = [num_orders_inpatients, num_orders_outpatients, num_orders_icupatients]
        labels = ['inpatient', 'outpatient', 'icu']
elif num_orders_uccpatients != 0:
    data = [num_orders_inpatients, num_orders_outpatients, num_orders_uccpatients]
    labels=['inpatient', 'outpatient', 'ucc']
else:
    print("[ERROR] Something wrong when plotting pie chart for patient type")

plt.figure()
plt.pie(x=data, labels=labels, autopct=lambda pct: pie_draw_n(pct, data))    
plt.title("The total number of orders:{}".format(num_orders_database))
plt.show()
plt.savefig(figloc + 'orders - patient type.png')


###########
### Age ###
###########
plt.figure()
plt.hist(df_ori.age)
plt.title("Patient Age Distribution (n={})".format(df_ori.shape[0]))
plt.xlabel("Age range")
plt.ylabel("the number of patients")
plt.show()
plt.savefig(figloc + 'age.png')
print("[RES] The average age among all patients is:{:.2f}+/-{:.2f} (n={})".format(df_ori['age'].mean(), df_ori['age'].std(), df_ori['age'].shape[0]))


#####################
### Ability level ###
#####################
# row score
plt.figure()
plt.hist(df_ori.level_cooperation, bins=5)
plt.title("Patient Level of Cooperation Distribution (n={})".format(df_ori.shape[0]))
plt.xlabel("Ability Score")
plt.ylabel("the number of patients")
plt.show()
plt.savefig(figloc + 'ability_level.png')
print("[RES] The average ability score among all patients is:{:.2f}+/-{:.2f} (n={})".format(df_ori['level_cooperation'].mean(), df_ori['level_cooperation'].std(), df_ori['level_cooperation'].shape[0]))


# ability group (class)
num_high = df_ori[df_ori.class_level == 'high'].shape[0]
num_moderate = df_ori[df_ori.class_level == 'moderate'].shape[0]
num_low= df_ori[df_ori.class_level == 'low'].shape[0]
plt.figure()
data = [num_high, num_moderate, num_low]
plt.pie(x=data, labels=['high', 'moderate', 'low'], autopct=lambda pct: pie_draw_n(pct, data))
plt.title("The patient Cooperation Level (n:{})".format(df_ori.shape[0]))
plt.show()
plt.savefig(figloc + 'class_level.png')
print("[RES] The number of patients are high level:{}".format(num_high))
print("[RES] The number of patients are high level:{}".format(num_moderate))
print("[RES] The number of patients are high level:{}".format(num_low))



############
### Days ###
############
## NOT applicable for database 
## ONLY for this file'../data/30-Nov-26-Dec-new.xlsx' 
if filename != '../data/30-Nov-26-Dec-new.xlsx':
    days = df_ori.date.unique()   
    num_orders_day = []
    day = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']
    num_orders_day.append(lib.calculate_num_orders(df_ori[df_ori.date == days[0]]))
    num_orders_day.append(lib.calculate_num_orders(df_ori[df_ori.date == days[1]]))
    num_orders_day.append(lib.calculate_num_orders(df_ori[df_ori.date == days[2]]))
    num_orders_day.append(lib.calculate_num_orders(df_ori[df_ori.date == days[3]]))
    num_orders_day.append(lib.calculate_num_orders(df_ori[df_ori.date == days[4]]))
    num_orders_day.append(lib.calculate_num_orders(df_ori[df_ori.date == days[5]]))
    
    fig, ax = plt.subplots()
    rects = ax.bar(day, num_orders_day)
    bar_autolabel(rects)
    plt.title("The number of order each day (n={})".format(lib.calculate_num_orders(df_ori)))
    plt.show()
    plt.savefig(figloc + 'num_order-day.png')
    print("[RES] The number of orders on Monday:{}".format(num_orders_day[0]))
    print("[RES] The number of orders on Tuesday:{}".format(num_orders_day[1]))
    print("[RES] The number of orders on Wednesday:{}".format(num_orders_day[2]))
    print("[RES] The number of orders on Thursday:{}".format(num_orders_day[3]))
    print("[RES] The number of orders on Friday:{}".format(num_orders_day[4]))
    print("[RES] The number of orders on Saterday:{}".format(num_orders_day[5]))


###################################
### Number of sedation patients ###
###################################
num_non_sedation = df_data[df_data.sedation == 'n'].shape[0]
num_or_sedation = df_data[df_data.sedation == 'oral sedation'].shape[0]
num_iv_sedation = df_data[df_data.sedation == 'iv sedation'].shape[0]
num_ga_sedation = df_data[df_data.sedation == 'ga'].shape[0]
num_sedation = num_or_sedation + num_iv_sedation + num_ga_sedation
print("[RES] The number of non-sedation patinets:{}".format(num_sedation))
print("[RES] The number of sedation patinets:{}".format(num_sedation))
if(num_or_sedation != 0):
    print("[RES] The number of oral sedation patinets:{}".format(num_or_sedation))
if(num_iv_sedation != 0):
    print("[RES] The number of iv sedation patinets:{}".format(num_iv_sedation))
if(num_or_sedation != 0):
    print("[RES] The number of ga sedation patinets:{}".format(num_ga_sedation))
    
plt.figure()
data = [num_non_sedation, num_sedation]
plt.pie(x=data, labels=['non', 'sedation'], autopct=lambda pct: pie_draw_n(pct, data))
plt.title("The number of patients under sedation (n:{})".format(df_data.shape[0]))
plt.show()
plt.savefig(figloc + 'sedation.png')

####################
### In-room time ###
####################
# extract the cases when there is no scan time in the record
df_un["in_room_dur"] = ['']*df_un.shape[0]
mask = df_un['transfer end_time'].isnull()
df_un_dir = df_un[mask]
df_un = df_un[~mask]
df_un = lib.calculate_duration(df_un, "transfer end_time", "transfer strat_time", "in_room_dur")

#calculate scan time
scan_time_database = df_data['in_room_dur'].sum()
scan_time_un = df_un['in_room_dur'].sum()
scan_time_recall = df_recall['in_room_dur'].sum()

if scan_time_un == 0 and scan_time_recall == 0:
    data = [scan_time_database]
    labels = ['successful']
elif scan_time_un == 0:
    data = [scan_time_database, scan_time_recall]
    labels = ['successful', 'recall']
elif scan_time_recall == 0:
    data = [scan_time_database, scan_time_un]   
    labels = ['successful', 'unsuccessful']
else:
    data = [scan_time_database, scan_time_un, scan_time_recall]   
    labels = ['successful', 'unsuccessful', 'recall']

plt.figure()
plt.pie(x=data, labels=labels, autopct=lambda pct: pie_draw_n(pct, data))
plt.title("In-room time for successful/unsuccessful/recall (mins)")
plt.show()
plt.savefig(figloc + 'in-room time-successful_unsuccessful_recall.png')

print("[RES] The total scan time for successful orders (min.):{}".format(scan_time_database))
print("[RES] The total scan time for unsuccessful orders (min.):{}".format(scan_time_un))
print("[RES] The total scan time for recall patients(min.):{}".format(scan_time_recall))

#################
### Idle time ###
#################
df_ori["idle_time"] = ['']*df_ori.shape[0]    
for i in range(df_ori.shape[0]):
    if i == df_ori.shape[0]-1:
        df_ori.idle_time[i] = 0
        break
    if df_ori.day[i] == df_ori.day[i+1]: #same day
        start = df_ori["transfer end_time"][i]
        end = df_ori["transfer strat_time"][i+1]
        df_ori.idle_time[i] = lib.minute_interval(start, end)
    else:
        df_ori.idle_time[i] = 0
        


#####################
### Sedation time ###
#####################
mask = df_data.sedation == 'n'
scan_time_nonsedation = df_data[mask]['in_room_dur'].sum()
scan_time_sedation = df_data[~mask]['in_room_dur'].sum()

plt.figure()
data = [scan_time_nonsedation, scan_time_sedation]
plt.pie(x=data, labels=['scan_time_nonsedation', 'scan_time_sedation'], autopct=lambda pct: pie_draw_n(pct, data))
plt.title("In-room time for sedation and non-sedation time (mins)")
plt.show()
plt.savefig(figloc + 'in-room time-sedation.png')


################################
### Average number of orders ###
################################
if filename == '../data/30-Nov-26-Dec-new.xlsx':
    num_days = len(dict_data)
    ave_num_patients = num_patients/ num_days
    ave_num_orders = num_orders_database/ num_days
    print("[RES] The average number of patients per day:{:.2f}".format(ave_num_patients))
    print("[RES] The average number of orders per day:{:.2f}".format(ave_num_orders))


###################
### Output .txt ###
###################

text_file = open(figloc + "Output.txt", "w")

## Number of patients
text_file.write("[RES] The number of patients:{}\n".format(num_patients))
text_file.write("[RES] The number of female patients:{}\n".format(num_patients_female))
text_file.write("[RES] The number of male patients:{}\n".format(num_patients_male))
text_file.write("[RES] The number of unsuccessful patients:{}/{}\n".format(num_patients_un, num_patients))
text_file.write("[RES] The number of recall patients:{}\n".format(num_patients_recall))

## Number of orders
text_file.write("[RES] The number of successful orders:{}\n".format(num_orders_database))
text_file.write("[RES] The number of successful inpatient orders:{}/{}\n".format(num_orders_inpatients, num_orders_database))
text_file.write("[RES] The number of successful outpatient orders:{}/{}\n".format(num_orders_outpatients, num_orders_database))
text_file.write("[RES] The number of successful icupatient orders:{}/{}\n".format(num_orders_icupatients, num_orders_database))
text_file.write("[RES] The number of successful uccpatient orders:{}/{}\n".format(num_orders_uccpatients, num_orders_database))

## Age
text_file.write("[RES] The average age among all patients is:{:.2f}+/-{:.2f} (n={})\n".format(df_ori['age'].mean(), df_ori['age'].std(), df_ori['age'].shape[0]))

## Ability data
text_file.write("[RES] The average ability score among all patients is:{:.2f}+/-{:.2f} (n={})\n".format(df_ori['level_cooperation'].mean(), df_ori['level_cooperation'].std(), df_ori['level_cooperation'].shape[0]))
text_file.write("[RES] The number of patients are high level:{}\n".format(num_high))
text_file.write("[RES] The number of patients are moderate level:{}\n".format(num_moderate))
text_file.write("[RES] The number of patients are low level:{}\n".format(num_low))

## Date
if filename != '../data/30-Nov-26-Dec-new.xlsx':
    text_file.write("[RES] The number of orders on Monday:{}\n".format(num_orders_day[0]))
    text_file.write("[RES] The number of orders on Tuesday:{}\n".format(num_orders_day[1]))
    text_file.write("[RES] The number of orders on Wednesday:{}\n".format(num_orders_day[2]))
    text_file.write("[RES] The number of orders on Thursday:{}\n".format(num_orders_day[3]))
    text_file.write("[RES] The number of orders on Friday:{}\n".format(num_orders_day[4]))
    text_file.write("[RES] The number of orders on Saterday:{}\n".format(num_orders_day[5]))

## Sedation
text_file.write("[RES] The number of non-sedation patinets:{}\n".format(num_patients-num_sedation))
text_file.write("[RES] The number of sedation patinets:{}\n".format(num_sedation))
text_file.write("[RES] The number of oral sedation patinets:{}\n".format(num_or_sedation))
text_file.write("[RES] The number of iv sedation patinets:{}\n".format(num_iv_sedation))
text_file.write("[RES] The number of ga sedation patinets:{}\n".format(num_ga_sedation))

## In-room time
text_file.write("[RES] The total scan time for successful orders (min.):{}\n".format(scan_time_database))
text_file.write("[RES] The total scan time for unsuccessful orders (min.):{}\n".format(scan_time_un))
text_file.write("[RES] The total scan time for recall patients(min.):{}\n".format(scan_time_recall))

## Idle time

text_file.close()
