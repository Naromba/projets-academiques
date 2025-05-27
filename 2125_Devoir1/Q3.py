# Nom(s) étudiant(s) / Name(s) of student(s):
# Naromba Condé (20251772), Rima Boujenane (20235550)

import sys

# Espace pour fonctions auxillaires :
# Space for auxilary functions :

# Fonction auxilliaire pour calculer la mediane d'une liste triée
def get_median(numbers):
    n = len(numbers)
    # On ne renvoie rien si la liste est vide
    if n == 0:
        return None
    
    # Si la liste a un nombre impair d'éléments
    # on renvoie l'élément du milieu
    if n % 2 == 1:
        return numbers[n//2]
    
    # Si la liste a un nombre pair d'éléments
    # on renvoie la moyenne des deux éléments du milieu
    else:
        return (numbers[n//2 - 1] + numbers[n//2]) / 2
        

# Fonction auxilliaire qui renvoie toutes les paires distinctes
# de nombres dans une liste qui ont une somme égale à la médiane
def find_pairs(numbers, median):
    pairs = []
    left = 0
    right = len(numbers) - 1

    while left < right:
        sum = numbers[left] + numbers[right]

        if sum == median:
            # On ajoute la paire à la liste
            pairs.append((numbers[left], numbers[right]))

            # On memorise les valeurs pour éviter les doublons
            left_value = numbers[left]
            right_value = numbers[right]

            # On avance le pointeur de gauche tant qu'on a la même valeur
            while left < right and numbers[left] == left_value:
                left += 1

            # On recule le pointeur de droite tant qu'on a la même valeur
            while left < right and numbers[right] == right_value:
                right -= 1

        elif sum < median:
            # On avance le pointeur de gauche si la somme est trop petite

            left += 1
            # On recule le pointeur de droite si la somme est trop grande
        else:
            right -= 1

    return pairs

        
# Fonction à compléter / function to complete:
def solve(numbers):
    # Calculer la médiane de la liste
    median = get_median(numbers)
    if median is None:
        return []
    
    # Rechercher les paires de nombres qui ont une somme égale à la médiane
    pairs = find_pairs(numbers, median)

    return pairs



# Ne pas modifier le code ci-dessous :
# Do not modify the code below :

def process_numbers(input_file):
    try:
        # Read integers from the input file
        with open(input_file, "r") as f:
            content = f.read()
        
        # Convert content into a list of integers
        numbers = list(map(int, content.split()))

        pairs = solve(numbers)

        return(len(pairs))

    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python Q3.py <input_file>")
        return

    input_file = sys.argv[1]

    print(f"Input File: {input_file}")
    res = process_numbers(input_file)
    print(f"Result: {res}")

if __name__ == "__main__":
    main()
