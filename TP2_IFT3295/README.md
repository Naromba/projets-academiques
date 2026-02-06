
Description:

Ce dépôt contient une implémentation simplifiée de l'algorithme PLAST pour rechercher
des similarités entre une séquence d'entrée et une banque de séquences FASTA.

Prérequis

- Python 3.8+ installé
- Encodage des fichiers FASTA en UTF-8.
- Placez `tRNAs.fasta` et `unknown.fasta` dans le dossier `data/` (déjà en place).


Exécution

Le dépôt fournit un script helper `run.sh` (Merci Emeric!) qui :
- exécute un test rapide (écrit `results/test.txt`),
- parcourt `data/unknown.fasta` et génère un fichier de sortie par requête dans `results/`.

Pour lancer (depuis la racine du projet) :

./run.sh

Ou lancer directement le script Python (exemples) :

# analyser toutes les séquences du FASTA de requêtes
python3 src/plast.py --db data/tRNAs.fasta --query data/unknown.fasta

# analyser une séquence fournie en ligne de commande
python3 src/plast.py -db data/tRNAs.fasta -i CGTAGTCGGCTAACGCATACGCTTGATAAGCGTAAGAGCCC -E 5 -ss 10 -seed '11111111111'

Comportement de `run.sh`
------------------------
Le `run.sh` fourni va créer un dossier `results/` (s'il n'existe pas), lancer un test et ensuite traiter
chaque séquence contenue dans `data/unknown.fasta`. Pour chaque requête il écrit un fichier `results/<id>.txt`.

Options CLI utiles
Le script `src/plast.py` accepte les options courtes et longues :

- `-db, --db` : chemin vers la banque FASTA (par défaut `data/tRNAs.fasta`).
- `-q, --query` : chemin vers le FASTA de requêtes (par défaut `data/unknown.fasta`).
- `-i, --input_seq` : analyser une séquence brute fournie en argument (ignore `--query`).
- `--query_id` : identifiant utilisé lorsqu'on passe `-i` (nom de sortie).
- `-seed, --seed` : graine pour extraire les k-mers (ex. `11111111111`).
- `-E, --E` : seuil d'extension (ex. `4`).
- `-ss, --ss_threshold` : seuil d'e-value (ex. `1e-3`).

Exemples

Analyser le FASTA de requêtes et écrire les sorties :
./run.sh


Analyser une seule séquence et afficher sur la sortie standard :

python3 src/plast.py -db data/tRNAs.fasta -i ACGTACGT... -E 4 -ss 1e-3


Exemple de sortie
-----------------
Le script affiche pour chaque requête les HSPs significatifs (bitscore, e-value, positions et alignements locaux).


