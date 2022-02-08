from os import listdir
from os.path import isfile, join
from tqdm import tqdm
import pickle
from datetime import datetime
import time
import pandas as pd
import numpy as np
import json
from work_dir.utils.data_functions import convert_time_in_seconds, outlier_removal_by_pvalue, plot_value_in_time

file = open(".\\config.json")
config_file = json.load(file)
file.close

start_script_time = time.time()

# Paths to data ---------------------------------------------------------------
trainings_path = config_file['paths']['trainings']
matches_path = config_file['paths']['trainings']

# Check that they are files and list their complete paths
all_trainings_paths = [join(trainings_path, f) for f in listdir(trainings_path) if isfile(join(trainings_path, f))]
all_matches_path = [join(matches_path, f) for f in listdir(matches_path) if isfile(join(matches_path, f))]

# Trainings: Import dict of dict {date:{expected name : {info}}}
a_file = open(config_file['paths']['date_to_name_to_info'], "rb")
date_to_name_to_info_trainings = pickle.load(a_file)

# Trainings: Import dict {expected name : date}
a_file = open(config_file['paths']['date_to_name_to_info'], "rb")
name_to_date_exercises = pickle.load(a_file)

# Matches: Import dict {date:{expected name : {info}}}
a_file = open(config_file['paths']['date_to_match_to_info'], "rb")
date_to_name_to_info_matches = pickle.load(a_file)

# Matches: Import dict {expected name : date}
a_file = open(config_file['paths']['name_to_date_matches'], "rb")
name_to_date_matches = pickle.load(a_file)


first = True
all_data = []
data_variables_lists = []
missing_in_expected_name_to_date = 0
missing_in_date_to_training_name_and_ord = 0

# Creation of a single dataset for trainings
for folder in [trainings_path, matches_path]:
    
    print('\nData loading and concatenation from:\n{}'.format(folder))
    time.sleep(1)
    
    # Check that they are files and list their complete paths
    all_data_paths = [join(folder, f) for f in listdir(folder) if isfile(join(folder, f))]
    
    for complete_data_path in tqdm(all_data_paths):
        single_data = pd.read_csv(complete_data_path, sep = ";",  decimal=",")
        
        # Get the filename
        file_extension = -4
        filename = complete_data_path[len(folder)+1 :file_extension]

        
        # Distinction for exercises order between matches and trainings
        if  folder == trainings_path:
            
            # 1) Assign the date
            date = name_to_date_exercises[filename]
            single_data['date'] = [date for i in range(single_data.shape[0])]
            
            # 2) Assign the order to all observations in the file
            order = date_to_name_to_info_trainings[date][filename]['ord']
            single_data['naive_order'] = [order for i in range(single_data.shape[0])]
            
            # 3) Group name
            group_name = date_to_name_to_info_trainings[date][filename]['group_name']
            single_data['group_name'] = [group_name for i in range(single_data.shape[0])]
   
            # 4) Assign session
            session = date_to_name_to_info_trainings[date][filename]['session_name']
            single_data['session'] = [session for i in range(single_data.shape[0])]

            # 5) Assign notes
            notes = date_to_name_to_info_trainings[date][filename]['notes']
            single_data['notes'] = [notes for i in range(single_data.shape[0])]

            # 6) Note the source dataset
            single_data['from'] = ['trainings' for i in range(single_data.shape[0])]
        
        else:
            # 1) Assign the date
            date = name_to_date_matches[filename]
            single_data['date'] = [date for i in range(single_data.shape[0])]
            
            # 2) Assign 0 to all match event
            single_data['naive_order'] = [0 for i in range(single_data.shape[0])]

            # 3) Group name
            group_name = date_to_name_to_info_matches[date][filename]['group_name']
            single_data['group_name'] = [group_name for i in range(single_data.shape[0])]
   
            # 4) Assign session
            session = date_to_name_to_info_matches[date][filename]['session_name']
            single_data['session'] = [session for i in range(single_data.shape[0])]

            # 5) Assign notes
            notes = date_to_name_to_info_matches[date][filename]['notes']
            single_data['notes'] = [notes for i in range(single_data.shape[0])]

            # 6) Note the source dataset            
            single_data['from'] = ['matches' for i in range(single_data.shape[0])]
        
        # Concatenation
        data_columns_list = list(single_data.columns)
    
        # Check on columns names
        if first:
            all_data = single_data
            data_variables_lists = data_columns_list
            first = False
        else:
            # Check if columns names always the same in time
            if type(data_variables_lists[0]) == list and any([data_columns_list != variables_list for variables_list in data_variables_lists]):
                
                # Annotate different columns lists
                data_variables_lists.append(data_columns_list)
    
            # Concatenation        
            all_data = pd.concat([all_data, single_data])


