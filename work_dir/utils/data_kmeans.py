import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import cm as cms

from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
import json
from os import chdir
# chdir('..\\')
from work_dir.utils.data_functions import correct_sessione_and_esercizio, remove_duplicate_symbol, get_ordered_cmap, kMeansRes, chooseBestKforKMeans

file = open(".\\config.json")
config_file = json.load(file)
file.close

# Import
path = "C:/Users/vince/Desktop/Olbia/olbia_project_AI/data/joined/joined.xlsx"
df = pd.read_excel(path)

ab = df
df = ab

# Options
recap_info = True
var_rif = 'D'
optionable_palette = 'viridis'
figx = 15
figy = 15

# Info
sessione_before = len(set(df['sessione']))
esercizio_before = len(set(df['esercizio']))

# Data Selection
variabili_scelte = config_file["selected_variables"]
df = df.rename(columns={'session': 'sessione', 'notes': 'esercizio'})


sessioni_escluse = ['amichevole ', 'amichevole',  'campionato', 'torneo','coppa italia ',
                    'partita a tema', 'partita finale','partita','partita ',
                    
                    'sostituzioni', 'full training', 'full training ','full training',
                    'full training att/cen','full training difensori', 'full match',
                    'full training G','full training NG','full training ng',
                    'full training parziale', 'differenziato','dif',
                    
                    'FM','fm', 'full match','gara','T1','T2', '1T','2T', 't1','t2'
                    '0-15',"15'-30","30'-45'","45'-60'","60'-75'","75'-90'",
                    "15'","30'","45'","60'", "75'",
                    
                    'arbo', 'occhio', 'trava', 'cocco', 'boccia', 'pale', 'bello',
                    "muroni",'pisano - 30','renault','renault 45', 'king',
                    'emerson', 'evrald', 'dema','la rosa', 'lella', 'sanna',
                    'ragatzu',
                    
                    'trq','villareal','chi non ha giocato', 'chi ha giocato'

                    ]



# Restrizione ad esercizi
df['sessione'] = df['sessione'].str.rstrip()
df = df[variabili_scelte].copy()
df = df[~(df['sessione'].str.contains('|'.join(sessioni_escluse)))].copy()
lenb = len(set(df['sessione']))
df = correct_sessione_and_esercizio(df)
df['sessione'] = remove_duplicate_symbol(df['sessione'])

unique_session = sorted(list(set(df['sessione'])))
sessione_after = len(set(df['sessione']))
esercizio_after = len(set(df['esercizio']))

if sessione_before > lenb > sessione_after:
    print('OK')

for i in unique_session:
    print(i)
print(len(unique_session))

# Attributi qualitativi -------------------------------------------------------
# Creo il dizionario che da esercizio mi riporta a sessione
attribute = {}
for i in range(df.shape[0]):
    if df['esercizio'].iloc[i] not in list(attribute.keys()):
        attribute[df['esercizio'].iloc[i]] = df['sessione'].iloc[i]
number_of_sessions = len(set(attribute.values()))
number_of_exercises = len(set(df['esercizio']))


# Correlazione ordinata -------------------------------------------------------
corr = df.corr()
descending_corr_series = corr['D'].sort_values(ascending=False)
descending_corr_series_index = descending_corr_series.index

zeros_array = np.zeros([len(descending_corr_series_index),len(descending_corr_series_index)])


for riga in range(len(descending_corr_series_index)):
    for colonna in range(len(descending_corr_series_index)):
        zeros_array[riga,colonna] = corr.loc[descending_corr_series_index[riga],descending_corr_series_index[colonna]]

ord_corr = pd.DataFrame(zeros_array)
ord_corr.columns = descending_corr_series_index
ord_corr.index = descending_corr_series_index

# Colors definition -----------------------------------------------------------
my_cmap = matplotlib.cm.get_cmap(optionable_palette)
my_cmap.set_under('w')

lst = list(ord_corr[var_rif])
minima = min(lst)
maxima = max(lst)

norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
mapper = cm.ScalarMappable(norm=norm, cmap=my_cmap)
for i in range(10):
    print()

