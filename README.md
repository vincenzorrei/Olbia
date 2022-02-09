## Processo di acquisizione e aggiornamento dati
Questo progetto vede sostanzialmente due macro fasi:
1) Acquisizione dei dati
2) Concatenazione dei dati

### Acquisizione dei dati
L'acquisizione dei dati è affidata a dei bot che operano su due diverse piattaforme:
1.1) Stats dynamics per i dati relativi ai gps
1.2) Instat per i dati relativi alle partite

I bot relativi all'acquisizione dei dati alla piattaforma Stats dynamics sono molto simili
ma li analizzeremo uno per volta.

#### Stats dynamics
1.1.1) Bot Stats dynamics per i trainings
Questo è il primo bot che viene lanciato in ordine anche temporale.
Insieme all'acquisizione vengono operate anche alcune modifiche per evitare duplicati per
quanto possibile oltre che aggiunte informazioni rispetto all'ordine delle esercitazioni.

In output vengono prodotti inoltre due file .pkl che saranno salvati nella cartella 
.\data\accessories_data e che serviranno per le operazioni aggiuntive:
- train_date_name_info.pkl:
    un dizionario di dizionari che per gli allenamenti dalla data, ci porta alle esercitazioni
    alle informazioni aggiuntive;
- train_name_date.pkl:
    un dizionario che restituisce la data per l'allenamento individuato.

1.1.2) Bot Stats dynamics per i matches
E' il secondo bot ad essere lanciato.
Speculare al bot per gli allenamenti ma con le dovute differenze.
Anche questo produce i due file output che prendono il nome di 
- match_date_name_info.pkl;
- match_name_date.pkl.

#### Instat
1.2) Bot Instat 
Il bot che lavora sul sito Instat è molto lento e non affidabile al 100% dal momento che il sito,
purtroppo, non sempre risponde agli stessi input allo stesso modo.
