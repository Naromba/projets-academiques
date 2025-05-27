  
# Nom(s) étudiant(s) / Name(s) of student(s): Rima Boujenane, Naromba Condé

import sys

# Espace pour fonctions auxillaires :
# Space for auxilary functions :



# Fonction à compléter / function to complete:
def solve(cost, forest):
    l = len(forest)

    # Cas de base : si la forêt est vide, le profit est 0
    if l == 0:
        return 0
    
    # Si la forêt ne contient qu'un arbre, on calcule le maximum entre le 
    # profit de cet arbre et 0
    if l == 1:
        return max(0, forest[0] - cost) 

    # Initialisation pour les deux premiers arbres :
    # Meilleur profit possible jusqu'à l'arbre numéro 0 (en ne coupant que lui)
    deux_prec = max(0, forest[0] - cost) 

    # Meilleur profit jusqu'à l'arbre 1 
    # (on choisit entre garder deux_prec ou couper seulement l'arbre 1)
    precedent = max(deux_prec, forest[1] - cost)  

    # On parcourt les arbres à partir du 3ème
    for i in range(2, l):
        # Soit on coupe l'arbre i et on ajoute son profit au meilleur score jusqu'à i-2
        # Soit on ne le coupe pas et on garde le meilleur score jusqu'à i-1
        actuel = max(forest[i] - cost + deux_prec, precedent)

        # Avancer les pointeurs pour la prochaine itération
        deux_prec = precedent
        precedent = actuel

    # À la fin, le meilleur profit est dans la variable precedent
    return precedent



# Ne pas modifier le code ci-dessous :
# Do not modify the code below :

def process_numbers(input_file):
    try:
        # Read integers from the input file
        with open(input_file, "r") as f:
            lines = f.readlines() 
            cost = int(lines[0].strip())  # cout d'exploitation pour couper un arbre
            forest = list(map(int, lines[1].split()))  # valeur de chaque arbre    

        return solve(cost, forest)
    
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python foresterie.py <input_file>")
        return

    input_file = sys.argv[1]

    print(f"Input File: {input_file}")
    res = process_numbers(input_file)
    print(f"Result: {res}")

if __name__ == "__main__":
    main()