# Columns trainingn alert
if type(data_variables_lists[0]) == list:
    print('!!! ALERT!!!\nDifferent columns setting in matches dataset:\n', len(data_variables_lists))
else:
    print('\nData loading and concatenation successfully completed!\n')


# Change columns names
all_data = all_data.rename(columns={'Unnamed: 0': "name"})

all_data['T_conversion'] = all_data['T'].map(convert_time_in_seconds)
all_data = all_data.drop(['Unnamed: 30'], axis = 1)

# Series types
dtypes = [str(all_data[col].dtype) for col in all_data.columns]
col_to_dtypes = dict(zip(all_data.columns, dtypes))

numerical_classes = ['int64', 'float64', 'bool']

for k, v in col_to_dtypes.items():
    if v not in numerical_classes:
        all_data[k] = all_data[k].str.lower()

# Unique index 
all_data.index = list(range(all_data.shape[0]))


# REMOVINGS -------------------------------------------------------------------
# 1) Duplicates remove
print('Duplicates founded and deleted:\n{}\n'.format(len(all_data[all_data.duplicated()])))
all_data = all_data.drop_duplicates()


# 2) 0 time removing
print('"O" time row(s) founded and deleted:\n{}\n'.format(len(all_data[all_data['T_conversion'] <= 0])))
all_data = all_data.drop(all_data[all_data['T_conversion'] <= 0].index, axis = 0)


# 3) NaN values
is_NaN = all_data.isnull()
row_has_NaN = is_NaN.any(axis=1)
rows_with_NaN = all_data[row_has_NaN]
print('Rows with "NaN" founded and deleted:\n{}\n'.format(sum(row_has_NaN)))

if sum(row_has_NaN) > 0:
    all_data = all_data.drop(all_data[rows_with_NaN].index)


# 4) Removing 'team average' 
team_averages = all_data[all_data['name'] ==  'team average']
all_data = all_data.drop(team_averages.index)


# 5) Obvious error in distance
distance_error = all_data[all_data['D'] >=  20000]
all_data = all_data.drop(distance_error.index)

# 6) Outlier: Z-scores removing
numerical_cols = [col for col in all_data.columns if (col_to_dtypes[col] in numerical_classes)]

# Assign to all_data the next line to use automatic outlier detection based on p-value
# outlier_removal_by_pvalue(all_data, numerical_cols, p_value = 1.1102230246251565e-16)


# CONVERSIONS -----------------------------------------------------------------
# 1) Rstrip : space in the end
all_data['name'] = all_data['name'].map(str.rstrip)

# 2) Convert date to datetime format
all_data['date'] = [datetime.strptime(i, '%d/%m/%Y') for i in all_data['date']]

# 3) Sort by date first and naive order after and indexing 
all_data = all_data.sort_values(["date", "naive_order"], ascending = (True, True))
all_data.index = list(range(all_data.shape[0]))

# 4) Year sin cosin convertion
timestamp_s = all_data['date'].map(pd.Timestamp.timestamp)

day = 24*60*60
year = (365.2425)*day

all_data['Year sin'] = np.sin(timestamp_s * (2 * np.pi / year))
all_data['Year cos'] = np.cos(timestamp_s * (2 * np.pi / year))

