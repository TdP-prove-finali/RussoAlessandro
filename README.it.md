# Applicazione per l'ottimizzazione logistica ed economica degli sviluppi vettura in Formula 1

Alessandro Russo

## Istruzioni per l'installazione e l'utilizzo dell'applicazione

- Effettuare il fork del progetto al seguente link URL: https://github.com/TdP-prove-finali/RussoAlessandro
- Clonare il progetto dal link all'interno del proprio ambiente di programmazione
- Installare le dipendenze eseguendo: `pip install -r Requirements.txt`
- Creare localmente un database vuoto di nome `f1_logistics_db` (MariaDB 10.10 o successivo)
- Importare il database, eseguendo il file `f1_logistics_db.sql` contenuto nella cartella `database`
- Aggiornare i dati d'accesso al database nel file `connector.cnf` (dentro la cartella `database`)
- Eseguire il file `main.py` per avviare l'applicazione

## Configurazione

- Tutte le costanti dell'applicazione sono nel file `model/constants.py` e si possono modificare da lì:
  parametri del modello (α, β, ipotesi logistiche, valori di default, limite di 12 pacchetti)
  e valori del regolamento (scala ATR, tetti di spesa, supplemento gare), da cambiare solo se cambia il regolamento
- Costi, guadagni e lead time dei pacchetti, indici dei circuiti, probabilità di pioggia e tratte sono nel database, non in `constants.py`
- I risultati riportati nella relazione sono ottenuti con i valori consegnati: modificare le costanti cambia i risultati

Il video di dimostrazione di utilizzo del software è disponibile al seguente link di YouTube: [link da inserire]

Le tratte su strada del database derivano da dati © OpenStreetMap contributors, licenza ODbL.