variable_to_color = {}
for i in range(ord_corr.shape[0]):
    variable_to_color[ord_corr.index[i]] = mapper.to_rgba(lst[i])
    
if recap_info:
    
    # Generali di conteggio
    print('In totale abbiamo {} differenti esercizi'.format(number_of_exercises))
    print('In totale abbiamo {} differenti sessioni'.format(number_of_sessions))
    
    # Plot
    titolo = "Correlazione variabili"
    f, ax = plt.subplots(figsize=(figx, figy))
    ax = sns.heatmap(ord_corr, linewidths = 1,mask=np.zeros_like(ord_corr, dtype=np.bool), cmap=my_cmap,
                square=True, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)
    ax.set_title(titolo)
    
    titolo = "Correlazione rispetto " + str(var_rif)
    f, ax = plt.subplots(figsize=(figx, figy))
    ax = sns.barplot(x=ord_corr.index, y=ord_corr.loc[var_rif], palette = mapper.to_rgba(lst))
    ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)
    ax.set_title(titolo)


# Groupby ---------------------------------------------------------------------
df_gb = df.groupby(by='sessione', axis=0, as_index=True, sort=True, group_keys=True, dropna=True).mean().copy()
df_index = df_gb.index

# -----------------------------------------------------------------------------
# PRINCIPAL COMPONENT ANALYSIS ------------------------------------------------
# ALL VARIABLES ---------------------------------------------------------------

scaled_columns = df_gb.columns

scaler = MinMaxScaler()
print(scaler.fit(df_gb))
print(scaler.data_max_)
print(scaler.transform(df_gb))
df_scaled = scaler.transform(df_gb)
df_scaled = pd.DataFrame(df_scaled)
df_scaled.columns = df_gb.columns

# Decomposition

# Looking for all components avaible ------------------------------------------
n_components_complete = df_scaled.shape[1]
pca_complete=PCA(n_components=n_components_complete)
pca_complete.fit(df_scaled)
pca_complete_values=pca_complete.components_
pca_complete.components_
print(pca_complete.explained_variance_ratio_)
components_name_complete = ['C_%d' % i for i in range(1, n_components_complete +1)]

# Color map
cmap_secondary = plt.get_cmap('Blues_r')
colors_complete = cmap_secondary(np.linspace(0, 1, n_components_complete))

titolo = 'Varianza spiegata dalle componenti'
plt.figure(figsize = (figx, figy))
plt.bar(components_name_complete, pca_complete.explained_variance_ratio_, width=0.8, color=colors_complete)
plt.xticks(rotation=90)
plt.title(titolo)


# testing ---------------------------------------------------------------------
columns = df_scaled.columns
print(abs( pca_complete.components_ ))

f_c = {}
s_c = {}
t_c = {}

for i in range(len(columns)):
    f_c[columns[i]] = pca_complete.components_[0][i]
    s_c[columns[i]] = pca_complete.components_[1][i]
    t_c[columns[i]] = pca_complete.components_[2][i]
    
f_c = dict(sorted(f_c.items(), key=lambda item: abs(item[1]), reverse=True))
s_c = dict(sorted(s_c.items(), key=lambda item: abs(item[1]), reverse=True))
t_c = dict(sorted(t_c.items(), key=lambda item: abs(item[1]), reverse=True))

# Plot Settings ---------------------------------------------------------------

c_c = [f_c, s_c, t_c]
i = 1


for c in c_c:
    
    valus_list = list(c.values())
    abs_list = [abs(i) for i in valus_list]
    i = i+1
    mask1 = abs_list > np.mean(abs_list)
    mask2 = abs_list <= np.mean(abs_list)
    
    cl = np.array(list(c.values()))
    cols = np.array(list(c.keys()))
    
    ordered_cmap = get_ordered_cmap(list(c.keys()), variable_to_color = variable_to_color)
    
    title = 'Componente principale '+ str(i)
    plt.figure(figsize = (figx, figy))
    plt.bar(cols[mask1], np.array(valus_list)[mask1], color = np.array(ordered_cmap)[mask1])
    plt.bar(cols[mask2], np.array(valus_list)[mask2], color =np.array(ordered_cmap)[mask1]*0.2)
    plt.xticks(rotation=90)
    plt.title(title)
    plt.show()
    

