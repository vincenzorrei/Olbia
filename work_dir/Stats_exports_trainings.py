from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import isfile, join
import time
import pickle
from IPython import get_ipython
import datetime
import os
import fast_functions



user = "olbiapass65"
pw = "olbiapass65"

PATH = "C:\Program Files (x86)\chromedriver.exe"

# Seleziono la cartella di destinazione
downloads_path = "C:\\Users\\vince\\Desktop\\Contrader\\Calcio\\Olbia\\data\\trainings"

# Controllo quali siano i file già presenti nella cartella di destianzione
already_downloaded = [f[:-4] for f in listdir(downloads_path) if isfile(join(downloads_path, f))]
number_of_files_yet_downloaded = len(already_downloaded)


# Standardizzo il nome per il salvataggio e il matching
def standardize_name(string):
    excluded_values = ["ˆ","~","{","}","”","#","|","&","*",":","?","/","\\","<",">"]
    for i in excluded_values:
        string = string.replace(i,"")
    return string.replace("%","percent").lower()


# Clear per il terminal
def clearConsole():
    try:
        get_ipython().magic('clear')
    except:
        pass


# Per aspettare il download
def download_wait(directory, len_before, timeout):
    """
    Wait number of files increase.
    """
    not_matched = True
    sec = 0
    
    while not_matched:
        time.sleep(1)
        sec += 1
        
        if len([f for f in listdir(downloads_path) if isfile(join(downloads_path, f))]) == len_before + 1 or sec > timeout:
            time.sleep(2)
            not_matched = False


# Setto il webdriver
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : downloads_path}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(PATH, chrome_options=chrome_options)
driver.maximize_window()

# Sleep time per il ciclo
sleeptime = 1

# settiamo l'attesa massima
wait = WebDriverWait(driver, 10)

clearConsole()

# Setto il sito di partenza
driver.get("http://stats-dynamix.com/Account/KineticLogOn?returnUrl=%2FGpsReports%2FTrainings%3Fgrid-page%3D14")

# Cerco la barra per l'username
username_bar = driver.find_element(By.ID,"UserName")

# Scrivo all'interno della barra
username_bar.send_keys(user)

# Cerco la barra per la password
pw_bar = driver.find_element(By.ID,"Password")

# Scrivo all'interno della barra
pw_bar.send_keys(pw)

# Premo invio
pw_bar.send_keys(Keys.RETURN)

# Individuo il bottone e premo
button = driver.find_element(By.XPATH,"//div[@class='TileTitle']").click()
button = driver.find_element(By.XPATH,"(//div[@class='TileTitle'])[3]").click()


# Due calcoli per le info sulle pagine e tempo mancante
len_full_page = len(driver.find_elements(By.CLASS_NAME ,"grid-row "))
button = driver.find_element(By.XPATH,'//*[@id="KSWrapper"]/div[1]/div/div/div/div/ul/li[5]/a').click()
pages = int(driver.find_element(By.XPATH,'//*[@id="KSWrapper"]/div[1]/div/div/div/div/ul/li[5]/a').text)
len_last_page = len(driver.find_elements(By.CLASS_NAME ,"grid-row "))
driver.back()
total_len = (pages - 1) * len_full_page + len_last_page


# Dict per data e ordine degli esercizi con if nel caso si interrompa
if 'file_to_download_in_this_tournment' not in locals():
    file_to_download_in_this_tournment = total_len - number_of_files_yet_downloaded

if 'name_to_date' not in locals():
    name_to_date = {}

if 'date_to_name_to_info' not in locals():
    date_to_name_to_info = {}

if 'conteggio_giornaliero' not in locals():
    conteggio_giornaliero = 0

if 'old_date' not in locals():
    old_date = 0

if 'files_count' not in locals():
    files_count = 0

if 'expected_replicas' not in locals():
    expected_replicas = []

if 'processed_expected_names' not in locals():
    processed_expected_names = []
    
if 'processed_expected_names_with_extension' not in locals():
    processed_expected_names_with_extension = []
    