# Plot


# print(set(all_data['name']))
# print(all_data.columns)
plot_value_in_time(player = 'giandonato', value_to_plot = '%Tempo Recupero', alpha = 0.2)


# 5) Friendly match management 
session_col_contain_amichev = all_data['session'].str.contains('amichev')
groupname_col_contain_amichev = all_data['group_name'].str.contains('amichev')
groupname_col_contain_primavera = all_data['group_name'].str.contains('primavera')

# Assign different 'from'
for i in list(all_data[(session_col_contain_amichev) | (groupname_col_contain_amichev) | (groupname_col_contain_primavera)].index): # & condition: what i want to keep (not what i want to drop, it could be confusing!)
    if all_data.iloc[i]['from'] == 'matches':
        
        # .at[index, column] modifies df itself, not a copy
        all_data.at[i, 'from'] = 'matches -> training'

all_data[all_data['from'] == 'matches -> training'][['session', 'group_name']]



# ADDING ----------------------------------------------------------------------
# 1) Pomeriggio 0-1 : fortunately there's no other 'pom' meaning
all_data['pomeriggio'] = [1 if ('pom' in i) else 0 for i in all_data['group_name']]


# 2) Year
all_data['year'] = pd.DatetimeIndex(all_data['date']).year


# FILTERING AND FULL MATCH ASSIGNMENT -----------------------------------------
players = list(set(all_data['name']))
full_match = 'full match'
fm = 'fm'
sostituzioni = 'sostituzioni'

to_retain_cols = ['name','T','date','group_name','from','Year sin','Year cos','pomeriggio','year','order']
to_zero_cols = ['naive_order']
max_cols = ['SMax (kmh)']
session_col = ['session']
notes_col = ['notes']
absolute_sum_cols = ['D','Drel', 'D_SHI','D_AccHI','D_DecHI','D_MPHI','D_S6','D_A8','D_A1','D_MP5','ND_A1','NU_A8','NU_AccHI','ND_DecHI','NU_S6','ND_DecHI.1','D_S4','T_conversion']
time_weighted_av_cols = ['AMP','%Tempo Recupero']
distance_weighted_av_cols = ['%ED','%D_A1','%D_A8','%D_AccHI','%D_DecHI','%D_MPHI','%D_SHI','%AI']


df = pd.DataFrame(all_data.iloc[[1,2]])

def compute_full_match(df):
    df_to_concat = []
    
    for col in df.columns:
        if col in to_retain_cols:
            df_to_concat.append(df.iloc[-1][col])
        elif col in to_zero_cols:
            df_to_concat.append(0)
        elif col in session_col:
            df_to_concat.append('full match')
        elif col in notes_col:
            df_to_concat.append('calculated')
        elif col in max_cols:
            df_to_concat.append(max(df[col])  )     
        elif col in absolute_sum_cols:
            df_to_concat.append(sum(df[col]))
        elif col in time_weighted_av_cols:
            df_to_concat.append(sum(df[col] * df['T_conversion'])/(sum(df['T_conversion'])))
        elif col in distance_weighted_av_cols:
            df_to_concat.append(sum(df[col] * df['D'])/(sum(df['D'])))
        else:
            print(col)
    df_to_concat = pd.DataFrame([df_to_concat], columns = df.columns)
    return df_to_concat


def choose_session(element):
    if type(element) != str:
        res = sorted(list(element))[-1]
    else:
        res = element
    return res


import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')


# For every players
df_to_concat = pd.DataFrame()
indexes_to_remove_from_all_data = []

checkpoint_full_match = all_data
all_data = checkpoint_full_match
presences = 0
empties = 0
concat = 0


print('Assigning matches data')
time.sleep(1)

