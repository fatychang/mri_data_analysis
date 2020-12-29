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
filename = "../data/30-Nov-26-Dec-new.xlsx"
df_data = lib.read_data(filename)

###########################
### feature engineering ###
###########################

## clean the dataset and calculate the ability level and group them accordingly
df_data, df_failed, all_acc= lib.clean_data(df_data, ["remark"], 70)

## extract the duplicated cases (recall)
df_data, df_recall = lib.find_duplicates(df_data, all_acc)


#######################
### results & plots ###
######################
sns.set()
figloc = "../results/weekly report/"

# the number of patients
num_patients = df_data.shape[0]
num_female = df_data[df_data.gender == 'f'].shape[0]
num_male = df_data[df_data.gender == 'm'].shape[0]
print("[RES] The number of patients:{}".format(num_patients))
print("[RES] The number of female patients:{}".format(num_female))
print("[RES] The number of male patients:{}".format(num_male))

def func(pct, allvals):
    absolute = round(pct/100.*np.sum(allvals))

    return "{:.1f}%\n({:})".format(pct, absolute)

plt.figure()
data = [num_female, num_male]
plt.pie(x=data, labels=['female', 'male'], autopct=lambda pct: func(pct, data))
plt.title("The total number of patients:{}".format(num_patients))
plt.show()
plt.savefig(figloc + 'gender.png')

# the type of patients
num_inpatients = df_data[df_data.patient_type == 'ip'].shape[0]
num_outpatients = df_data[df_data.patient_type == 'op'].shape[0]
num_icupatients = df_data[df_data.patient_type == 'icu'].shape[0]
num_uccpatients = df_data[df_data.patient_type == 'ucc'].shape[0]

if num_icupatients + num_uccpatients == 0:
    data = [num_inpatients, num_outpatients]
    labels = ['inpatient', 'outpatient']
elif num_icupatients != 0:
    if num_uccpatients != 0:
        data = [num_inpatients, num_outpatients, num_icupatients, num_uccpatients]
        labels = ['inpatient', 'outpatient', 'icu', 'ucc']
    else:
        data = [num_inpatients, num_outpatients, num_icupatients]
        labels = ['inpatient', 'outpatient', 'icu']
elif num_uccpatients != 0:
    data = [num_inpatients, num_outpatients, num_uccpatients]
    labels=['inpatient', 'outpatient', 'ucc']
else:
    print("[ERROR] Something wrong when plotting pie chart for patient type")

plt.figure()
plt.pie(x=data, labels=labels, autopct=lambda pct: func(pct, data))    
plt.title("The total number of patients:{}".format(num_patients))
plt.show()
plt.savefig(figloc + 'patient type.png')

# the number of order
num_orders = lib.calculate_num_orders(df_data)
# tmp = df_data[df_data.date=="27 Nov"]
# num_orders = lib.calculate_num_orders(df_data[df_data.date=="27 Nov"])
print("[RES] The number of orders done:{}".format(num_orders))

# the number of failed cases
df_failed = df_data[df_data.successful=="n"]
num_failed = df_failed.shape[0]
print("[RES] The number of failed case:{}".format(num_failed))

# age
plt.figure()
plt.hist(df_data.age)
plt.title("Patient Age Distribution")
plt.xlabel("Age range")
plt.ylabel("the number of patients")
plt.show()
plt.savefig(figloc + 'age.png')

# ability level
plt.figure()
plt.hist(df_data.level_cooperation, bins=5)
plt.title("Patient Level of Cooperation Distribution")
plt.xlabel("Ability Score")
plt.ylabel("the number of patients")
plt.show()
plt.savefig(figloc + 'ability_level.png')

## class_level
num_high = df_data[df_data.class_level == 'high'].shape[0]
num_moderate = df_data[df_data.class_level == 'moderate'].shape[0]
num_low= df_data[df_data.class_level == 'low'].shape[0]

plt.figure()
data2 = [num_high, num_moderate, num_low]
# data2 = [34, 15, 15]
plt.pie(x=data2, labels=['high', 'moderate', 'low'], autopct=lambda pct: func(pct, data2))
plt.title("The total number of patients:{}".format(num_patients))
plt.show()
plt.savefig(figloc + 'class_level.png')


# the number of orders
days = df_data.date.unique()   
patients_day = []
day = ['Mod', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat']
patients_day.append(df_data[df_data.date == days[0]].shape[0])
patients_day.append(df_data[df_data.date == days[1]].shape[0])
patients_day.append(df_data[df_data.date == days[2]].shape[0])
patients_day.append(df_data[df_data.date == days[3]].shape[0])
patients_day.append(df_data[df_data.date == days[4]].shape[0])
patients_day.append(df_data[df_data.date == days[5]].shape[0])

fig, ax = plt.subplots()
rects = ax.bar(day, patients_day)

def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects)
plt.title("The number of order per day")
plt.show()
plt.savefig(figloc + 'num_order.png')

## in-room time
new_feature = ['']*df_data.shape[0]
df_data['in_room_minute'] = new_feature
for j in range (len(patients_day)):
    for i in range (df_data[df_data.date == days[j]].shape[0]):   
        if j==0:
            index = i
        else:
            prev = 0
            for k in range(j):
                prev += patients_day[k]
                index = i+prev
                
        start = df_data["transfer strat_time"][index]
        end = df_data["transfer end_time"][index]
        df_data['in_room_minute'][index] = lib.minute_interval(start, end)


## number of sedation cases
num_or_sedation = df_data[df_data.sedation == 'oral sedation'].shape[0]
num_iv_sedation = df_data[df_data.sedation == 'iv sedation'].shape[0]
num_ga_sedation = df_data[df_data.sedation == 'ga'].shape[0]
print("[RES] The number of sedation case:{}".format(num_or_sedation+num_iv_sedation+num_ga_sedation))
if(num_or_sedation != 0):
    print("[RES] The number of oral sedation case:{}".format(num_or_sedation))
if(num_iv_sedation != 0):
    print("[RES] The number of iv sedation case:{}".format(num_iv_sedation))
if(num_or_sedation != 0):
    print("[RES] The number of ga sedation case:{}".format(num_ga_sedation))



