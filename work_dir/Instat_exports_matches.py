from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import isfile, join
import time
from IPython import get_ipython
from datetime import date
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import json
from work_dir.utils.bot_functions import clearConsole, download_wait, select_new_tab, wait_and_try_to_find_loop, an_year_later_one_day_left, right_format_date_imputation

file = open(".\\config.json")
config_file = json.load(file)
file.close

# Info first and last match for every player
stats_match_path = config_file['paths']['matches']
matches = [f for f in listdir(stats_match_path) if isfile(join(stats_match_path, f))]

players_to_first_and_last_match = {}
for i in matches:
    date = datetime.strptime(i[:10], '%Y_%m_%d')
    a_match_day = pd.read_csv(join(stats_match_path, i), sep = ";",  decimal=",")
    names = list(a_match_day[a_match_day.columns[0]])
    for name in names:
        name = name.lower()
        if name not in list(players_to_first_and_last_match.keys()):
            players_to_first_and_last_match[str(name)] = {'max':date,
                                                       'min':date}
        else:
            if players_to_first_and_last_match[str(name)]['max'] < date:
                players_to_first_and_last_match[str(name)]['max'] = date
            if players_to_first_and_last_match[str(name)]['min'] > date:
                players_to_first_and_last_match[str(name)]['min'] = date


file = open(".\\config.json")
config_file = json.load(file)
file.close

chromedriver = config_file['paths']['chromedriver']
downloads_path = config_file['paths']['instat_matches']

# Sleep time per il ciclo
sleeptime = 1
script_start = time.time()
all_players_till_the_date = 'instat_all_players_matches_till_the_date'

# Controllo quali siano i file già presenti nella cartella di destianzione
file_already_downloaded = [
    f[:-5] for f in listdir(downloads_path) if isfile(join(downloads_path, f))]


# Se è già presente il file all_players_till_the_date ne ricaviamo la data di partenza
if len(file_already_downloaded) == 1:
    if file_already_downloaded[0][11:] == all_players_till_the_date:
        year = file_already_downloaded[0][:4]
        month = file_already_downloaded[0][5:7]
        day = file_already_downloaded[0][8:10]

        start_date = day + '.' + month + '.' + year
else:
    start_date = None

clearConsole()