# Varianza cumulata
cumulatives = []
cumulative = 0
for i in pca_complete.explained_variance_ratio_:
    cumulative = i + cumulative
    cumulatives.append(cumulative)

percentuale_spiegata = 0.9
power_component_index = 0
while cumulatives[power_component_index] < percentuale_spiegata:
    power_component_index += 1
power_component_index += 1

soglia_label = f'Soglia {str(percentuale_spiegata * 100)}%'
titolo = 'Varianza spiegata cumulata dalle componenti'
plt.figure(figsize = (figx, figy))
plt.bar(components_name_complete, cumulatives, width=0.8, color=colors_complete)
plt.hlines(0.9, xmin = -0.5, xmax = len(components_name_complete) - 0.5, colors = 'red', linestyles = 'dashed', label = soglia_label)
plt.title(titolo)
plt.legend(loc = 2)
plt.xticks(rotation=90)
plt.show()


titolo = f'Componenti per oltre il {str(percentuale_spiegata * 100)}% di varianza spiegata'
plt.figure(figsize = (figx, figy))
plt.bar(components_name_complete[:power_component_index], cumulatives[:power_component_index], width=0.8, color=colors_complete[:power_component_index])
plt.hlines(0.9, xmin = -0.5, xmax = power_component_index - 0.5, colors = 'red', linestyles = 'dashed', label = soglia_label)
plt.title(titolo)
plt.legend(loc = 2)
plt.show()



# Selecting the best 2 --------------------------------------------------------
# Looking for all components avaible
n_components = 3
pca=PCA(n_components=n_components)
pca.fit(df_scaled)
pca_values=pca.components_
pca.components_
print(pca.explained_variance_ratio_)
components_name = ['C_%d' % i for i in range(1, n_components +1)]
cmap = plt.get_cmap(optionable_palette)
colors = cmap(np.linspace(0, 1, n_components))

# Circle plot -----------------------------------------------------------------
plt.figure(figsize=(figx, figy))
plt.rcParams.update({'font.size': 14})

# Plot circle
# Create a list of 500 points with equal spacing between -1 and 1
plt.figure(figsize=(figx*2, figx*2))

# Plot smaller circle
x=np.linspace(start=-0.5,stop=0.5,num=500)
y_positive=lambda x: np.sqrt(0.5**2-x**2) 
y_negative=lambda x: -np.sqrt(0.5**2-x**2)
plt.plot(x,list(map(y_positive, x)), color='grey')
plt.plot(x,list(map(y_negative, x)),color='grey')

# Create broken lines
max_component_value = max(max(pca_values[0]), abs(min(pca_values[0])), max(pca_values[1]), abs(min(pca_values[1])) )
x=np.linspace(start=-(max_component_value *1.1),stop=(max_component_value *1.1),num=30)
plt.scatter(x,[0]*len(x), marker='_',color='grey')
plt.scatter([0]*len(x), x, marker='|',color='grey')

# Define color list
add_string=""
for i in range(len(pca_values[0])):
    xi=pca_values[0][i]
    yi=pca_values[1][i]
    plt.arrow(0,0, 
              dx=xi, dy=yi, 
              head_width=0.03, head_length=0.05, 
              color=mapper.to_rgba(lst[i]), length_includes_head=True)
    add_string=f" ({round(xi,2)} {round(yi,2)})"
    plt.text(pca_values[0, i], 
             pca_values[1, i] , 
             s=columns[i]  )

plt.xlabel(f"C_1 ({round(pca.explained_variance_ratio_[0]*100,2)}%)")
plt.ylabel(f"C_2 ({round(pca.explained_variance_ratio_[1]*100,2)}%)")
plt.title('Mappa delle variabili')
plt.show()

# Plot esercizi ---------------------------------------------------------------
X = pca.fit_transform(df_scaled)

first = []
second = []
third = []
for i in range(len(X)):
    first.append(X[i][0])
    second.append(X[i][1])
    third.append(X[i][2])

