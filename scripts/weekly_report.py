# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 09:17:04 2021

@author: Chang
"""
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import selfbuildlib as lib
import pandas as pd
import os


######################
### file directory ###
######################
read_directory = "../data/clean/"
weekly_result_directory = "../results/weekly report/"
read_file_name = "11-Jan-16-Jan_clean"
write_directory = weekly_result_directory + read_file_name +"/"

# create folder if not exist
if not os.path.exists(weekly_result_directory+read_file_name):
    os.makedirs(weekly_result_directory+read_file_name)




############
### plot ###
############
sns.set()

def pie_draw_n(pct, allvals, txt):
    absolute = round(pct/100.*np.sum(allvals))
    return_txt = ""
    if txt == "all":
        return_txt = "{:.1f}%\n({:})".format(pct, absolute)
    elif txt == "per":
        return_txt = "{:.1f}%".format(pct)
    else:
        return_txt = "{:.1f}%\n({:})".format(pct, absolute)
    return return_txt

def bar_autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

###########################
### read the excel file ###
########################### 



xls = pd.ExcelFile(read_directory+read_file_name+".xlsx")
dict_data = pd.read_excel(xls, sheet_name=None, ignore_index=True)

## Create the dataframe for the remaining data
df_data = pd.concat(dict_data, ignore_index=True)

## Convert the account number to list type
# df_data = lib.convert_acc_to_list(df_data)


###########################
### create sub-dataset  ###
########################### 
df_normal = df_data.copy()
df_data_wo_recall = df_data.copy()
df_failed = df_normal[df_normal.successful == 'n']
df_recall = df_normal[df_normal.recall == 'y']
df_normal.drop(index = df_failed.index, inplace=True)
df_normal.drop(index = df_recall.index, inplace=True)
df_data_wo_recall.drop(index = df_recall.index, inplace=True)
df_normal.reset_index(drop=True, inplace=True)
df_failed.reset_index(drop=True, inplace=True)
df_recall.reset_index(drop=True, inplace=True)


#############################
### (Money) In-room Time  ###
#############################
time_money = round(df_normal["in_room_time"].sum())
time_failed = round(df_failed["in_room_time"].sum())
time_recall = round(df_recall["in_room_time"].sum())
time_idle = round(df_data["idle_time"].sum())
time_total = time_money+time_failed+time_recall
time_other = time_failed+time_recall


## Plot pie chart
plt.figure()

if time_other/ time_total < 0.01:
    data = [time_money, time_other, time_idle]
    label = ['successful', 'other', 'idle']
    plt.title("The total time:{}.\nThe successful time:{}    idle time:{}   other time:{}".format(time_total, time_money, time_idle, time_other))
else:
    data = [time_money, time_failed, time_recall, time_idle]
    label = ['successful', 'failed', 'recall', 'idle']
    plt.title("The total time:{}.\nThe successful time:{}    idle time:{}   recall time:{}  failed time:{}".format(time_total, time_money, time_idle, time_recall, time_failed))
    
plt.pie(x=data, labels=label, autopct=lambda pct: pie_draw_n(pct, data, "per"))
plt.show()
plt.savefig(write_directory + 'time_allocation.png')


##########################
### Number of patients ###
##########################
# number of patients (total, unsuccessful, recall)
num_patients = df_data_wo_recall.shape[0]
num_patients_un = df_failed.shape[0]

print("[RES] The number of patients (total):{}".format(num_patients))
print("[RES] The number of unsuccessful patients:{}".format(num_patients_un))


# number of male and female patients
num_patients_male = df_data_wo_recall[df_data_wo_recall.gender == 'm'].shape[0]
num_patients_female = df_data_wo_recall[df_data_wo_recall.gender == 'f'].shape[0]
print("[RES] The number of male patients:{}".format(num_patients_male))
print("[RES] The number of female patients:{}".format(num_patients_female))


## figures
# pie chart - female v.s male patient
plt.figure()
data = [num_patients_male, num_patients_female]
plt.pie(x=data, labels=['male', 'female'], autopct=lambda pct: pie_draw_n(pct, data, "all"))
plt.title("The total number of patients:{}".format(num_patients))
plt.show()
plt.savefig(write_directory + 'Number of patients - gender.png')


########################
### Number of recall ###
########################
num_patients_recall = df_recall.shape[0]
print("[RES] The number of recall:{}".format(num_patients_recall))


#####################
### Ability level ###
#####################
# row score
plt.figure()
plt.hist(df_data_wo_recall.level_cooperation, bins=5)
plt.title("Patient Level of Cooperation Distribution (n={})".format(df_data_wo_recall.shape[0]))
plt.xlabel("Ability Score")
plt.ylabel("the number of patients")
plt.show()
plt.savefig(write_directory + 'ability_level.png')
print("[RES] The average ability score among all patients is:{:.2f}+/-{:.2f} (n={})".format(df_data_wo_recall['level_cooperation'].mean(), df_data_wo_recall['level_cooperation'].std(), df_data_wo_recall['level_cooperation'].shape[0]))

# ability group (class)
num_high = df_data_wo_recall[df_data_wo_recall.ability_class == 'high'].shape[0]
num_moderate = df_data_wo_recall[df_data_wo_recall.ability_class == 'moderate'].shape[0]
num_low= df_data_wo_recall[df_data_wo_recall.ability_class == 'low'].shape[0]

plt.figure()
data = [num_high, num_moderate, num_low]
plt.pie(x=data, labels=['high', 'moderate', 'low'], autopct=lambda pct: pie_draw_n(pct, data, "all"))
plt.title("The patient Cooperation Level (n:{})".format(df_data_wo_recall.shape[0]))
plt.show()
plt.savefig(write_directory + 'class_level.png')
print("[RES] The number of patients are high level:{}".format(num_high))
print("[RES] The number of patients are high level:{}".format(num_moderate))
print("[RES] The number of patients are high level:{}".format(num_low))


###################################
### Number of sedated patients ###
###################################
num_non_sedation = df_data[df_data.sedation == 'n'].shape[0]
num_or_sedation = df_data[df_data.sedation == 'oral sedation'].shape[0]
num_iv_sedation = df_data[df_data.sedation == 'iv sedation'].shape[0]
num_ga_sedation = df_data[df_data.sedation == 'ga'].shape[0]
num_sedation = num_or_sedation + num_iv_sedation + num_ga_sedation

# print("[RES] The number of non-sedation patinets:{}".format(num_sedation))
print("[RES] The number of sedated patinets:{}".format(num_sedation))
if(num_or_sedation != 0):
    print("[RES] The number of oral sedation:{}".format(num_or_sedation))
if(num_iv_sedation != 0):
    print("[RES] The number of iv sedation:{}".format(num_iv_sedation))
if(num_or_sedation != 0):
    print("[RES] The number of ga sedation:{}".format(num_ga_sedation))
    
# plt.figure()
# data = [num_non_sedation, num_sedation]
# plt.pie(x=data, labels=['non', 'sedation'], autopct=lambda pct: pie_draw_n(pct, data))
# plt.title("The number of patients under sedation (n:{})".format(df_data.shape[0]))
# plt.show()
# plt.savefig(write_directory + 'sedation.png')


################################
### Number of orders per day ###
################################
num_orders_day = [0]*6
num_orders_day[0] = lib.calculate_num_orders(df_data_wo_recall[df_data_wo_recall.day == "Mon"])
num_orders_day[1] = lib.calculate_num_orders(df_data_wo_recall[df_data_wo_recall.day == "Tue"])
num_orders_day[2] = lib.calculate_num_orders(df_data_wo_recall[df_data_wo_recall.day == "Wed"])
num_orders_day[3] = lib.calculate_num_orders(df_data_wo_recall[df_data_wo_recall.day == "Thur"])
num_orders_day[4] = lib.calculate_num_orders(df_data_wo_recall[df_data_wo_recall.day == "Fri"])
num_orders_day[5] = lib.calculate_num_orders(df_data_wo_recall[df_data_wo_recall.day == "Sat"])


day = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']
fig, ax = plt.subplots()
rects = ax.bar(day, num_orders_day)
bar_autolabel(rects)
plt.title("The number of order each day (n={})".format(lib.calculate_num_orders(df_data_wo_recall)))
plt.show()
plt.savefig(write_directory + 'num_order-day.png')
num_orders = sum(num_orders_day)
print("[RES] The number of orders:{}".format(num_orders))
print("[RES] The number of orders on Monday:{}".format(num_orders_day[0]))
print("[RES] The number of orders on Tuesday:{}".format(num_orders_day[1]))
print("[RES] The number of orders on Wednesday:{}".format(num_orders_day[2]))
print("[RES] The number of orders on Thursday:{}".format(num_orders_day[3]))
print("[RES] The number of orders on Friday:{}".format(num_orders_day[4]))
print("[RES] The number of orders on Saterday:{}".format(num_orders_day[5]))



###########
### Age ###
###########
plt.figure()
plt.hist(df_data_wo_recall.age)
plt.title("Patient Age Distribution (n={})".format(df_data_wo_recall.shape[0]))
plt.xlabel("Age range")
plt.ylabel("the number of patients")
plt.show()
plt.savefig(write_directory + 'age.png')
print("[RES] The average age among all patients is:{:.2f}+/-{:.2f} (n={})".format(df_data_wo_recall['age'].mean(), df_data_wo_recall['age'].std(), df_data_wo_recall['age'].shape[0]))


##############################
### Number of patient type ###
##############################
num_inpatients = df_data_wo_recall[df_data_wo_recall["patient_type"] == 'ip'].shape[0]
num_outpatients = df_data_wo_recall[df_data_wo_recall["patient_type"] == 'op'].shape[0]
num_icupatients = df_data_wo_recall[df_data_wo_recall["patient_type"] == 'iuc'].shape[0]
num_uccpatients = df_data_wo_recall[df_data_wo_recall["patient_type"] == 'ucc'].shape[0]

print("[RES] The number of inpatients:{}".format(num_inpatients))
print("[RES] The number of outpatients:{}".format(num_outpatients))
print("[RES] The number of icupatients:{}".format(num_icupatients))
print("[RES] The number of uccpatients:{}".format(num_uccpatients))



plt.figure()
if num_icupatients + num_uccpatients == 0:
    data = [num_inpatients, num_outpatients]
    labels = ['inpatient', 'outpatient']
elif num_icupatients != 0:
    if num_uccpatients != 0:
        data = [num_inpatients, num_outpatients, num_icupatients, num_uccpatients]
        labels = ['inpatient', 'outpatient', 'ICU', 'UCC']
    else:
        data = [num_inpatients, num_outpatients, num_icupatients]
        labels = ['inpatient', 'outpatient', 'ICU']
elif num_uccpatients != 0:
    data = [num_inpatients, num_outpatients, num_uccpatients]
    labels=['inpatient', 'outpatient', 'UCC']
else:
    print("[ERROR] Something wrong when plotting pie chart for patient type")

plt.pie(x=data, labels=labels, autopct=lambda pct: pie_draw_n(pct, data, "all"))
plt.title("The percentage of patient type (n:{})".format(num_patients))
plt.show()
plt.savefig(write_directory + 'patient_type.png')


###################
### Output .txt ###
###################
text_file = open(write_directory + read_file_name+ "_Output.txt", "w")


text_file.write("[RES] The number of patients (total):{}\n".format(num_patients))
text_file.write("[RES] The number of unsuccessful patients:{}\n".format(num_patients_un))
text_file.write("[RES] The number of male patients:{}\n".format(num_patients_male))
text_file.write("[RES] The number of female patients:{}\n".format(num_patients_female))

text_file.write("[RES] The number of recall:{}\n".format(num_patients_recall))
text_file.write("[RES] The average ability score among all patients is:{:.2f}+/-{:.2f} (n={})\n".format(df_data_wo_recall['level_cooperation'].mean(), df_data_wo_recall['level_cooperation'].std(), df_data_wo_recall['level_cooperation'].shape[0]))
text_file.write("[RES] The number of patients are high level:{}\n".format(num_high))
text_file.write("[RES] The number of patients are moderate level:{}\n".format(num_moderate))
text_file.write("[RES] The number of patients are low level:{}\n".format(num_low))

text_file.write("[RES] The number of sedated patinets:{}\n".format(num_sedation))
if(num_or_sedation != 0):
    text_file.write("[RES] The number of oral sedation:{}\n".format(num_or_sedation))
if(num_iv_sedation != 0):
    text_file.write("[RES] The number of iv sedation:{}\n".format(num_iv_sedation))
if(num_or_sedation != 0):
    text_file.write("[RES] The number of ga sedation:{}\n".format(num_ga_sedation))

text_file.write("[RES] The number of orders:{}\n".format(num_orders))
text_file.write("[RES] The number of orders on Monday:{}\n".format(num_orders_day[0]))
text_file.write("[RES] The number of orders on Tuesday:{}\n".format(num_orders_day[1]))
text_file.write("[RES] The number of orders on Wednesday:{}\n".format(num_orders_day[2]))
text_file.write("[RES] The number of orders on Thursday:{}\n".format(num_orders_day[3]))
text_file.write("[RES] The number of orders on Friday:{}\n".format(num_orders_day[4]))
text_file.write("[RES] The number of orders on Saterday:{}\n".format(num_orders_day[5]))

text_file.write("[RES] The average age among all patients is:{:.2f}+/-{:.2f} (n={})\n".format(df_data_wo_recall['age'].mean(), df_data_wo_recall['age'].std(), df_data_wo_recall['age'].shape[0]))
text_file.write("[RES] The number of inpatients:{}\n".format(num_inpatients))
text_file.write("[RES] The number of outpatients:{}\n".format(num_outpatients))
text_file.write("[RES] The number of icupatients:{}\n".format(num_icupatients))
text_file.write("[RES] The number of uccpatients:{}\n".format(num_uccpatients))


text_file.close()









