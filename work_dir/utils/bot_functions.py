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


def datetime_to_instat_format(datetime_obj):
    return str(datetime_obj.day) + '.' + str(datetime_obj.month) + '.' + str(datetime_obj.year)
    

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
def download_wait(downloads_path, len_before, timeout):
    """
    Wait number of files increase.
    """
    not_matched = True
    sec = 0
    
    while not_matched:
        time.sleep(1)
        sec += 1
        
        if (len([f for f in listdir(downloads_path) if isfile(join(downloads_path, f))]) == (len_before + 1)) or sec > timeout:
            time.sleep(2)
            not_matched = False
    return (len([f for f in listdir(downloads_path) if isfile(join(downloads_path, f))]) == (len_before + 1))


# POCO ELECANTE ma selenium delude
def wait_and_try_to_find_loop(element, sleeptime = 2):
    try:
        time.sleep(sleeptime)
        element
    except:
        wait_and_try_to_find_loop(element)
    return element


# Get the new tab as difference 
def select_new_tab(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif[0]


# Simply get a date 364 days before
def an_year_later_one_day_left(starting_date):
    res = str(int(starting_date[:2])-1) + starting_date[2:-4] + str(int(starting_date[-4:])+1)
    return res

def right_format_date_imputation(string):
    if len(string) == 8:
        string = string[:-2] + '20' + string[-2:]
    elif len(string) == 5:
        string = string + '/' + str(datetime.now().year)
    return string