for player in tqdm(players):
    
    # For every date he appears in filtered 'matches'
    for date in list(set(all_data['date'][(all_data['name'] == player) & (all_data['from'] == 'matches')])):
        index1t, index2t = [], []
        presences += 1
        plr_mtc_dt = (all_data['name']==player) & (all_data['from'] == 'matches') & (all_data['date'] == date)
        not_selected_option = True
        
        # Taking only one of the events starting from selected_option
        
        # 1) FULL MATCH : If he appears in at last one 'full match' of 'fm' or 'sostituzioni' in 'session'
        for selected_option in [full_match, fm, sostituzioni]:
            if (all_data['session'][(plr_mtc_dt)].str.contains(selected_option) == True).any():
                
                # Get the index of every 'selected_option' appearances
                index = list((all_data[(plr_mtc_dt) & (all_data['session'].str.contains(selected_option) == True)]).index)
                
                # If more than one select the last one (It is probably the correct one) remove the other
                index = list(all_data.iloc[index].sort_values(['session']).index)[-1]
                indexes_to_remove = [i for i in all_data[(plr_mtc_dt)].index if (i != index)]
                indexes_to_remove_from_all_data.extend(indexes_to_remove)
                not_selected_option = False
                break
            
        if not_selected_option:  
            
            # 2) 1t - 2t : If he appears in at last one '1t' or '2t' in 'session'
            if ((all_data['session'][(plr_mtc_dt)].str.contains('|'.join(['1t','t1','2t','t2'])) == True).any()):
                
                # Get the index of every '1t' and '2t' appearances
                index1t = list((all_data[(plr_mtc_dt) & (all_data['session'].str.contains('|'.join(['1t','t1'])) == True)]).index)
                index2t = list((all_data[(plr_mtc_dt) & (all_data['session'].str.contains('|'.join(['2t','t2'])) == True)]).index)
                
                # Remove all the indexes in the day
                indexes_to_remove = list(all_data[(plr_mtc_dt)].index)
                indexes_to_remove_from_all_data.extend(indexes_to_remove)
                concat += 1
                
                # Select the last ones if there are (probably the correct one) and assing to index to analize
                indexes_to_analize = []
                for indexxt in [index1t, index2t]:
                    if len(indexxt) > 0:
                        index = list(all_data.iloc[indexxt].sort_values(['session']).index)[-1]
                        indexes_to_analize.extend([index])
    
                if not df_to_concat.empty:
                    df_to_concat = df_to_concat.append(compute_full_match(all_data.iloc[indexes_to_analize]))
                else:
                    df_to_concat = compute_full_match(all_data.iloc[indexes_to_analize])
    
    
            # 6) 15' minutes : fortunately, never matched a duplicate and being residuals there's no need to check for indexes_to_remove
            elif not all_data[(plr_mtc_dt)].empty:
                # print(all_data[(plr_mtc_dt)])
                indexes_to_remove = list(all_data[(plr_mtc_dt)].index)
                indexes_to_remove_from_all_data.extend(indexes_to_remove)
                concat +=1
                if not df_to_concat.empty:
                    df_to_concat = df_to_concat.append(compute_full_match(all_data[(all_data['name']==player) & (all_data['from'] == 'matches') & (all_data['date'] == date)]))
                else:
                    df_to_concat = compute_full_match(all_data[(all_data['name']==player) & (all_data['from'] == 'matches') & (all_data['date'] == date)])
            
            else:
                print(all_data[(all_data['name']==player) & (all_data['from'] == 'matches') & (all_data['date'] == date)])

if all_data[all_data['from'] == 'matches'].shape[0] == presences:
    print('Single data for match assigned!')
else:
    number_of_matches_event_before_concatenation = all_data[all_data['from'] == 'matches'].shape[0]
    len_after = df_to_concat.shape[0] + len([i for i in list(all_data.index) if ( i not in indexes_to_remove_from_all_data)])
    number_of_matches_after_before_concatenation = number_of_matches_event_before_concatenation - len(indexes_to_remove_from_all_data) + df_to_concat.shape[0]
    print('\n   Len before all_data:', all_data.shape[0])
    print('\n   Number of match event after concatenation:', number_of_matches_event_before_concatenation)
    print(' - Invalid indexes detected:',len(indexes_to_remove_from_all_data))
    print(' + Df_to_concat len:',df_to_concat.shape[0])
    print(' = Number of match event after concatenation:', number_of_matches_after_before_concatenation)
    print('   Number of presences:', presences)
    print(' = Differences presences - matches afetr correction:',presences - number_of_matches_after_before_concatenation)


