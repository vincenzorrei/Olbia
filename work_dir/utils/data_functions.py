import pandas as pd
import numpy as np
from scipy import stats
import re
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


# Outlier romeval
def outlier_removal_by_pvalue(all_data, numerical_cols, p_value = 1.1102230246251565e-16):
    prob = 1 - p_value
    z_score = stats.norm.ppf(prob)
    
    zscores_condition_respected = (np.abs(stats.zscore(all_data[numerical_cols])) < z_score).all(axis=1)
    zscores_condition_unrespected = len(zscores_condition_respected) - sum(zscores_condition_respected)
    df_zscores_boolean = (np.abs(stats.zscore(all_data[numerical_cols])) >= z_score)
    
    evidence_value = pd.DataFrame()
    for index, row in df_zscores_boolean.iterrows():
        if True in list(row):
            evidence_value[all_data.iloc[index]['name']] = np.array(row) * all_data.iloc[index][numerical_cols]
                
    evidence_value = evidence_value.T.sort_index()
    print('Outlier excluded for (p = {}):\n{}\n'.format(round(p_value,20),zscores_condition_unrespected))
    print(evidence_value)
        
    return all_data[zscores_condition_respected]


#• Time format
def check_unique_time_format(a_string):
    if (a_string[-3] == ':') & (a_string[-6] == ':'):
        res = True
    else:
        res = False
    return res


# Time conversion
def convert_time_in_seconds(a_string):
    try:
        second = int(a_string[-2:]) + int(a_string[-5:-3])*60 + int(a_string[-8:-6])*3600
    except:
        try:
            second = int(a_string)
        except:
            second = 0
    return second


def plot_value_in_time(all_data, player = 'lella', value_to_plot = 'Year sin', alpha = 0.1):
    plt.style.use('dark_background')
    player_dates = list(all_data[all_data['name'] == player]['date'])
    values_player = list(all_data[all_data['name'] == player][value_to_plot])
    
    dt_start = datetime.fromtimestamp(datetime.timestamp(player_dates[0]))
    dt_stop = datetime.fromtimestamp(datetime.timestamp(player_dates[-1]))
    periods = int((dt_stop - dt_start).days)
    datelist = pd.date_range(dt_start, periods=periods).map(pd.Timestamp.timestamp)
    
    datelist = [datetime.fromtimestamp(int(i)) for i in datelist]
    plt.figure(figsize = (13,5))
    plt.scatter(datelist, [(min(values_player) - np.abs(min(values_player)*0.1)) for i in range(len(datelist))], color = 'black', marker = 'o', s = 1)
    plt.scatter(player_dates, values_player, color= 'deepskyblue', alpha = alpha, label = value_to_plot)
    plt.legend()
    plt.title(player.upper())
    plt.show()

