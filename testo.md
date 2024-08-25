Per formalizzare il problema in modo da risolvere il punto 1, dobbiamo definire chiaramente il dominio del problema e i suoi componenti chiave. Questo implica specificare gli stati del problema, le azioni possibili, le transizioni tra gli stati, e il criterio per determinare se un certo stato è uno stato "goal" (obiettivo).

### Formalizzazione del Problema

1. **Descrizione del Dominio del Problema:**
   Il problema riguarda la classificazione di lettere e cifre scritte a mano utilizzando dataset come MNIST/eMNIST. Dato un insieme di immagini, ogni immagine rappresenta una lettera maiuscola o una cifra. L'obiettivo è identificare correttamente tutte le lettere e le cifre nelle immagini e organizzare i risultati secondo una specifica rappresentazione o sequenza.

2. **Stati del Problema:**

   - **Stato Iniziale (`stato_iniziale`):** 
     Lo stato iniziale è una rappresentazione delle immagini così come sono fornite all'inizio. Per ogni immagine, viene determinato il simbolo (lettera maiuscola o cifra) presente, utilizzando un modello di classificazione (ad esempio, una rete neurale convoluzionale). Lo stato iniziale è quindi una griglia o un vettore che rappresenta la disposizione e il tipo di simboli identificati.

     \[
     S_{\text{iniziale}} = \{s_1, s_2, \ldots, s_n\}
     \]

     dove \(s_i\) rappresenta l'identificazione del simbolo nell'immagine \(i\)-esima.

   - **Stato Goal (`stato_goal`):**
     Lo stato goal è una configurazione desiderata dei simboli. Potrebbe essere una disposizione ordinata alfabeticamente, numericamente, o secondo qualche criterio specifico (ad esempio, tutte le lettere prima di tutte le cifre, o viceversa).

     \[
     S_{\text{goal}} = \{g_1, g_2, \ldots, g_n\}
     \]

     dove \(g_i\) rappresenta la posizione desiderata del simbolo nella sequenza goal.

3. **Azioni:**

   Le azioni possibili sono le operazioni che possono essere eseguite per trasformare uno stato in un altro. Nel contesto della classificazione e organizzazione delle immagini:

   - **Riconoscimento del Simbolo:** Utilizzare un modello di machine learning per classificare l'immagine e identificare la lettera maiuscola o la cifra rappresentata.
   - **Spostamento del Simbolo:** Cambiare la posizione di un simbolo nella griglia o sequenza per avvicinarsi allo stato goal.
   - **Rimozione/Aggiunta di Simboli:** (Se applicabile) Aggiungere o rimuovere simboli dalla griglia/sequenza.

4. **Transizioni tra Stati:**

   Le transizioni tra gli stati sono determinate dalle azioni sopra descritte. Se uno stato \(S_i\) è rappresentato da una sequenza di simboli, allora una transizione a un nuovo stato \(S_{i+1}\) può comportare:

   - Riconoscimento corretto di un simbolo, aggiornando l'identificazione nel vettore o nella griglia.
   - Cambiare la posizione di un simbolo nella griglia o sequenza.

   Matematicamente, una transizione può essere rappresentata come:

   \[
   S_{i+1} = T(S_i, a)
   \]

   dove \(T\) è la funzione di transizione che applica l'azione \(a\) allo stato \(S_i\) per produrre un nuovo stato \(S_{i+1}\).

5. **Funzione Costo:**

   La funzione costo può essere definita in termini di numero di mosse necessarie per raggiungere lo stato goal o il costo computazionale associato al riconoscimento dei simboli e alla riorganizzazione delle immagini.

   \[
   C(S_i, a) = \text{costo dell'azione } a \text{ applicata allo stato } S_i
   \]

6. **Funzione Obiettivo (Goal Test):**

   La funzione obiettivo verifica se uno stato attuale coincide con lo stato goal.

   \[
   \text{Goal}(S) = 
   \begin{cases} 
   \text{True} & \text{se } S = S_{\text{goal}} \\
   \text{False} & \text{altrimenti}
   \end{cases}
   \]

7. **Criterio di Ottimizzazione:**

   Il problema può essere risolto ottimizzando in termini di:

   - **Numero di Azioni (Lunghezza della Soluzione):** Minimizzare il numero di spostamenti o cambiamenti di posizione necessari per raggiungere lo stato goal.
   - **Costo Totale della Soluzione:** Minimizzare il costo computazionale totale associato alla sequenza di azioni eseguite.

### Passi Successivi per la Risoluzione del Problema

- **Classificazione delle Immagini:** Addestra un modello per riconoscere lettere e cifre, e usalo per generare lo stato iniziale.
- **Implementazione degli Algoritmi di Ricerca:** Scegli e implementa algoritmi di ricerca informata (come A*) e non informata (come BFS o DFS) per esplorare lo spazio degli stati.
- **Simulazione delle Azioni:** Utilizza OpenCV o un'altra libreria di visualizzazione per creare una sequenza di immagini che mostra il processo di trasformazione dallo stato iniziale allo stato goal.

### Conclusione

Questa formalizzazione definisce chiaramente il dominio del problema e i suoi componenti chiave, consentendo di sviluppare soluzioni algoritmiche per la classificazione e l'organizzazione di lettere e cifre. È un buon punto di partenza per implementare il progetto e confrontare diversi approcci algoritmici.