valid_indexes = [i for i in list(all_data.index) if ( i not in indexes_to_remove_from_all_data)]
all_data = all_data.iloc[valid_indexes]
all_data = all_data.append(df_to_concat)

all_data = all_data.sort_values(["date", "naive_order"], ascending = (True, True))
all_data.index = list(range(all_data.shape[0]))

checkpoint_full_match = all_data
all_data = checkpoint_full_match


# REMOVING --------------------------------------------------------------------
# Match error double imputation
index_to_remove = list(all_data[(all_data['date'] == '2017-03-18') & (all_data['from'] == 'trainings')].index)
all_data = all_data.drop(all_data.index[index_to_remove])


# 3) Right order from naive_order ---------------------------------------------
start_time = time.time()

# Default value for order set to 0 (for matches and full trainings)
all_data = all_data.sort_values(["date", "naive_order"], ascending = (True, True))
all_data.index = list(range(all_data.shape[0]))

all_data['order'] = [0 for i in range(all_data.shape[0])]
full_training ='full t'

duplicates_index = []
indexes_to_remove_from_all_data = []
df_to_concat = pd.DataFrame()



# For a single player
for player in players:
    print('\n{}/{}) Player: {}'.format(players.index(player) + 1, len(players), player.upper()))
    time.sleep(1)
    
    # For a date
    for date in tqdm(list(set(all_data['date'][all_data['name']==player]))):
        
        # Player in the Date in the Morning and Afternoon (as not Morning)
        morning_player_df = all_data.loc[(all_data['name']==player) & (all_data['date']==date) & (all_data['pomeriggio']==0)]
        afternoon_player_df = all_data.loc[(all_data['name']==player) & (all_data['date']==date) & (~(all_data['pomeriggio']==0))]

        for morning_or_afternoon_df in [morning_player_df, afternoon_player_df]:
            
            # 1)   SKIP MATCHES (all zeros)
            if morning_or_afternoon_df['from'].str.contains('matches').any():
                continue
            
            
            # 2)   Friendly conditions ---------------------------------------------
            f0 = morning_or_afternoon_df['group_name'].str.contains('olbia')
            f1 = morning_or_afternoon_df['group_name'].str.contains('amich')
            f2 = morning_or_afternoon_df['group_name'].str.contains('triang')
            f3 = morning_or_afternoon_df['session'].str.contains('amich')
            friendly_conditions = (f0) | (f1) | (f2) | (f3)
            
            # If there are friendly matches
            if friendly_conditions.any():
                friendly =  morning_or_afternoon_df[friendly_conditions]
                not_selected_option = True
                

                    
                # 2.1) FULL MATCH : If he appears in at last one 'full match' of 'fm' or 'sostituzioni' in 'session'
                for selected_option in [full_match, fm, sostituzioni]:
                    if (friendly['session'].str.contains(selected_option) == True).any():
                        
                        # Get the index of every 'selected_option' appearances
                        # index = list((friendly['session'].str.contains(selected_option)).index)
                        
                        # If more than one select the last one (It is probably the correct one) remove the other
                        index = list(friendly.sort_values(['session']).index)[-1]
                        indexes_to_remove = [i for i in friendly.index if (i != index)]
                        indexes_to_remove_from_all_data.extend(indexes_to_remove)
                        not_selected_option = False
                        break
                    
                if not_selected_option:  
                    
                    # 2.2) 1t - 2t : If he appears in at last one '1t' or '2t' in 'session'
                    if ((friendly['session'].str.contains('|'.join(['1t','t1','2t','t2'])) == True).any()):
                        
                        # Get the index of every '1t' and '2t' appearances
                        index1t = list(((friendly['session'].str.contains('|'.join(['1t','t1'])) == True)).index)
                        index2t = list(((friendly['session'].str.contains('|'.join(['2t','t2'])) == True)).index)
                        
                        # Remove all the indexes in the day
                        indexes_to_remove = list(friendly.index)
                        indexes_to_remove_from_all_data.extend(indexes_to_remove)
                        concat += 1
                        
                        # Select the last ones if there are (probably the correct one) and assing to index to analize
                        indexes_to_analize = []
                        for indexxt in [index1t, index2t]:
                            if len(indexxt) > 0:
                                index = list(all_data.iloc[indexxt].sort_values(['session']).index)[-1]
                                indexes_to_analize.extend([index])
            
                        if not df_to_concat.empty:
                            df_to_concat = df_to_concat.append(compute_full_match(all_data.iloc[indexes_to_analize]))
                        else:
                            df_to_concat = compute_full_match(all_data.iloc[indexes_to_analize])
            
            
                    # 2.3) 15' minutes : fortunately, never matched a duplicate and being residuals there's no need to check for indexes_to_remove
                    elif not friendly.empty:
                        # print(all_data[(plr_mtc_dt)])
                        indexes_to_remove = list(friendly.index)
                        indexes_to_remove_from_all_data.extend(indexes_to_remove)
                        concat +=1
                        if not df_to_concat.empty:
                            df_to_concat = df_to_concat.append(compute_full_match(friendly))
                        else:
                            df_to_concat = compute_full_match(friendly)        
            
            # 3)   Training with friendly exclusion
            morning_or_afternoon_df = morning_or_afternoon_df[~friendly_conditions]
            full_training_condition = (morning_or_afternoon_df['session'].str.contains(full_training) == True)
            if morning_or_afternoon_df.shape[0] > 1:
                
                # 3.1) If we have more than one 'full training' we take the last
                if morning_or_afternoon_df[morning_or_afternoon_df['session'].str.contains(full_training) == True].shape[0] > 1:
                    
                    
                    last_full_training_session = sorted(list(morning_or_afternoon_df[full_training_condition]['session']))[-1]
                    
                    # Select the Distance
                    full_training_duration = morning_or_afternoon_df[morning_or_afternoon_df['session'] == last_full_training_session]['D']
                    
                    # Indexes to drop because duplicates
                    indexes_to_drop = sorted(list(morning_or_afternoon_df[morning_or_afternoon_df['session'].str.contains(full_training) == True].index))[:-1]
                    duplicates_index.extend(indexes_to_drop)
                    
                    # 3.2) If we have more session with the same session name we select by group name too and take the last
                    if full_training_duration.shape[0] > 1:
                        last_full_training_group = sorted(list(morning_or_afternoon_df[morning_or_afternoon_df['session']== last_full_training_session]['group_name']))[-1]
                        full_training_duration = morning_or_afternoon_df[(morning_or_afternoon_df['session']== last_full_training_session) & (morning_or_afternoon_df['group_name']== last_full_training_group)]['D']
            
                        indexes_to_drop = sorted(list(morning_or_afternoon_df[(morning_or_afternoon_df['session']== last_full_training_session) & (~(morning_or_afternoon_df['group_name']== last_full_training_group))].index))
                        duplicates_index.extend(indexes_to_drop)

                duplices_condition = morning_or_afternoon_df['session'].index.isin(duplicates_index)                                                                                                                             
                training_player_df = morning_or_afternoon_df[(~full_training_condition) & (~duplices_condition)].sort_values(["naive_order"], ascending = (True))                
                
                # Assign right order
                all_data.at[training_player_df.index, 'order'] = [i+1 for i in range(training_player_df.shape[0])]
            
            else:
                if morning_or_afternoon_df.shape[0] == 1:       
                    if not morning_or_afternoon_df['session'].str.contains(full_training).any() :
                        all_data.at[morning_or_afternoon_df.index, 'order'] = 1