def correct_sessione_and_esercizio(df, col1= 'esercizio', col2 = 'sessione'):

    esercizi = df[col1]
    correzione1 = esercizi == 'sdp 6c6+4'
    esercizi[correzione1] = 'sdp 6c6 +4'
    df[col1] = esercizi
    
    correzione2 = esercizi == 'pps 6+1c3 '
    esercizi[correzione2] = 'pps 6+1 c3'
    
    correzione3 = esercizi == 'pps 6 +1 c3'
    esercizi[correzione3] = 'pps 6+1 c3'
    
    correzione4 = esercizi == 'pp cat centrale 5c5 +3 '
    esercizi[correzione4] = 'pp catena centrale 5c5 +3'
    
    correzione5 = esercizi == 'pp a 3 zone '
    esercizi[correzione5] = 'pp a 3 zone'
    
    correzione6 = esercizi == 'pp 6c3 2 campi '
    esercizi[correzione6] = 'pp 6c3 2 campi'
    
    correzione7 = esercizi == 'poss doppio vertice per transizioni'
    esercizi[correzione7] = 'poss doppio vertice per transizione'
    
    correzione8 = esercizi == 'poss 4c4 +4 con 4 porte'
    esercizi[correzione8] = 'poss 4c4 +4 4porte '
    
    correzione9 = esercizi == 'pentagono '
    esercizi[correzione9] = 'pentagono'
    
    correzione10 = esercizi == 'int 20''/20''  '
    esercizi[correzione10] = 'int 20''/10'''
    
    correzione11 = esercizi == 'secco coordinativo '
    esercizi[correzione11] = 'secco-coordinativo'
    
    correzione12 = esercizi == 'int 20''/20'' '
    esercizi[correzione12] = 'int - 20"/20"'
    
    correzione13 = esercizi == 'int 20''/20'' '
    esercizi[correzione13] = 'int - 20"/20"'
    
    correzione14 = esercizi == 'int 20''/20'' misto'
    esercizi[correzione14] = 'int - 20"/20" misto'
    
    correzione15 = esercizi == 'int 15''/15'''
    esercizi[correzione15] = 'int - 15"/15"'
    
    correzione16 = esercizi == 'int 15"/15" '
    esercizi[correzione16] = 'int - 15"/15"'
    
    correzione17 = esercizi == 'int 15"/15"'
    esercizi[correzione17] = 'int - 15"/15"'
    
    correzione17 = esercizi ==  "int 15''/15''"
    esercizi[correzione17] = 'int - 15"/15"'
    
    correzione17 = esercizi ==    "int 20''/20'' "
    esercizi[correzione17] = 'int - 20"/20" '
    
    correzione17 = esercizi ==    "int 20''/10''"
    esercizi[correzione17] = 'int - 20"/10"'
    
    correzione17 = esercizi ==    'int 20"/10"'
    esercizi[correzione17] = 'int - 20"/10"'
    
    correzione17 = esercizi ==    'int 20"/20"'
    esercizi[correzione17] = 'int - 20"/20" '
    
    correzione18 = esercizi == 'diamanti simmetrici  + allungo'
    esercizi[correzione18] = 'diamanti simmetrici + allungo'
    
    correzione19 = esercizi == 'attivazione secco-coordinativo '
    esercizi[correzione19] = 'attivazione secco-coordinativo'
    
    correzione20 = esercizi == 'R4c2 a due campi '
    esercizi[correzione20] = 'R4c2 a due campi'
    
    correzione21 = esercizi == 'R4c2 +1 '
    esercizi[correzione21] = 'R4c2 +1'
    
    correzione22 = esercizi == 'R4c2 + 1'
    esercizi[correzione22] = 'R4c2 +1'
    
    correzione23 = esercizi == '40m x 50m '
    esercizi[correzione23] = '40m x 50m'
    
    correzione24 = esercizi == '34m '
    esercizi[correzione24] = '34m'
    
    correzione24 = esercizi == '5c5 +2gk '
    esercizi[correzione24] = '5c5 +2gk'
    
    correzione24 = esercizi == '40mx50m'
    esercizi[correzione24] = '40m x 50m'
    
    correzione25 = esercizi == '10c0 '
    esercizi[correzione25] = '10c0'
    
    correzione26 = esercizi == "int 20''/20'' misto"
    esercizi[correzione26] = 'int - 20"/20" misto'
    
    correzione26 = esercizi == 'int 20"/20" misto'
    esercizi[correzione26] = 'int - 20"/20" misto'
    
    correzione26 = esercizi ==  '40m x 70m '
    esercizi[correzione26] = '40m x 70m'
    
    # Report sui nomi esercizi
    df[col1] = esercizi
    
    # correzioni sessioni ---------------------------------------------------------
    sessioni = df[col2]
    
    sessione1 = sessioni == 'rondos '
    sessioni[sessione1] = 'rondos'
    
    sessione1 = sessioni == 'reparto offensivo '
    sessioni[sessione1] = 'reparto offensivo'
    
    sessione1 = sessioni == 'possesso posizonale'
    sessioni[sessione1] = 'possesso posizionale'
    
    sessione1 = sessioni == 'possesso posizionale '
    sessioni[sessione1] = 'possesso posizionale'
    
    sessione1 = sessioni == 'possesso '
    sessioni[sessione1] = 'possesso'
    
    sessione1 = sessioni == 'partita finale '
    sessioni[sessione1] = 'partita finale'
    
    sessione1 = sessioni == 'partita '
    sessioni[sessione1] = 'partita'
    
    sessione1 = sessioni == 'palle inattive '
    sessioni[sessione1] = 'palle inattive'
    
    sessione1 = sessioni == 'gioco di posizione '
    sessioni[sessione1] = 'gioco di posizione'
    
    sessione1 = sessioni == 'finalizzazioni'
    sessioni[sessione1] = 'finalizzazioni '
    
    sessione1 = sessioni == 'contrapposizioni '
    sessioni[sessione1] = 'contrapposizioni'
    
    sessione1 = sessioni == 'attivazione tecnica '
    sessioni[sessione1] = 'attivazione tecnica'
    
    sessione1 = sessioni == 'attivazione a secco '
    sessioni[sessione1] = 'attivazione a secco'
    
    sessione1 = sessioni == 'attivazione '
    sessioni[sessione1] = 'attivazione'
    
    sessione1 = sessioni == 'amichevole '
    sessioni[sessione1] = 'amichevole'
    
    sessione1 = sessioni == 'amichevole '
    sessioni[sessione1] = 'amichevole'
    
    sessione1 = sessioni == 'aerobico '
    sessioni[sessione1] = 'aerobico'
    
    sessione1 = sessioni == 'intermittente - 10/20 100%vam '
    sessioni[sessione1] = 'int - 10/20 100%vam'
    
    df[col2] = sessioni
    
    return df

def remove_duplicate_symbol(list_kind):
    correct_sessions = []
    pattern = r' \(\d\)'
    finder = re.compile(pattern)
    for i in list(list_kind):
        if (finder.search(i) != None):
            i = re.sub(pattern, '', i )
        correct_sessions.append(i.rstrip())
    return correct_sessions

def get_ordered_cmap(ordered_vars_names_list, variable_to_color):
    ordered_cmap = []
    for i in ordered_vars_names_list:
        ordered_cmap.append(variable_to_color[i])
    return ordered_cmap

def kMeansRes(X, k, alpha_k=0.02, random_state = 1):
    '''
    Parameters 
    ----------
    X: matrix 
        scaled data. rows are samples and columns are features for clustering
    k: int
        current k for applying KMeans
    alpha_k: float
        manually tuned factor that gives penalty to the number of clusters
    Returns 
    -------
    scaled_inertia: float
        scaled inertia value for current k           
    '''
    
    inertia_o = KMeans(n_clusters=1, random_state=random_state).fit(X).inertia_
    # fit k-means
    kmeans = KMeans(n_clusters=k, random_state=random_state).fit(X)
    scaled_inertia = kmeans.inertia_ / inertia_o + alpha_k * k
    return scaled_inertia

def chooseBestKforKMeans(scaled_data, k_range):
    ans = []
    for k in k_range:
        scaled_inertia = kMeansRes(scaled_data, k)
        ans.append((k, scaled_inertia))
    results = pd.DataFrame(ans, columns = ['k','Scaled Inertia']).set_index('k')
    # print(ans)
    best_k = results.idxmin()[0]
    return best_k, results