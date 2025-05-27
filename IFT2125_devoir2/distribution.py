
# Nom(s) étudiant(s) / Name(s) of student(s): Rima Boujenane, Naromba Condé

import sys



# Espace pour fonctions auxillaires :
# Space for auxilary functions :

# Calcule l'excès de jetons du sous-arbre dont noeud est la racine
def calcul_exces(noeud, compteur):
    if not noeud:
        return 0

    # calculer l'excès du sous-arbre gauche
    exces_gauche = calcul_exces(noeud.left, compteur)
    # calculer l'excès du sous-arbre droit
    exces_droit = calcul_exces(noeud.right, compteur)

    # chaque déplacement de jeton est comptabilisé
    compteur[0] += abs(exces_gauche) + abs(exces_droit)

    # retourne l'excès du noeud actuel :
    # (nombre de jetons dans ce noeud + excès gauche + excès droit) - 1 jeton attendu
    return noeud.val - 1 + exces_gauche + exces_droit

# Fonction à compléter / function to complete:
def solve(root):
    compteur = [0]  # compteur[0] contiend le nombre total de transactions
    calcul_exces(root, compteur)
    return compteur[0]
    

# Ne pas modifier le code ci-dessous :
# Do not modify the code below :

# Ne pas modifier le code ci-dessous :

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def process_numbers(input_file):
    try:
        # Read integers from the input file
        with open(input_file, "r") as f:
            lines = f.readlines() 
            tree_list = list(map(int, lines[0].split()))  # valeur de chaque noeud
            root = build_tree(tree_list)

        return solve(root)
    
    except Exception as e:
        print(f"Error: {e}")

def build_tree(lst):
    if not lst:
        return None
    
    root = TreeNode(lst[0])
    queue = [root]
    i = 1
    
    while i < len(lst):
        node = queue.pop(0)
        
        if i < len(lst):
            node.left = TreeNode(lst[i])
            queue.append(node.left)
            i += 1
        
        if i < len(lst):
            node.right = TreeNode(lst[i])
            queue.append(node.right)
            i += 1
    
    return root

def print_tree(root):
    if not root:
        return
    current_level = [root]
    while current_level:
        next_level = []
        values = []
        for node in current_level:
            if node:
                values.append(str(node.val))
                if node.left != None :
                    next_level.append(node.left)
                if node.right != None :
                    next_level.append(node.right)
        print(" ".join(values))
        current_level = next_level

def main():
    if len(sys.argv) != 2:
        print("Usage: python distribution.py <input_file>")
        return

    input_file = sys.argv[1]

    print(f"Input File: {input_file}")
    res = process_numbers(input_file)
    print(f"Result: {res}")

if __name__ == "__main__":
    main()