def download_instat_matches_for_all_players_in_period(starting_date, ending_date, processed_player_list=[], config_file=config_file, first_and_last = players_to_first_and_last_match):
    user = config_file['credentials']['instat_user']
    pw = config_file['credentials']['instat_password']
    reference_team = config_file['credentials']['reference_team']
    stats_to_instats_names = config_file['stats_to_instats_names']
    instat_to_stats_names = {v:k for k, v in stats_to_instats_names.items()}

   # Setto il webdriver
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': downloads_path}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
    driver.maximize_window()

    # settiamo l'attesa massima
    sleep_time = 30
    wait = WebDriverWait(driver, sleep_time)

    # Setto il sito di partenza
    driver.get("https://football.instatscout.com/login")

    # Cerco la barra per l'username
    xpath = '/html/body/div[3]/div/article/div/div[1]/div/div/form/div[1]/div[1]/div/input'
    username_bar = wait.until(
        EC.presence_of_element_located((By.XPATH, xpath)))
    username_bar.send_keys(user)

    # Cerco la barra per la password e 'invio'
    xpath = '/html/body/div[3]/div/article/div/div[1]/div/div/form/div[1]/div[2]/div/input'
    pw_bar = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    pw_bar.send_keys(pw)
    pw_bar.send_keys(Keys.RETURN)

    # Scrivo il nome nella search bar
    xpath = "/html/body/div[3]/div/div[2]/div/div[1]/div[1]/div/form/input"
    search_bar = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    search_bar.send_keys(reference_team)

    # Le possibile opzioni dalla finestra a tendina dopo la digitazione del nome seleziono reference team
    xpath = "/html/body/div[3]/div/div[2]/div/div[1]/div[1]/div/div/div/div[2]/ul"
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    number_possible_options = len(driver.find_elements(By.XPATH, xpath))
    opened_tabs_before_olbia_selection = driver.window_handles

    for i in range(1, number_possible_options+1):
        xpath = "/html/body/div[3]/div/div[2]/div/div[1]/div[1]/div/div/div/div[2]/ul/li[{}]/a/span[1]".format(
            i)
        team = wait.until(
            EC.presence_of_element_located((By.XPATH, xpath))).text
        if team == reference_team:
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            break

    # Team: Prendo nota delle tab aperte e della nuova
    opened_tabs_after_olbia_selection = driver.window_handles
    players_tab = select_new_tab(
        opened_tabs_after_olbia_selection, opened_tabs_before_olbia_selection)

    # Team: Cancello le pagine precedenti
    if len(opened_tabs_before_olbia_selection) > 1:
        for i in opened_tabs_before_olbia_selection:
            driver.switch_to.window(i)
            driver.close()
    else:
        driver.switch_to.window(opened_tabs_before_olbia_selection[0]).close()

    # Team: Mi sposto sull'ultima delle pagine aperte
    driver.switch_to.window(players_tab)

    # Team: Mi sposto su 'PLAYERS'
    class_name = '#root > div > article > div > ul > li:nth-child(3) > a'
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, class_name))).click()
    print('Wait : this operation may need some times\n')

    # The downloading function
    readable_season = starting_date[-4:] + '/' + ending_date[-2:]

    # Team: Mi sposto su 'Current season'
    xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/span/span[2]'
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    # Team: Mi sposto su 'Advanced selection of matches'
    xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/div/ul/li[6]/span'
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    # Team: Deseleziono la stagione corrente
    xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div'
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    # Team: Attivo il flag 'Dates'
    xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div'
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    # Team: Inserisco la data dei primi dati disponibili dei gps
    xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]/div/input'
    from_date = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    from_date.send_keys(Keys.CONTROL, 'a')
    from_date.send_keys(Keys.BACKSPACE)
    from_date.send_keys(starting_date)

    # Team: Fino ad oggi
    xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/input'
    to_date = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    to_date.send_keys(Keys.CONTROL, 'a')
    to_date.send_keys(Keys.BACKSPACE)
    to_date.send_keys(ending_date)

    # Team: 'OK'
    time.sleep(5)
    css_name = '#root > div > article > section.player-details > div > div > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.advanced-select > div > div.advanced-select__footer > button'
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_name))).click()
    time.sleep(15)

    # Team: Seleziono la griglia intera dei giocatori
    css_name = '#root > div > article > section.player-details > div > div > div.table-scroll-inner > div.team-stats-wrapper > table > tbody'
    parent = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, css_name)))

    # Conto i "figli" con tag name "tr"
    number_of_elements = len(parent.find_elements_by_tag_name("tr"))
    if number_of_elements < 30:
        time.sleep(15)
        parent = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, css_name)))
        number_of_elements = len(parent.find_elements_by_tag_name("tr"))

    player_names = []
    for i in range(number_of_elements):
        xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[2]/table/tbody/tr[{}]/td[1]/div/div[3]/a'.format(
            i+1)
        player_names.append(wait.until(
            EC.presence_of_element_located((By.XPATH, xpath))).text)

    print('({}) Players found in the period: {}'.format(
        readable_season, number_of_elements))
    print('1) {}\n    ...\n{}) {}\n'.format(
        player_names[0], number_of_elements, player_names[-1]))
    print('')

    # Dato che combina un casino con l'apertura delle nuove tab
    opened_tabs_before_player_selection = driver.window_handles
    player_processed = processed_player_list

    # Ciclo per i giocatori -------------------------------------------------------
    for i in range(1, number_of_elements+1):

        if player_processed and (player_names[i-1] in player_processed):
            print("({}) {}'s career yet downloaded".format(
                readable_season, player_names[i-1]))
            continue
        
        try:
            player_name_instat = instat_to_stats_names[str(player_names[i-1])]
            players_to_first_and_last_match[player_name_instat]
            never_played = False
        except:
            never_played = True
        
        if never_played:
            print(f'{player_names[i-1]} never played')
            continue

        # Giocatore: Seleziono il giocatore
        try:
            time.sleep(10)
            xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[2]/table/tbody/tr[{}]/td[1]/div/div[3]/a'.format(
                i)
            wait.until(EC.presence_of_element_located(
                (By.XPATH, xpath))).click()
            print('Player selected:\n{}/{}) {}\n'.format(i,
                  number_of_elements, player_names[i-1]))

        except:
            class_name = '#root > div > article > section.player-details > div > div > div.table-scroll-inner > div.team-stats-wrapper > table > tbody > tr:nth-child({}) > td.match-table__body-cell.with-border > div > div.match-table__body-cell.match-table__player-name > a'.format(
                i)
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, class_name))).click()
            if len(driver.window_handles) != 2:
                print("ATTENTION!\nDidn't open the tab")
            print('{}/{}) {}'.format(i, number_of_elements, player_names[i-1]))
        


        # Giocatore: Mi sposto nell'ultima tab aperta
        opened_tabs_after_player_selection = driver.window_handles
        player_tab = select_new_tab(
            opened_tabs_after_player_selection, opened_tabs_before_player_selection)
        driver.switch_to.window(player_tab)

        # Mi sposto in 'matches'
        try:
            class_name = '#root > div > article > div > ul > li:nth-child(2)'
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, class_name))).click()
            print('({}) : 1/5 MATCHES'.format(readable_season))
        except:
            xpath = '/html/body/div[3]/div/article/div/ul/li[2]'
            time.sleep(5)
            wait_and_try_to_find_loop(wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath)))).click()
            # print('1/5 MATCHES')

        # Clicco su 'Current season'
        try:
            class_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.sc-kGXeez.eJhxTi > div > span > span.styled__Caret-sc-1dwxsrr-3.cxNuZB'
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, class_name))).click()
            print('({}) : 2/5 Current season '.format(readable_season))
        except:
            xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/span'
            time.sleep(5)
            wait_and_try_to_find_loop(wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath)))).click()
            print('2/5 Current season')

        # Clicco 'Advanced ...'
        try:
            class_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.sc-kGXeez.eJhxTi > div > div > ul > li:nth-child(6) > span'
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, class_name))).click()
            print('({}) : 3/5 CSS: Advanced selection of matches '.format(readable_season))
        except:
            xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/div/ul/li[6]/span'
            wait_and_try_to_find_loop(wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath)))).click()
            print('3/5 XPATH: Advanced selection of matches')

        # Team: Attivo il flag 'Dates'
        xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div'
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

        # Team: Inserisco la data dei primi dati disponibili dei gps
        time.sleep(3)
        
        # From
        try:
            css_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.advanced-select > div > div.advanced-select__content > div.advanced-select__filters > div.advanced-select__filters-column-season > div.sc-dVNXKj.kydHHv > div:nth-child(1) > div.react-datepicker-wrapper > div > input'
            from_date = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_name)))
        except:
            css_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.advanced-select > div > div.advanced-select__content > div.advanced-select__filters > div.advanced-select__filters-column-season > div.sc-eoZuQF.iVCbog > div:nth-child(1) > div.react-datepicker-wrapper > div > input'
            from_date = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_name)))

        from_date.send_keys(Keys.CONTROL, 'a')
        from_date.send_keys(Keys.BACKSPACE)
        player_name_instat = instat_to_stats_names[str(player_names[i-1])]

                
        from_date.send_keys(starting_date_player)
 
        # To
        time.sleep(3)
        css_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.advanced-select > div > div.advanced-select__content > div.advanced-select__filters > div.advanced-select__filters-column-season > div.sc-eoZuQF.iVCbog > div:nth-child(2) > div.react-datepicker-wrapper > div > input'
        to_date = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, css_name)))
        to_date.send_keys(Keys.CONTROL, 'a')
        to_date.send_keys(Keys.BACKSPACE)
        ending_date_player = players_to_first_and_last_match[player_name_instat]['max']
        to_date.send_keys(ending_date_player)
        time.sleep(10)

        # Premo il bottone "OK"
        try:
            class_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.advanced-select > div > div.advanced-select__footer > button'
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, class_name))).click()
            print('({}) : 4/5 "OK" button'.format(readable_season))
        except:

            # Il bottone è opaco nel caso non ci sono match selezionati per il periodo e non può essere premuto
            # print('({}) : 4/5 Matches not founded!'.format(readable_season))
            # print('({}) : 5/5 Skipped!\n'.format(readable_season))
            driver.close()
            driver.switch_to.window(players_tab)
            continue

        # Controllo il numero di partite selezionate
        xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/span'
        text = wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath))).get_attribute('innerHTML')
        text = text.replace('<span class="T9n__Text-sc-oyt3bv-0 iekKGO">Selected matches</span>: ',
                            '').replace('<span class="styled__Caret-sc-1dwxsrr-3 cxNuZB"></span>', '')
        # print('({}) : 5/5 Founded {} matches'.format(readable_season, number_of_matches))
        time.sleep(5)

        len_before = len([f for f in listdir(downloads_path)
                         if isfile(join(downloads_path, f))])

        # Premo il formato XLS e scarico
        # css_selector = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.sc-kzSDHa.hKSUKH > a:nth-child(1)'
        css_selector = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.sc-itBpjh.drAlwl > a:nth-child(1)'
        xls_element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, css_selector)))
        xls_element.click()

        downloaded = download_wait(downloads_path, len_before, 30)
        player_processed.append(player_names[i-1])

        if not downloaded:
            print('Trying to download it again...')
            xls_element.click()
            downloaded = download_wait(downloads_path, len_before, 15)

        if downloaded:
            print("({}) {}\'s career downloaded successfully!\n".format(
                readable_season, player_names[i-1]))
        else:
            print('DIOCANE DIOCANE DIOCANE DIOCANE DIOCANE DIOCANE')
            player_processed = player_processed[:-1]

        # Posso chiudere questa tab e spostarmi su quella di partenza
        driver.close()
        driver.switch_to.window(players_tab)

    driver.quit()
    return player_processed


