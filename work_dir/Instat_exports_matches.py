import os
from os import listdir, chdir

chdir('..\\')
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from os.path import isfile, join
import time
from datetime import datetime, date
from tqdm import tqdm
import pandas as pd
import json
import pickle
from work_dir.utils.bot_functions import an_year_later_one_day_left, right_format_date_imputation
from work_dir.utils.bot_instat_functions  import download_instat_matches_for_all_players_in_period

file = open(".\\config.json")
config_file = json.load(file)
file.close

# Info first and last match for every player from Stats
stats_match_path = config_file['paths']['matches']
matches = [f for f in listdir(stats_match_path) if isfile(join(stats_match_path, f))]

if len(matches) > 1:
    players_first_last_match_downloaded = {}
    for i in matches:
        match_date = datetime.strptime(i[:10], '%Y_%m_%d')
        a_match_day = pd.read_csv(join(stats_match_path, i), sep = ";",  decimal=",")
        names = list(a_match_day[a_match_day.columns[0]])
        for name in names:
            name = name.lower()
            if name not in list(players_first_last_match_downloaded.keys()):
                players_first_last_match_downloaded[str(name)] = {'max':match_date,
                                                           'min':match_date}
            else:
                if players_first_last_match_downloaded[str(name)]['max'] < match_date:
                    players_first_last_match_downloaded[str(name)]['max'] = match_date
                if players_first_last_match_downloaded[str(name)]['min'] > match_date:
                    players_first_last_match_downloaded[str(name)]['min'] = match_date


file = open(".\\config.json")
config_file = json.load(file)
file.close

downloads_path = config_file['paths']['instat_matches']

# Sleep time per il ciclo
sleeptime = 1
script_start = time.time()
data_aggregation_name = config_file['default_names']['data_aggregation_name']

# Controllo quali siano i file già presenti nella cartella di destianzione
file_already_downloaded = [
    f[:-5] for f in listdir(downloads_path) if isfile(join(downloads_path, f))]


# Se è già presente il file data_aggregation_name ne ricaviamo la data di partenza
if len(file_already_downloaded) == 1:
    if file_already_downloaded[0][11:] == data_aggregation_name:
        year = file_already_downloaded[0][:4]
        month = file_already_downloaded[0][5:7]
        day = file_already_downloaded[0][8:10]

        start_date = day + '.' + month + '.' + year
else:
    start_date = None

# Ciclo per le stagioni -------------------------------------------------------
today = str(date.today().day) + '.' + str(date.today().month) + \
    '.' + str(date.today().year)
today_datetime_format = datetime.today()


if not start_date:
    # Ciclo per stagionai dal 15 Agosto 20XX al 14 Agosto 20XX + 1
    # Selenium non riesce ad accedere a tutti i giocatori contemporaneamente
    # Ad ogni stagione individuo i suoi calciatori e scarico l'intera carriera
    # Memorizzo il calciatore per ignorarlo nelle stagioni successive
    
    starting_date = "15.08.2015"
    ending_date = an_year_later_one_day_left(starting_date)
    ending_date_datetime_format = datetime.strptime(ending_date, '%d.%m.%Y')

    player_processed = []

    while ending_date_datetime_format < today_datetime_format:
        player_processed = download_instat_matches_for_all_players_in_period(
            starting_date = starting_date, ending_date = ending_date,
            config_file = config_file, first_and_last = players_first_last_match_downloaded,
            processed_player_list = player_processed
            )
        
        print('\nDonwload completed for the period:\n{}  -  {}\n'.format(starting_date, ending_date))
        print(player_processed)

        # Update
        starting_date = starting_date[:-4] + str(int(starting_date[-4:])+1)
        ending_date = an_year_later_one_day_left(starting_date)
        ending_date_datetime_format = datetime.strptime(
            ending_date, '%d.%m.%Y')

    player_processed = download_instat_matches_for_all_players_in_period(
        starting_date = starting_date, ending_date = ending_date,
        config_file = config_file, first_and_last = players_first_last_match_downloaded,
        processed_player_list = player_processed
        )

else:
    player_processed = download_instat_matches_for_all_players_in_period(
        starting_date = start_date, ending_date = today,
        config_file = config_file, first_and_last = players_first_last_match_downloaded,
        processed_player_list = player_processed
        )


# driver.quit()
print('\nDonwload completed!\nGood job asshole...')

#for i in all_files_paths:
#    if '(1)' in i:
#        os.remove(i)
        
# NOT AGGREGATED : Saving last saved match -----------------------------------------------------
def player_from_filename(filename):
    return filename[25:-5]

