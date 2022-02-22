from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from os.path import isfile, join
from os import listdir
import time
import pickle
from datetime import datetime, timedelta, date
import os
import json

from work_dir.utils.bot_functions import clearConsole, download_wait, select_new_tab, datetime_to_instat_format, wait_and_try_to_find_loop

def download_instat_matches_for_all_players_in_period(starting_date, ending_date,  config_file, first_and_last, processed_player_list=[]):
    today = str(date.today().day) + '.' + str(date.today().month) + \
        '.' + str(date.today().year)
    
    file = open(".\\config.json")
    config_file = json.load(file)
    file.close
    
    user = config_file['credentials']['instat_user']
    pw = config_file['credentials']['instat_password']
    downloads_path = config_file['paths']['instat_matches']
    reference_team = config_file['credentials']['reference_team']
    player_to_last_instat_match_path = config_file['paths']['player_to_last_instat_match']
    stats_to_instats_names = config_file['stats_to_instats_names']
    instat_to_stats_names = {v:k for k, v in stats_to_instats_names.items()}
    stored_instat = False
    instat_already_downloaded = False
    
    if os.path.isfile(player_to_last_instat_match_path):
        with open(player_to_last_instat_match_path, 'rb') as handle:
            player_to_last_instat_match = pickle.load(handle)
        stored_instat = True

    
   # Setto il webdriver
    directory = os.getcwd() + downloads_path[1:]
    prefs = {'download.default_directory': directory}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', prefs)
    chromedriver = config_file['paths']['chromedriver']
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
    clearConsole()
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
    to_date.send_keys(today)

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
        
        # Giocatore: Se è stato già scaricato in questo ciclo di downlaod 
        if player_processed and (player_names[i-1] in player_processed):
            print("({}) {}'s career already downloaded".format(
                readable_season, player_names[i-1]))
            continue
        
        # Giocatore: Check se abbia mai giocato
        try:
            player_name_instat = instat_to_stats_names[str(player_names[i-1])]
            first_and_last[player_name_instat]
            never_played = False
        except:
            never_played = True
        
        if never_played:
            print(f'{player_names[i-1]} never played in the period')
            continue

        # Giocatore: Check se abbia già scaricato fino all'ultima partita o fino a quando
        from_date_match = first_and_last[player_name_instat]['min']
        to_date_match = first_and_last[player_name_instat]['max']
        
        
        if stored_instat:
            last_match_downloaded_instat = player_to_last_instat_match[player_name_instat]
            last_match_downloaded_instat = datetime.strptime(last_match_downloaded_instat, '%d.%m.%Y')
            
            if last_match_downloaded_instat == to_date_match:
                instat_already_downloaded = True
            elif last_match_downloaded_instat > from_date_match:
                from_date_match = last_match_downloaded_instat
        
        if instat_already_downloaded:
            print(f'{player_names[i-1]} already downloaded')
            continue
        
        from_date_match = datetime_to_instat_format(from_date_match - timedelta(days=1))
        to_date_match = datetime_to_instat_format(to_date_match + timedelta(days=1))
    
                
        # Giocatore: Seleziono il giocatore
        time.sleep(10)
        xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[2]/table/tbody/tr[{}]/td[1]/div/div[3]/a'.format(
            i)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath))).click()
        print('Player selected:\n{}/{}) {}\n'.format(i,
                number_of_elements, player_names[i-1]))
        
        # Giocatore: Mi sposto nell'ultima tab aperta
        opened_tabs_after_player_selection = driver.window_handles
        player_tab = select_new_tab(
            opened_tabs_after_player_selection, opened_tabs_before_player_selection)
        driver.switch_to.window(player_tab)

        # Mi sposto in 'matches'
        class_name = '#root > div > article > div > ul > li:nth-child(2)'
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, class_name))).click()
        print('({}) : 1/5 MATCHES'.format(readable_season))

        # Clicco su 'Current season'
        try:
            xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/span'
            time.sleep(5)
            wait_and_try_to_find_loop(wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath)))).click()
            print('({}) : 2/5 Current season '.format(readable_season))
        except:
            class_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.sc-kGXeez.eJhxTi > div > span > span.styled__Caret-sc-1dwxsrr-3.cxNuZB'
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, class_name))).click()           
            print('2/5 Current season')

        # Clicco 'Advanced ...'
        try:
            xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/div/ul/li[6]/span'
            wait_and_try_to_find_loop(wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath)))).click()
            print('({}) : 3/5 Advanced selection of matches '.format(readable_season))
        except:
            class_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.sc-kGXeez.eJhxTi > div > div > ul > li:nth-child(6) > span'
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, class_name))).click()          
            print('3/5 XPATH: Advanced selection of matches')

        # Team: Attivo il flag 'Dates'
        xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div'
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

        # Team: Inserisco la data dei primi dati disponibili dei gps
        time.sleep(3)
        
        # From
        css_name = 'div.advanced-select__filters-column-season > div:nth-child(3) > div:nth-child(1) > div > div > input'
        from_date = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_name)))
        from_date.send_keys(Keys.CONTROL, 'a')
        from_date.send_keys(Keys.BACKSPACE)
        from_date.send_keys(from_date_match)

        # To
        time.sleep(3)
        css_name = 'div.advanced-select__filters-column-season > div:nth-child(3) > div:nth-child(2) > div > div > input'
        to_date = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, css_name)))
        to_date.send_keys(Keys.CONTROL, 'a')
        to_date.send_keys(Keys.BACKSPACE)
        to_date.send_keys(to_date_match)
        time.sleep(10)

        # Premo il bottone "OK"
        try:
            class_name = '#team-table1 > div.table-scroll-inner > div.team-stats-header.team-stats-header__small > div > div.advanced-select > div > div.advanced-select__footer > button'
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, class_name))).click()
            print('({}) : 4/5 "OK" button'.format(readable_season))
        except:
            # Il bottone è opaco nel caso non ci sono match selezionati per il periodo e non può essere premuto
            print('({}) : 4/5 Matches not founded!'.format(readable_season))
            print('({}) : 5/5 Skipped!\n'.format(readable_season))
            driver.close()
            driver.switch_to.window(players_tab)
            continue

        # Controllo il numero di partite selezionate
        xpath = '/html/body/div[3]/div/article/section[2]/div/div/div[2]/div[1]/div/div[1]/div/span'
        text = wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath))).get_attribute('innerHTML')
        text = text.replace('<span class="T9n__Text-sc-oyt3bv-0 iekKGO">Selected matches</span>: ',
                            '').replace('<span class="styled__Caret-sc-1dwxsrr-3 cxNuZB"></span>', '')
        print('({}) : 5/5 Matches founded'.format(readable_season))
        time.sleep(5)

        len_before = len([f for f in listdir(downloads_path)
                         if isfile(join(downloads_path, f))])

        # Premo il formato XLS e scarico
        css_selector = 'div.team-stats-header-inner > div:nth-child(3) > a:nth-child(1)'
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
            print("({}) {}\'s downloaded NOT successfully!\n")
            player_processed = player_processed[:-1]

        # Posso chiudere questa tab e spostarmi su quella di partenza
        driver.close()
        driver.switch_to.window(players_tab)

    driver.quit()
    return player_processed
