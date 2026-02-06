IFT3325 - Devoir2

Prérequis : Python 3.10+ (macOS testé). Aucune dépendance externe.
Depuis le dossier `Devoir2` :

1) Créer les logs (une seule fois) :
   mkdir -p logs

2) Tester le bit-stuffing :
   python3 -m code.test_stuffing > logs/stuffing_test.txt 2>&1

3) Lancer un scénario (1, 2 ou 3) et logger :
   python3 -m code.protocole 1 > logs/scenario_1.txt 2>&1
   (sans log) python3 -m code.protocole 1   # remplacer 1 par 2 ou 3

4) Tout exécuter (scénarios + test4) :
   python3 run_experiments.py

Paramètres utiles (facultatif) :
- Dans `code/protocole.py` : `TIMEOUT_MS`, `SCENARIOS` (probErreur, probPerte, delaiMax)
- Dans `code/Canal.py`    : probabilités d'erreur/perte, delaiMax
- Dans `code/stuffing.py` : option `msb_first`