# -----------------------------------------------------------------------------
dfx = pd.DataFrame(X)
dfx.columns = ['PC1','PC2','PC3']
dfx['PC3'] = dfx['PC3'] * 90
dfx['Durata'] = df_scaled['T_conversion'] * 100
# dfx['indice'] = df_index
# dfx['sessione'] = [attribute[i] for i in dfx['indice']]
dfx['sessione'] = df_index
unique_sess = list(set(dfx['sessione']))

# colors ----------------------------------------------------------------------
palette = cms.get_cmap('tab20', len(unique_sess))

attr_colors = {}
for i in range(len(unique_sess)):
    attr_colors[unique_sess[i]] = palette(1/len(unique_sess) + i/len(unique_sess))

# opzione 1 ------------------------ PLAYABLE ---------------------------------
def evidence_plot(lista):
    viz_multpy = 1.05
    norm_dim_on_third_dim = (dfx['PC3'] - min(dfx['PC3']))/(max(dfx['PC3']) - min(dfx['PC3']))
    s = ( norm_dim_on_third_dim + 1) * 20
    cfg_color = {}
    for k,v in attr_colors.items():
        if k not in sessioni_selezionate:
            cfg_color[k] = (0.1, 0.1, 0.1, 0.1)
        else:
            cfg_color[k] = v
     
    fig, ax = plt.subplots()
    plt.figure(figsize = (figx*2, figy*2))
    ax.scatter(dfx['PC1'], dfx['PC2'], c=dfx['sessione'].map(cfg_color), s = s ,label = sessioni_selezionate)
    handlelist = []
    keys = []
    for k,v in cfg_color.items():
        if k in sessioni_selezionate:
            handlelist.append(ax.plot([], marker="o", ls="", color=v)[0])
            if k not in keys:
                keys.append(k)
        
    ax.hlines(0,min(first)*viz_multpy,max(first), colors = 'grey', linestyles = ':')
    ax.vlines(0, min(second)*viz_multpy, max(second), colors = 'grey', linestyles = ':')
    ax.legend(handlelist, keys,loc=0, bbox_to_anchor=(1, 0.5))
    ax.set_title('Sessioni sulle 2 componenti + 1', loc= 'right')
    fig.show()

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
set(dfx['sessione'])

sessioni_selezionate = [ 
 'sviluppo di posizione',
 'sviluppo di posizione 4c4 +2ji +2je',
 'sviluppo di posizione 6c6 +2 +2',
 ]

evidence_plot(sessioni_selezionate)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
 
sns.set_style("white")

# create figure
my_dpi=96
plt.figure(figsize=(480/my_dpi, 480/my_dpi), dpi=my_dpi)

df3d = dfx.copy()
df3d['sessione']=pd.Categorical(df3d['sessione'])
my_color=df3d['sessione'].cat.codes
df3d = df3d.drop('sessione', 1)
s = df3d['Durata']
 
# -----------------------------------------------------------------------------


# Create 5 blobs of 2,000 random data
n_samples = 2000
random_state = 42
X, y = make_blobs(n_samples=n_samples, 
                  random_state=random_state, 
                  centers=5)

complete_transform = pca_complete.fit_transform(df_scaled)

PC3 = complete_transform[:,2]
dfx['PC3'] = PC3
X = dfx[['PC1','PC2','PC3']]

           
# Plot the random blub data
plt.figure(figsize=(6, 6))
plt.scatter(X['PC1'], X['PC2'], s=5)
plt.title("No Clusters Assigned")


# Plot the data and color code based on clusters
# changing the number of clusters 
max_cluster_number = 20

for i in range(1,max_cluster_number + 1):
    plt.figure(figsize=(6, 6))
    
    # Predicting the clusters
    y_pred = KMeans(n_clusters=i, random_state=random_state).fit_predict(X)
# plotting the clusters
    plt.scatter(X['PC1'], X['PC2'], c=y_pred, s=30)
    plt.title(f"Number of Clusters: {i}")
plt.show();


km = KMeans(n_clusters=i, random_state=random_state)
km.fit(X)


# Calculating the inertia and silhouette_score¶
inertia = []
sil = []
# changing the number of clusters 
for k in range(2,max_cluster_number + 1):
    
    km = KMeans(n_clusters=k, random_state=random_state)
    km.fit(X)
    y_pred = km.predict(X)
    
    inertia.append((k, km.inertia_))
    sil.append((k, silhouette_score(X, y_pred)))