if 'count_already_downloaded_on_other_tournment' not in locals():
    count_already_downloaded_on_other_tournment = 0

# Questa deve essere inizializzata ogni volta
count_already_downloaded_matched = 0

# Opzione per il while loop
there_is_a_next_page = True

# Inizia il conteggio del tempo
start_time = time.time()


while there_is_a_next_page:
    
    # Seleziono gli elementi della griglia
    grid_elements = driver.find_elements(By.CLASS_NAME ,"grid-row ")
    
    # Itero per il numero elementi della griglia
    for i in range(len(grid_elements)):
        
        # Info per data e ordine
        date = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[1]'.format(i+1)))).text
        group_name = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[2]'.format(i+1)))).text
        session_name = wait.until(EC.presence_of_element_located((By.XPATH ,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[3]'.format(i+1)))).text
        notes = wait.until(EC.presence_of_element_located((By.XPATH ,'/html/body/div[1]/section/div[1]/div/div/table/tbody/tr[{}]/td[4]'.format(i+1)))).text
        
        # Salvataggio standard del nome atteso
        expected_name = group_name + "_" + session_name
        expected_name = standardize_name(expected_name)
        expected_name_with_extenion = expected_name + '.csv'
        
        # 1) Controllo che non sia stato già scaricato in un precedente tournment
        if expected_name in already_downloaded:
            print('Already downloaded in other tournment:\n{}\n\nSo skipped\n'.format(expected_name))
            count_already_downloaded_on_other_tournment +=1
            print('Founded on totals:\n{}/{}'.format(count_already_downloaded_on_other_tournment,number_of_files_yet_downloaded))
            continue
 
        
        # 2) Controllo che non sia stato già processato in questo tournment
        if expected_name in processed_expected_names:
            clearConsole()
            count_already_downloaded_matched += 1

            print('\nAlready downloaded:\n{}\n'.format(expected_name))
            print('Found already downloaded in this tournment on true already downloaded in this tournment:\n{}/{}'.format(count_already_downloaded_matched,number_of_files_yet_downloaded - len(processed_expected_names)))
            time.sleep(1)
            continue


        # 3) Controlliamo se è passata una replica: in teoria, arrivati qua all'if dovrebbe valere l'uguaglianza
        if count_already_downloaded_matched < number_of_files_yet_downloaded:
            expected_replicas.append(expected_name)
            
            print('\n\nAttention!!!\n')
            print('Found an expected replica:\n{}\n'.format(expected_name))
            print('Total expected replicas:\n{}\n'.format(len(expected_replicas)))

            
        # Se cambiata la data, per la data precedente sistemo il conteggio degli esercizi che ora è al contrario
        if date != old_date and old_date != 0:
            conteggio_giornaliero = 0
            
            exercise_in_the_day = list(date_to_name_to_info[old_date].keys())
            inverted_order = [date_to_name_to_info[old_date][ex]['ord'] for ex in exercise_in_the_day]
            true_order = list(reversed(inverted_order))
                
            for ind in range(len(exercise_in_the_day)):
                date_to_name_to_info[old_date][exercise_in_the_day[ind]]['ord'] = true_order[ind]
        
        

        
        # Puliamo il terminal
        clearConsole()

        # Conteggio file salvati
        files_count += 1
        
        # Cronometro
        end_time = time.time()
        delta_time = end_time - start_time
        time_to_finish = delta_time * (total_len - number_of_files_yet_downloaded - files_count)
        conversion = datetime.timedelta(seconds=time_to_finish)
        time_to_finish = str(conversion)[:7]
        
        start_time = time.time()
        
        
        # Print di alcune info
        print('\nDownloading:\n{}\n'.format(expected_name))
        print('Found already downloaded on true already downaloaded:\n{}/{}'.format(count_already_downloaded_matched,number_of_files_yet_downloaded))
        print('\nDownloaded files number:\n{}/{}'.format(files_count, file_to_download_in_this_tournment))
        print('\nTime to finish:\n{}'.format(time_to_finish))
        
        
        # Aggiorno
        old_date = date
        conteggio_giornaliero += 1
        
        # Salvo nei dizionari
        name_to_date[expected_name] = date
        
        if conteggio_giornaliero == 1:
            date_to_name_to_info[date] = {}
        date_to_name_to_info[date][expected_name] = {'ord':conteggio_giornaliero,
                                                     'group_name':group_name,
                                                     'session_name':session_name,
                                                     'notes':notes}

        # Seleziono l'allenamento specifico
        xpath = "(//tr[@class='grid-row '])[" + str(i+1) + ']'
        training_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        training_element.click()
        
        # Mi sposo su "Tabella"
        time.sleep(sleeptime + sleeptime) # a volte wait non basta + sleeptime non basta
        table_element = wait.until(EC.element_to_be_clickable((By.ID, "tabNewTable")))
        table_element.click()
        
        
        # Len prima del download+
        downloaded_before = [f for f in listdir(downloads_path) if isfile(join(downloads_path, f))]
        len_before = len(downloaded_before)
        
        
        # Faccio l'export del file
        time.sleep(sleeptime) # a volte wait 
        export_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='toolbar']//button[@class='btn-toolbar']")))
        export_element.click()
        
        # Aspetto il download
        download_wait(downloads_path, len_before, 20)
        
        downloaded_till_now = [f for f in listdir(downloads_path) if isfile(join(downloads_path, f))]
        right_name = downloads_path+'\\'+ expected_name_with_extenion
        
        
        if len(downloaded_till_now) == 1:
            last_downloaded = downloaded_till_now[0]
            actual_name = downloads_path+'\\'+ last_downloaded
            os.rename(actual_name, right_name)
            
        else:
            last_downloaded = str(list(set(downloaded_till_now).symmetric_difference(set(downloaded_before)))[0])
            actual_name = downloads_path+'\\'+ last_downloaded
            os.rename(actual_name, right_name)
        
        print('\nModified:\n{}\n --->\n{}'.format(last_downloaded, expected_name_with_extenion))
            
        processed_expected_names.append(expected_name)
        processed_expected_names_with_extension.append(expected_name_with_extenion)
        print('\nRight name stored\n')
        
        
        # Torno indietro
        driver.back()

    # Condizione there_is_a_next_page    
    try:
        icon_to_next_page = wait.until(EC.visibility_of_element_located((By.LINK_TEXT , "»")))
        icon_to_next_page.click()
        
    except:
        exercise_in_the_day = list(date_to_name_to_info[date].keys())
        inverted_order = [date_to_name_to_info[date][ex]['ord'] for ex in exercise_in_the_day]
        true_order = list(reversed(inverted_order))
            
        for ind in range(len(exercise_in_the_day)):
            date_to_name_to_info[date][exercise_in_the_day[ind]]['ord'] = true_order[ind]
        
        
        print("\n\nDone!\n")
        driver.quit()
        there_is_a_next_page = False




config_filename_1 = 'C:\\Users\\vince\\Desktop\\Contrader\\Calcio\\Olbia\\config\\date_to_name_to_info.pkl'
config_filename_2 = 'C:\\Users\\vince\\Desktop\\Contrader\\Calcio\\Olbia\\config\\name_to_date_matches.pkl'

try:
    # Trainings: Import dict of dict {date:{expected name : {info}}}
    first_file = open(config_filename_1, "rb")
    date_to_name_to_info_trainings = pickle.load(first_file)
    first_file.close()
    
    # Update it with new info
    date_to_name_to_info.update(date_to_name_to_info_trainings)

    # Trainings: Import dict {expected name : date}
    second_file = open(config_filename_2, "rb")
    name_to_date_exercises = pickle.load(second_file)
    second_file.close()
    
    name_to_date.update(name_to_date_exercises)
 
except:
    pass

first_file = open(config_filename_1, "wb")
pickle.dump(date_to_name_to_info, first_file)
first_file.close()

second_file = open(config_filename_2, "wb")
pickle.dump(name_to_date, second_file)
second_file.close()

print('Ancillary information saved in the folder:\nC:\\Users\\vince\\Desktop\\Contrader\\Calcio\\Olbia\\config')
