
# Nom(s) étudiant(s) / Name(s) of student(s):Rima Boujenane, Naromba Condé

import sys
# seuil utilisé par défaut
SEUIL = 8

# Espace pour fonctions auxillaires :
# Space for auxilary functions :
def insertion_sort(tab, gauche, droite):
    #Tri par insertion en place sur la partie [gauche, droite]
    for i in range (gauche + 1, droite):
        cle = tab[i]
        j = i - 1
        while j >= gauche and tab[j] > cle:
            tab[j + 1] = tab[j]
            j -= 1
        tab[j + 1] = cle

def fusion(tab, gauche, milieu, droite, tampon):
    #Fusionne tab[g:m] et tab[m:d] dans l’ordre croissant
    i,j,k = gauche, milieu, gauche
    while i < milieu and j < droite:
        if tab[i] <= tab[j]:
            tampon[k] = tab[i]
            i += 1
        else:
            tampon[k] = tab[j]
            j += 1
        k += 1

    while i < milieu:
        tampon[k] = tab[i]
        i += 1
        k += 1
    
    while j < droite:
        tampon[k] = tab[j]
        j += 1
        k += 1

    # recopie dans le tableau principal
    tab[gauche:droite] = tampon[gauche:droite]

def tri_hybride(tab, gauche, droite, tampon):
    #Tri fusion récursif qui bascule sur insertion si (d-g) ≤ SEUIL
    if droite - gauche <= SEUIL:
        insertion_sort(tab, gauche, droite)
        return
    
    milieu = (gauche + droite) // 2
    tri_hybride(tab, gauche, milieu, tampon)
    tri_hybride(tab, milieu, droite, tampon)
    fusion(tab, gauche, milieu, droite, tampon)
      
    
# Fonction à compléter / function to complete:
def solve(array) :
    #  Trie le tableau et renvoie la version triée
    tampon = [0] * len(array)  # tableau tampon de la même taille que array
    # On appelle la fonction de tri hybride
    tri_hybride(array, 0, len(array), tampon)
    # On renvoie le tableau trié
    return array

# Ne pas modifier le code ci-dessous :
# Do not modify the code below :

def process_numbers(input_file):
    try:
        # Read integers from the input file
        with open(input_file, "r") as f:
            lines = f.readlines() 
            array = list(map(int, lines[0].split()))  # valeur de chaque noeud  

        return solve(array)
    
    except Exception as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tri_hybride.py <input_file>")
        return

    input_file = sys.argv[1]

    print(f"Input File: {input_file}")
    res = process_numbers(input_file)
    print(f"Result: {res}")

if __name__ == "__main__":
    main()