fig, ax = plt.subplots(1,2, figsize=(12,4))
# Plotting Elbow Curve
x_iner = [x[0] for x in inertia]
y_iner  = [x[1] for x in inertia]
ax[0].plot(x_iner, y_iner)
ax[0].set_xlabel('Number of Clusters')
ax[0].set_ylabel('Intertia')
ax[0].set_title('Elbow Curve')
# Plotting Silhouetter Score
x_sil = [x[0] for x in sil]
y_sil  = [x[1] for x in sil]
ax[1].plot(x_sil, y_sil)
ax[1].set_xlabel('Number of Clusters')
ax[1].set_ylabel('Silhouetter Score')
ax[1].set_title('Silhouetter Score Curve')




# from joblib import Parallel, delayed
best_k, results = chooseBestKforKMeans(scaled_data = X, k_range = range(1, max_cluster_number +1))
km = KMeans(n_clusters=best_k, random_state=random_state)
km.fit(X)
y_pred = km.predict(X)
dfx['km_pred'] = y_pred


# -----------------------------------------------------------------------------
for i in set(y_pred):
    sessioni_selezionate = dfx['sessione'].loc[(dfx['km_pred'] == i)] 
    sessioni_scelte = list(sessioni_selezionate)
    index = list(sessioni_selezionate.index)
    PC3 = dfx['Durata'].iloc[index]
    norm_dim_on_third_dim = (PC3 - min(PC3))/(max(PC3) - min(PC3))
    s = ( norm_dim_on_third_dim + 1) * 20
    
    # out = [ii for ii in list(dfx.index) if ii not in index]
    cfg_color = {}
    for k,v in attr_colors.items():
        if k not in sessioni_scelte:
            cfg_color[k] = (0.1,0.1,0.1,0.1)
        else:
            cfg_color[k] = v
        
    fig, ax = plt.subplots()
    plt.figure(figsize = (50,20))
    ax.scatter(dfx['PC1'], dfx['PC2'], c= (0.1,0.1,0.1,0.1), s = dfx['Durata'])
    ax.scatter(dfx['PC1'].iloc[index], dfx['PC2'].iloc[index], c=dfx['sessione'].iloc[index].map(cfg_color), s = s,label = sessioni_scelte)
    handlelist = []
    keys = []
    for k,v in cfg_color.items():
        if k in sessioni_scelte:
            handlelist.append(ax.plot([], marker="o", ls="", color=v)[0])
            if k not in keys:
                keys.append(k)
        
    ax.hlines(0,min(first)*1.2,max(first)*1.2, colors = 'grey', linestyles = ':')
    ax.vlines(0, min(second)*1.2, max(second)*1.2, colors = 'grey', linestyles = ':')
    ax.legend(handlelist, keys,loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_title(f'Confronto sessioni cluster {i}', loc= 'right')
    fig.show()
    
    
# 3D --------------------------------------------------------------------------
df3d['kmean'] = y_pred
df3d['kmean']=pd.Categorical(df3d['kmean'])
my_color=df3d['kmean'].cat.codes
df3d = df3d.drop('kmean', 1)
s = df3d['Durata']
 
# Run The PCA
pca_3 = PCA(n_components=3)
pca_3.fit(df_scaled)
 
# Store results of PCA in a data frame
result=pd.DataFrame(pca_3.transform(df_scaled), columns=['PCA%i' % i for i in range(3)], index=dfx.index)
 
# Plot initialisation
fig = plt.figure(figsize = (20,20))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(result['PCA0'], result['PCA1'], result['PCA2'], c=my_color, cmap=palette, s=s)

# make simple, bare axis lines through space:
xAxisLine = ((min(result['PCA0']), max(result['PCA0'])), (0, 0), (0,0))
ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'grey')
yAxisLine = ((0, 0), (min(result['PCA1']), max(result['PCA1'])), (0,0))
ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'grey')
zAxisLine = ((0, 0), (0,0), (min(result['PCA2']), max(result['PCA2'])))
ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'grey')
 
# label the axes
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_zlabel("PC3")
ax.set_title("PCA 3D")
plt.show()