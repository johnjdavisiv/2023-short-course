# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 15:58:21 2023

@author: John
"""


import wfdb
import numpy as np
import pandas as pd
from datetime import datetime, time


base_path = 'D:/long-term-movement-monitoring-database-1.0.0/'
save_path = 'C:/temp_activity_data/'

info_file = 'ClinicalDemogData_COFL.xlsx'
home_file = 'ReportHome75h.xlsx'

#Read subject info
home_df = pd.read_excel(base_path + home_file, sheet_name = '75h', 
                        na_values = ['N/A', 'N/A ', 'na', 'nan', '?'], 
                        date_format = '%d/%m/DY', skiprows=1)
home_df.columns = home_df.columns.str.strip() # 'start ' --> 'start' (whitespace)
home_df['start'] = home_df['start'].replace('13:00?', '13:00:00')

def convert_to_time(val):
    if isinstance(val, str):
        return datetime.strptime(val, '%H:%M:%S').time()
    else:
        return val

def convert_to_datetime(val):
    if isinstance(val, str):
        return datetime.strptime(val, '%d/%m/%Y')
    else:
        return val

home_df['start'] = home_df['start'].apply(convert_to_time)
home_df['date'] = home_df['date'].apply(convert_to_datetime)
home_df = home_df[home_df['#PIGD-'] != 'FL-003'] #Drop subject, ambigious data
home_df = home_df[home_df['#PIGD-'] != 'FL-009'] #Less than one full day
home_df = home_df[home_df['#PIGD-'] != 'FL-013'] #Drop subject, missing data
home_df = home_df[home_df['#PIGD-'] != 'CO-022'] #big gap in day
home_df = home_df[home_df['#PIGD-'] != 'CO-026'] #Drop subject, missing data
home_df = home_df[home_df['#PIGD-'] != 'CO-037'] #Low wear time loks like
home_df = home_df[home_df['#PIGD-'] != 'CO-041'] #Drop subject, missing data
home_df = home_df[home_df['#PIGD-'] != 'CO-011'] #Drop subject, missing data
home_df_complete = home_df.dropna(subset=['date', 'start']).copy() #deep copy avoids alert


# ---- Get "start time" for day one
from datetime import timedelta

def combine_date_time(row):
    date = row['date']
    time = row['start']
    
    if pd.isnull(date) or pd.isnull(time):
        return pd.NaT
    
    return date + timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)

home_df_complete['init_time'] = home_df_complete.apply(combine_date_time, axis=1)


#Demographics, etc
control_df = pd.read_excel(base_path + info_file, sheet_name = 'Controls', 
                           na_values = ['N/A', 'N/A ', 'na', 'nan'], 
                           parse_dates=['Date of Evaluation'], 
                           date_format = '%d/%m/DY')
control_df["Date of Evaluation"] = pd.to_datetime(control_df["Date of Evaluation"], format = 'mixed', dayfirst=True)
control_df['subject_category'] = 'control'
control_df.columns
control_df.rename(columns = {'Gender(1-female, 0-male)':'Gender(0-male,1-female)'}, inplace=True)


#What a mess!
fall_df = pd.read_excel(base_path + info_file, sheet_name = 'Fallers', 
                           na_values = ['N/A', 'N/A ', 'na', 'nan'], 
                           parse_dates=['Date of Evaluation'], 
                           date_format = '%d/%m/DY')
fall_df["Date of Evaluation"] = pd.to_datetime(fall_df["Date of Evaluation"], format = 'mixed', dayfirst=True)
fall_df['subject_category'] = 'faller'


#stack into one df
all_df = pd.concat([fall_df, control_df])


all_subjects = all_df["#"]

#Subjects where we have data onw hen they put device on
home_subjects = home_df_complete["#PIGD-"].to_list()
# ----------------------------------------------------



import matplotlib.pyplot as plt

sub_code = list()
is_male = list()
age = list()
subject_category = list()



#all home subjects are in all_df
for i, h in enumerate(home_subjects):
    print(i)
    #Get put on time from home_df 
    data_code = h.replace('-', '')#no suffix for wfdb
    init_time = pd.to_datetime(home_df_complete.loc[home_df_complete["#PIGD-"] == h, 'init_time'].values[0])
    midnight_next_day = init_time.normalize() + pd.DateOffset(days=1)
    s_to_mid = int((midnight_next_day - init_time).total_seconds())
    
    midnight_posix = midnight_next_day.timestamp()
    timestamps = np.arange(midnight_posix, midnight_posix + 24*60*60, 0.01)
    
    #Load data
    record = wfdb.rdrecord(base_path + data_code)
    signals = np.array(record.p_signal)
    assert(record.fs == 100)
    assert(s_to_mid*100 + 86400*100 < signals.shape[0])
    
    xyz = signals[:,:3]
    
    day_zero_end = s_to_mid*100
    
    day_one_xyz = xyz[day_zero_end:day_zero_end+86400*100]
    #Stack!@!
    df = pd.DataFrame(day_one_xyz, columns=['X', 'Y', 'Z'])
    df['HEADER_TIME_STAMP'] = timestamps
    df = df[['HEADER_TIME_STAMP', 'X', 'Y', 'Z']] #Reorded
    
    
    #Save
    df.to_csv(save_path + data_code + '.csv', index=False)
    
    #get age
    if np.isnan(all_df.loc[all_df['#'] == h, 'Age'].values[0]):
        sub_age = all_df.Age.median() #hacky median impute
    else:
        sub_age = all_df.loc[all_df['#'] == h, 'Age'].values[0]
    
    sub_is_male = all_df.loc[all_df['#'] == h, 'Gender(0-male,1-female)'].values[0]
    sub_cat = all_df.loc[all_df['#'] == h, 'subject_category'].values[0]
    
    #Append
    sub_code.append(data_code)
    is_male.append(sub_is_male)
    age.append(sub_age)
    subject_category.append(sub_cat)
    
    
    # ar = np.sqrt(day_one_xyz[:,0]**2 + day_one_xyz[:,1]**2 + day_one_xyz[:,2]**2)
    # plt.figure()    
    # plt.plot(ar)
    # plt.title(h)
    
    
main_save_path = 'C:/Users/johnj/Google Drive/Research/Obesity short course 2023/data/main_df.csv'
main_df = pd.DataFrame({"sub_code": sub_code,
                        "is_male": is_male,
                        "age":age,
                        "subject_category":subject_category})

main_df.to_csv(main_save_path, index=False)

    
    
    
    

# i = 0


# h = 'FL-035'
# h.replace('-', '')

# h in all_subjects.to_list()

# all_subjects

# for h in home_subjects:
#     if h in all_subjects.to_list():
#         print('match')
#         print(h)
#         i += 1




# # ----------------------

# # Now can loop through each subject? Save data to..hmm...
# #maybe just go midnight ot midnight for first full day right here


# demo_file = 'CO024'


# # Load the wfdb record and the physical signals
# record = wfdb.rdrecord(base_path + demo_file)

# # Extract the signals as a numpy array
# signals = np.array(record.p_signal)


# # Print the signal names
# print(record.sig_name)
# #100 hz data, organized as ax ay az ox oy oz

# print(signals)

# print(record.fs) 
# print(record.comments)



# ar = np.sqrt(signals[:,0]**2 + signals[:,1]**2 + signals[:,2]**2)



# plt.plot(ar)

# #Show all attrributes
# for attr in dir(record):
#     if not attr.startswith('_'):
#         print(f"{attr} = {getattr(record, attr)}")


# #Age and sex are in "comments" field

# print(record.comments) #Watn to iterate adn print, make sure htey'er correct. 
# #['Age:75.17', 'Sex:F']