# Ciclo per le stagioni -------------------------------------------------------
today = str(date.today().day) + '.' + str(date.today().month) + \
    '.' + str(date.today().year)
today_datetime_format = datetime.today()


if not start_date:
    # Ciclo per stagionai dal 15 Agosto 20XX al 14 Agosto 20XX + 1
    starting_date = "15.08.2015"
    ending_date = an_year_later_one_day_left(starting_date)
    ending_date_datetime_format = datetime.strptime(ending_date, '%d.%m.%Y')

    player_processed = []

    while ending_date_datetime_format < today_datetime_format:
        player_processed = download_instat_matches_for_all_players_in_period(
            starting_date, today, player_processed)
        print('\nDonwload completed for the period:\n{}  -  {}\n'.format(starting_date, ending_date))

        # Update
        starting_date = starting_date[:-4] + str(int(starting_date[-4:])+1)
        ending_date = an_year_later_one_day_left(starting_date)
        ending_date_datetime_format = datetime.strptime(
            ending_date, '%d.%m.%Y')

    download_instat_matches_for_all_players_in_period(starting_date, today)

else:
    download_instat_matches_for_all_players_in_period(start_date, today)

script_end = time.time()
times = (script_end - script_start)/60

# driver.quit()
print('\nDonwload completed!\nGood job asshole...')


