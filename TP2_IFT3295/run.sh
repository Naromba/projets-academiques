# ==============================================================================
# Ce script nécessite que votre projet respecte la structure suivante :
# ==============================================================================
#
# TP2_IFT3295/
#   ├── requirements.txt
#   ├── run.sh
#   ├── data/
#   │   ├── tRNAs.fasta
#   │   └── unknown.fasta
#   └── src/
#       ├── plast.py
#       └── [autres fichiers Python]
#
# ==============================================================================


# Si le dossier results n'existe pas, le créer
if [ ! -d "./results" ]; then
    mkdir results
fi

# Roule le programme avec le test donné dans le pdf
python3 src/plast.py -i CGTAGTCGGCTAACGCATACGCTTGATAAGCGTAAGAGCCC -db ./data/tRNAs.fasta -E 5 -ss 10 -seed '11111111111' > ./results/test.txt

# Traiter chaque séquence dans unknown.fasta et enregistrer les résultats dans des fichiers séparés
current_name=""
current_sequence=""
while IFS= read -r line || [ -n "$line" ]; do
    if [[ "$line" =~ ^\> ]]; then
        [ -n "$current_name" ] && [ -n "$current_sequence" ] && \
            python3 src/plast.py -i "$current_sequence" -db ./data/tRNAs.fasta -E 4 -ss 0.001 -seed '11111111111' > "./results/${current_name##*|}.txt"
        current_name="${line#>}"
        current_sequence=""
    else
        current_sequence="${current_sequence}${line}"
    fi
done < ./data/unknown.fasta

# Traiter la dernière séquence après la fin du fichier
[ -n "$current_name" ] && [ -n "$current_sequence" ] && \
    python3 src/plast.py -i "$current_sequence" -db ./data/tRNAs.fasta -E 4 -ss 0.001 -seed '11111111111' > "./results/${current_name##*|}.txt"

echo "Les résultats sont disponibles dans le dossier results"