all_data[all_data['name'] == 'brignani']

# Time computing
end_time = time.time()
delta_time = end_time - start_time
hours = int(delta_time/3600)
minutes = int((delta_time - (hours*3600))/60)
seconds = round(delta_time - (hours*3600) - minutes*60)
print("\nTime to execute the right \'order\' imputation:\n{}:{}:{}".format(hours, minutes, seconds))        

# VERIFICATO FIN QUI ----------------------------------------------------------

# 4) Distance from match
# From the last to the first
all_data = all_data.sort_values(["date"], ascending = (False))

tmp = []
final_series = []
days = 1
old_date = all_data.iloc[0]['date']

print('Assigning the distance from the match')
time.sleep(1)

for i in tqdm(range(all_data.shape[0])):
    new_date = all_data.iloc[i]['date']
    
    if all_data.iloc[i]['from'] != 'matches' and new_date != old_date:
        final_series.extend(tmp)
        days += 1
        tmp = [days]
        old_date = new_date
        
    elif all_data.iloc[i]['from'] != 'matches' and new_date == old_date:
        tmp.append(days)
        
    elif all_data.iloc[i]['from'] == 'matches' and new_date != old_date:
        final_series.extend(tmp)
        days = 0
        tmp = [0]
        old_date = new_date
        
    else:
        tmp.append(days)
        