# Concatenating values --------------------------------------------------------
all_files_paths = [join(downloads_path, f) for f in listdir(
    downloads_path) if isfile(join(downloads_path, f))]
first = True
all_new_data = []
all_players_till_the_date_before_full_path = None


for complete_file_path in tqdm(all_files_paths):

    # Get the filename
    file_extension = -5
    filename = complete_file_path[len(downloads_path)+1:file_extension]
    if filename[11:] == all_players_till_the_date:
        all_players_till_the_date_before_full_path = complete_file_path
        continue

    single_data = pd.read_excel(complete_file_path)
    player_name = filename[11:]
    single_data['name'] = [player_name for i in range(single_data.shape[0])]
    if first:
        all_new_data = single_data
        first = False
    else:
        # Concatenation
        all_new_data = pd.concat([all_new_data, single_data])

all_new_data.index = [i for i in range(all_new_data.shape[0])]


# REMOVAL ---------------------------------------------------------------------
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

# Concatenate if there's the df with old records
if all_players_till_the_date_before_full_path:
    all_players_till_the_date_before_full_path = pd.read_excel(
        all_players_till_the_date_before_full_path)
    all_new_data = pd.concat(
        [all_new_data, all_players_till_the_date_before_full_path])


# SAVING ----------------------------------------------------------------------
# Create the name for storing
all_players_till_the_date_complete_path = downloads_path + '\\' + \
    all_new_data_most_recent_date+' '+all_players_till_the_date+'.xlsx'

all_new_data.to_excel(all_players_till_the_date_complete_path)
