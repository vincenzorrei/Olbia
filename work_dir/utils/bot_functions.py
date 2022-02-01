# Standardizzo il nome per il salvataggio e il matching
def standardize_name(string):
    excluded_values = ["ˆ","~","{","}","”","#","|","&","*",":","?","/","\\","<",">"]
    for i in excluded_values:
        string = string.replace(i,"")
    return string.replace("%","percent").lower()