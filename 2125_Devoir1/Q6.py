# Nom(s) étudiant(s) / Name(s) of student(s): 
# Naromba Condé (20251772), Rima Boujenane (20235550)


import sys

# Espace pour fonctions auxillaires :
# Space for auxilary functions :

# fonction pour calculer la médiane d'une liste triée
def median(arr):
    n = len(arr)
    if n % 2 == 1:
        return arr[n // 2]
    else:
        return (arr[n // 2 - 1] + arr[n // 2]) / 2


# Fonction à compléter / function to complete:
def solve(nums1, nums2):
    # si nums1 est vide, on retourne la mediane de nums2
    if nums1 == []: 
        return median(nums2)
    
    # si nums2 est vide, on retourne la mediane de nums1
    if nums2 == []:
        return median(nums1)
    
    # si nums1 est plus grand que nums2, on les échange
    # cela fait en sorte que la recherche de la médiane se fait sur le tableau 
    # le plus court qui est nums1
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    size1= len(nums1)
    size2 = len(nums2)
    half_size = (size1 + size2 + 1) // 2

    left = 0 # borne inférieure
    right = size1 # borne supérieure

    while left <= right:
        i = (left + right) // 2 # position de la partition dans nums1
        j = half_size - i # position de la partition dans nums2

        # si la partition de nums1 est plus petite que la partition de nums2
        if i < size1 and nums2[j - 1] > nums1[i]: 
            left = i + 1 # on déplace la borne inférieure vers la droite

        # si la partition de nums1 est plus grande que la partition de nums2
        elif i > 0 and nums1[i - 1] > nums2[j]: 
            right = i - 1 # on déplace la borne supérieure vers la gauche
 
        # si on a trouvé la bonne partition
        else:
            # on détermine le maximum de la partition de gauche :

            # si i == 0, il n'y a aucun élément dans nums1 à gauche de 
            # la partition, on prend alors le plus grand élément à gauche 
            # dans nums2
            if i == 0: 
                left_max = nums2[j - 1] 

            # si j == 0, il n'y a aucun élément dans nums2 à gauche de 
            # la partition, on prend alors le plus grand élément à gauche 
            # dans nums1
            elif j == 0:
                left_max = nums1[i - 1]

            # sinon, on prend le maximum entre les deux éléments à gauche de la partition
            else:
                left_max = max(nums1[i - 1], nums2[j - 1])

            # si la somme de la taille des deux tableaux est impaire
            if (size1 + size2) % 2 == 1:
                # on retourne le maximum de la partition de gauche, qui est
                # dans ce cas la médiane
                return left_max 
            

            # on détermine le minimum de la partition de droite :

            # si i == size1, il n'y a aucun élément dans nums1 à droite de
            # la partition, on prend alors le plus petit élément à droite 
            # dans nums2
            if i == size1:
                right_min = nums2[j]

            # si j == size2, il n'y a aucun élément dans nums2 à droite de
            # la partition, on prend alors le plus petit élément à droite
            # dans nums1
            elif j == size2:
                right_min = nums1[i]

            # sinon, on prend le minimum entre les deux éléments à droite 
            # de la partition
            else:
                right_min = min(nums1[i], nums2[j])

             
            # on retourne la médiane qui est la moyenne des deux éléments 
            # centraux (left_max et right_min)
            return (left_max + right_min) / 2



# Ne pas modifier le code ci-dessous :
# Do not modify the code beleft :

def process_numbers(input_file):
    try:
        # Read integers from the input file
        with open(input_file, "r") as f:
            lines = f.readlines() 
            l0 = list(map(int, lines[0].split()))    
            l1 = list(map(int, lines[1].split()))    

        return solve(l0,l1)
    
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python Q6.py <input_file>")
        return

    input_file = sys.argv[1]

    print(f"Input File: {input_file}")
    res = process_numbers(input_file)
    print(f"Result: {res}")

if __name__ == "__main__":
    main()