from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir, chdir 
chdir('..\\')
from os.path import isfile, join
import time
import pickle
from IPython import get_ipython
import datetime
import os
import json
from work_dir.utils.bot_functions import standardize_name, clearConsole, download_wait

file = open(".\\config.json")
config_file = json.load(file)
file.close

user = config_file['credentials']['user']
pw = config_file['credentials']['password']
chromedriver = config_file['paths']['chromedriver']
downloads_path = config_file['paths']['trainings']

# Controllo quali siano i file già presenti nella cartella di destianzione
already_downloaded = [f for f in listdir(downloads_path) if isfile(join(downloads_path, f))]
number_of_files_yet_downloaded = len(already_downloaded)            
            
# Setto il webdriver
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : downloads_path}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
driver.maximize_window()

# Sleep time per il ciclo
sleeptime = 1
wait = WebDriverWait(driver, 10)
clearConsole()

# Setto il sito di partenza
driver.get("http://stats-dynamix.com/Account/KineticLogOn?returnUrl=%2FGpsReports%2FTrainings%3Fgrid-page%3D14")

# Cerco la barra per l'username
username_bar = driver.find_element(By.ID,"UserName")
username_bar.send_keys(user)

# Cerco la barra per la password e premo 'invio'
pw_bar = driver.find_element(By.ID,"Password")
pw_bar.send_keys(pw)
pw_bar.send_keys(Keys.RETURN)

# Individuo il bottone e premo
button = driver.find_element(By.XPATH,"//div[@class='TileTitle']").click()
button = driver.find_element(By.XPATH,"(//div[@class='TileTitle'])[2]").click()

# Vedo quanti sono nell'ultima pagina
len_full_page = len(driver.find_elements(By.CLASS_NAME ,"grid-row "))
button = driver.find_element(By.XPATH,'//*[@id="KSWrapper"]/div[1]/div/div/div/div/ul/li[5]/a').click()
pages = int(driver.find_element(By.XPATH,'//*[@id="KSWrapper"]/div[1]/div/div/div/div/ul/li[5]/a').text)
len_last_page = len(driver.find_elements(By.CLASS_NAME ,"grid-row "))
driver.back()
total_len = (pages - 1) * len_full_page + len_last_page

# Dict per data delle partite
if 'file_to_download_in_this_tournment' not in locals():
    file_to_download_in_this_tournment = total_len - number_of_files_yet_downloaded
    
if 'match_name_date' not in locals():
    match_name_date = {}
    
if 'match_date_name_info' not in locals():
    match_date_name_info = {}
    
if 'files_count' not in locals():
    files_count = 0
    
if 'old_date' not in locals():
    old_date = 0
    
if 'expected_replicas' not in locals():
    expected_replicas = []
    
if 'processed_expected_names' not in locals():
    processed_expected_names = []
    
if 'processed_expected_names_with_extension' not in locals():
    processed_expected_names_with_extension = []
    
if 'count_already_downloaded_on_other_tournment' not in locals():
    count_already_downloaded_on_other_tournment = []
    
# Inizializzazioni
count_already_downloaded_matched = 0
there_is_a_next_page = True
page = 0
start_time = time.time()

while there_is_a_next_page:
    # Seleziono gli elementi della griglia
    grid_elements = driver.find_elements(By.CLASS_NAME ,"grid-row ")
    
    # Itero per il numero elementi della griglia
    for i in range(len(grid_elements)):
        
        # Estraggo la data
        time.sleep(sleeptime)
        date = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[1]'.format(i+1)))).text
        group_name = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[2]'.format(i+1)))).text
        session_name = wait.until(EC.presence_of_element_located((By.XPATH ,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[3]'.format(i+1)))).text
        notes = wait.until(EC.presence_of_element_located((By.XPATH ,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[4]'.format(i+1)))).text
        
        # Salvataggio standard del nome atteso
        expected_name = group_name + "_" + session_name
        expected_name = standardize_name(expected_name)
        expected_name_with_extenion = expected_name + '.csv'
        
        
        # Dizionario dal nome ci da la data
        match_name_date[expected_name] = date
        
        # Conteggio file salvati
        files_count += 1
        
        # Dizionario data - nome - info
        if date != old_date:
            match_date_name_info[date] = {}
        match_date_name_info[date][expected_name] = {'group_name':group_name,
                                                      'session_name':session_name,
                                                      'notes':notes}
        
        old_date = date
        clearConsole()

        processed_expected_names.append(expected_name)
        processed_expected_names_with_extension.append(expected_name_with_extenion)        

    # Condizione there_is_a_next_page    
    xpath = '/html/body/div[1]/section/div[1]/div/div/div/div/ul/li[last()]/a'
    wait.until(EC.presence_of_element_located((By.XPATH, xpath))).click()
    page += 1
    clearConsole()
    print(f"Page {page}/{pages} downaloaded!")
    try:
        link_in_text = str(wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text)
        # print(f'Link in text: {link_in_text}\nNext page symbol: {next_page_symbol}\n Equivalence: {link_in_text != next_page_symbol}')
    
    
    except:
        driver.quit()
        there_is_a_next_page = False

    
config_filename_1 = config_file['paths']['match_date_name_info']
config_filename_2 = config_file['paths']['match_name_date']

try:
    # Trainings: Import dict of dict {date:{expected name : {info}}}
    first_file = open(config_filename_1, "rb")
    match_date_name_info_prec = pickle.load(first_file)
    first_file.close()
    match_date_name_info.update(match_date_name_info_prec)

    # Trainings: Import dict {expected name : date}
    second_file = open(config_filename_2, "rb")
    match_name_date_old = pickle.load(second_file)
    second_file.close()
    match_name_date.update(match_name_date_old)
    
except:
    pass

first_file = open(config_filename_1, "wb")
pickle.dump(match_date_name_info, first_file)
first_file.close()

second_file = open(config_filename_2, "wb")
pickle.dump(match_name_date, second_file)
second_file.close()

print('Ancillary information saved!')