def last_date_from_list(a_list):
    res = datetime.strptime( '01/01/2000', '%d/%m/%Y')
    for i in a_list:
        i = str(i)
        if len(i) == 5: # 01/01
            tmp = datetime.strptime( i+'/2022', '%d/%m/%Y')
        elif len(i) == 8: # 01/01/01
            tmp = datetime.strptime( i, '%d/%m/%y')
        if tmp > res:
            res = tmp
    res =  str(res)[8:10]+'.'+ str(res)[5:7] +'.'+ str(res)[:4]
    return res


# NOT AGGREGATED : 'player_to_last_instat_match'
player_to_last_instat_match = {}

all_files_paths = [join(downloads_path, f) for f in listdir(
    downloads_path) if isfile(join(downloads_path, f))]

data_aggregation_name = config_file['default_names']['data_aggregation_name']
data_aggregation_name_full_path = join(downloads_path, data_aggregation_name)
data_aggregation_name_presence = isfile(data_aggregation_name_full_path)

if data_aggregation_name_presence:
    all_files_paths.remove(data_aggregation_name_full_path)


for i in all_files_paths:
    player = player_from_filename(i)
    single_data = pd.read_excel(i)
    last_match = last_date_from_list(list(single_data['Date']))
    player_to_last_instat_match[player] = last_match
    

# NOT AGGREGATED : update if existing 'player_to_last_instat_match'
player_to_last_instat_match_path = config_file['paths']['player_to_last_instat_match']
base_path = os.getcwd()

if isfile(join(base_path, player_to_last_instat_match_path[1])):
    with open(player_to_last_instat_match_path, 'rb') as handle:
        old_dict = pickle.load(handle)
        old_dict.update(player_to_last_instat_match)
        player_to_last_instat_match = old_dict
else:              
    with open(player_to_last_instat_match_path, "wb") as handle:
        pickle.dump(player_to_last_instat_match, handle)


# NOT AGGREGATED : Concatenating values ---------------------------------------
first = True
all_new_data = []

print('Files concatenation...')
for complete_file_path in tqdm(all_files_paths):

    # Get the filename
    file_extension = -5
    filename = complete_file_path[len(downloads_path)+1:file_extension]
    single_data = pd.read_excel(complete_file_path)
    player_name = filename[11:]
    single_data['name'] = [player_name for i in range(single_data.shape[0])]
    
    if first:
        all_new_data = single_data
        first = False
    else:
        all_new_data = pd.concat([all_new_data, single_data])

all_new_data.index = [i for i in range(all_new_data.shape[0])]


# AGGREGATED : REMOVAL ---------------------------------------------------------------------
# Nan removing that correspond to the 'total' row for each excel
is_NaN = all_new_data.isnull()
row_has_NaN = is_NaN.any(axis=1)
rows_with_NaN = all_new_data[row_has_NaN]
print('Rows with "NaN" found and deleted:\n{}\n'.format(sum(row_has_NaN)))
all_new_data = all_new_data.drop(all_new_data[row_has_NaN].index)


# MODIFICATION ----------------------------------------------------------------
all_new_data['Date'] = all_new_data['Date'].map(right_format_date_imputation)

# sorting for date
all_new_data.index = all_new_data['Date'].apply(
    lambda x: datetime.strptime(x, '%d/%m/%Y'))
all_new_data = all_new_data.sort_index(ascending=False)

all_new_data_most_recent_date = list(all_new_data.index)[0]
all_new_data_most_recent_date = str(all_new_data_most_recent_date.year) + '_' + str(
    all_new_data_most_recent_date.month) + '_' + str(all_new_data_most_recent_date.day)

# Columns name
all_new_data = all_new_data.rename(columns={'Unnamed: 1': 'home'})

# Udoh's name
paul_akpan_udoh = all_new_data['name'] == 'Paul Akpan Udoh'
all_new_data['name'][paul_akpan_udoh] = 'King Udoh'

# Substitution
not_numeric_cols = ['Date', 'home', 'Opponent',
                    'Score', 'InStat Index', 'Position', 'name']
numeric_cols = [i for i in all_new_data.columns if (i not in not_numeric_cols)]

for col in all_new_data.columns:
    all_new_data[col] = all_new_data[col].replace(
        '-', '0').replace("%", '', regex=True)
    if col in numeric_cols:
        all_new_data[col] = pd.to_numeric(all_new_data[col])

    
# FULL AGGREGATED : Check older one and concatenate it ------------------------
if data_aggregation_name_presence:
    old_data = pd.read_excel(data_aggregation_name_full_path)
    all_new_data = pd.concat([all_new_data, old_data])


# SAVING ----------------------------------------------------------------------
# Create the name for storing
data_aggregation_name_complete_path = downloads_path + '\\' + \
    all_new_data_most_recent_date+' '+data_aggregation_name+'.xlsx'

all_new_data.to_excel(data_aggregation_name_complete_path)

# REMOVING OLD DATA -----------------------------------------------------------
for i in all_files_paths:
    os.remove(i)
        