final_series.extend(tmp)


if len(final_series) != all_data.shape[0]:
    print('ATTENTION!!!\nLenght mismatching in distance from match')
        
all_data['distance_from_match'] = final_series


# Checkpoint ------------------------------------------------------------------
print('Copy saved as "all_data_copy"')
all_data_copy = all_data

# Some statistics -------------------------------------------------------------
print(all_data.describe().transpose())


# Dicts
players_name = set(list(all_data['name']))
stats_names_to_first_and_last_match_date = {}
never_palyer = 0

for player in players_name:
    stats_names_to_first_and_last_match_date[player] = {}
    dates = list(all_data[(all_data['name'] == player) & (all_data['from'] == 'matches')]['date'])
    if len(dates) > 0:
        stats_names_to_first_and_last_match_date[player]['first'] = dates[0]
        stats_names_to_first_and_last_match_date[player]['last'] = dates[-1]
    else:
        never_palyer +=1


stats_to_instats_names = config_file['stats_to_instats_names']

config_filename_1 = 'C:\\Users\\vince\\Desktop\\Contrader\\Calcio\\Olbia\\config\\stats_to_instats_names.pkl'
a_file = open(config_filename_1, "wb")
pickle.dump(stats_to_instats_names, a_file)
a_file.close()

stats_names_to_first_and_last_match_date
config_filename_2 = 'C:\\Users\\vince\\Desktop\\Contrader\\Calcio\\Olbia\\config\\stats_names_to_first_and_last_match_date.pkl'
a_file = open(config_filename_2, "wb")
pickle.dump(stats_names_to_first_and_last_match_date, a_file)
a_file.close()

                



# Importing INSTAT ------------------------------------------------------------
instat_path = config_file['paths']['instat_matches']
all_instat_paths = [join(instat_path, f) for f in listdir(instat_path) if isfile(join(instat_path, f))]

all_players_till_the_date = 'instat_all_players_matches_till_the_date'

if len(all_instat_paths) > 1:
    all_instat_paths = [path  for path in all_instat_paths if (path[len(instat_path)+12:-5] == all_players_till_the_date)]

instat_data = pd.read_excel(all_instat_paths[0])
instat_data.index = [('-'+str(i))  for i in range(instat_data.shape[0])]

# Changing the names of instat
instat_to_stats = {v:k for k,v in stats_to_instats_names.items()}
instat_data['name'] = [instat_to_stats[i]  if (i in list(instat_to_stats.keys())) else i for i in instat_data['name']]


# DIFFERENCES -----------------------------------------------------------------
# Names
names_instat_not_stats = set(instat_data['name']).difference(set(all_data['name']))
names_stats_not_instat = set(all_data['name']).difference(set(instat_data['name']))

