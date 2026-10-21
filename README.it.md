# Applicazione per l'ottimizzazione logistica ed economica degli sviluppi vettura in Formula 1

Alessandro Russo

## Istruzioni per l'installazione e l'utilizzo dell'applicazione

- Effettuare il fork del progetto al seguente link URL: https://github.com/TdP-prove-finali/RussoAlessandro
- Clonare il progetto dal link all'interno del proprio ambiente di programmazione
- Installare le dipendenze eseguendo: `pip install -r Requirements.txt`
- Creare localmente un database vuoto di nome `f1_logistics_db` (MySQL 5.7/8 o MariaDB; il dump usa la collation `utf8mb4_unicode_ci`)
- Importare il database, eseguendo il file `f1_logistics_db.sql` contenuto nella cartella `database`
- Aggiornare i dati d'accesso al database nel file `connector.cnf` (dentro la cartella `database`)
- Eseguire il file `main.py` per avviare l'applicazione

## Configurazione

- Tutte le costanti dell'applicazione sono nel file `model/constants.py` e si possono modificare da lì:
  parametri del modello (α, β, ipotesi logistiche, valori di default, limite di 12 pacchetti)
  e valori del regolamento (scala ATR, tetti di spesa, supplemento gare), da cambiare solo se cambia il regolamento
- Costi, guadagni e lead time dei pacchetti, indici dei circuiti, probabilità di pioggia e tratte sono nel database, non in `constants.py`
- I risultati riportati nella relazione sono ottenuti con i valori consegnati: modificare le costanti cambia i risultati

Il video di dimostrazione di utilizzo del software è disponibile al seguente link di YouTube: https://youtu.be/n1bTftE29iw

## Dati e licenze

- I dati di base del database provengono dal dataset Kaggle [Formula 1 Complete Dataset 1950–2026](https://www.kaggle.com/datasets/patelris/formula-1-complete-dataset-1950-2026),
  derivato dall'API Jolpica F1 e rilasciato con licenza CC BY-NC-SA 4.0 (uso non commerciale, attribuzione, stessa licenza)
- Le tratte su strada derivano da dati © OpenStreetMap contributors (ODbL)
- La licenza del software è quella del file `LICENSE`