print('\nPlayers in instat but not in trainings (strange!):\n{}'.format(names_instat_not_stats))
print('\nPlayers in stats but not in instat (probably they never played):\n{}'.format(names_stats_not_instat))

# Removing player that are in instat but not in stats
instat_data = instat_data[~(instat_data['name'].isin(list(names_instat_not_stats)))]


# Dates in common
date_in_common = list(set(all_data['date']).intersection(set(instat_data['Date'])))
print('\nDates in common found (there are some of players against the team):\n{}'.format(len(date_in_common)))


# Filtering by date in common and session as 'full match'
all_data_date_in_common = all_data.loc[(all_data['date'].isin(date_in_common)) & (all_data['session'] == 'full match') & (~session_col_contain_amichev) & (~groupname_col_contain_amichev)]


# Two list to record the differences
missing_instat_match_data = []
missing_stats_match_data = []


somma = 0
missing = 0
# Assign the stats index to instat -------------------------------------------
instat_index_as_list = instat_data.index.tolist()

for date in date_in_common:
    
    # Reduce for the day in common
    in_the_day_stats = all_data_date_in_common[all_data_date_in_common['date'] == date]
    
    # Selecting a player in the day
    for name in in_the_day_stats['name']:
        
        # Check if in instat
        if name in list(instat_data[instat_data['Date'] == date]['name']):
            somma += 1
            
            # Taking the index i want  to set
            index_from_stats = in_the_day_stats[in_the_day_stats['name'] == name].index.tolist()[0]
            
            # Assign to instat
            index_to_change_in_instat = instat_data.loc[(instat_data['Date'] == date) & (instat_data['name'] == name)].index.tolist()[0]
            idx = instat_index_as_list.index(index_to_change_in_instat)
            instat_index_as_list[idx] = index_from_stats
            
            instat_data.index = instat_index_as_list
            
        else:
            missing += 1
            missing_instat_match_data.append([date,name])

# print('missing :',missing)
# print('somma :',somma)
# print(instat_data[(instat_data['Date'] == date) & (instat_data['name'] == name)])


# Instat to join based on index -----------------------------------------------
instat_to_join = instat_data.loc[(instat_data.index.isin(list(all_data_date_in_common.index)))]
instat_to_join['Instat_data_presence'] = [1 for i in range(instat_to_join.shape[0])]

instat_columns_to_retain = [col for col in instat_to_join.columns if (col not in all_data.columns)]
other_cols_to_remove = ['Date','Date.1','InStat Index','Opponent']
instat_columns_to_retain = [col for col in instat_columns_to_retain if (col not in other_cols_to_remove)]

instat_to_join = instat_to_join[instat_columns_to_retain]


# Instat not in stats (potrebbero esserci ex giocatori in altre squadre: non affidabile)
instat_not_in_stats = instat_data.loc[~(instat_data.index.isin(list(all_data_date_in_common.index)))]


# Instat missing date (checkend last 4 on instat: right) ----------------------
in_stats_not_in_instat = []

for i in range(len(missing_instat_match_data)):
    single = all_data_date_in_common[(all_data_date_in_common['date'] == missing_instat_match_data[i][0]) & (all_data_date_in_common['name'] == missing_instat_match_data[i][1])]
    if type(in_stats_not_in_instat) != list:
        in_stats_not_in_instat = pd.concat([single,in_stats_not_in_instat])
    else:
        in_stats_not_in_instat = single

in_stats_not_in_instat = in_stats_not_in_instat[in_stats_not_in_instat['distance_from_match'] == 0]
instat_missing_date = set(in_stats_not_in_instat['date'])
print('Missin dates in instat where "distance_from_the_match" = 0:\n{}'.format(len(instat_missing_date)))


# JOIN ------------------------------------------------------------------------
df = all_data.join(instat_to_join)
path_to_joined =  config_file['paths']['joined']
df.to_excel(path_to_joined)
