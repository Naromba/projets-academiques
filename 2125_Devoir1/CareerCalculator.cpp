#include "CareerCalculator.h"
#include <vector>
#include <math.h>
#include <iostream>

// Naromba Condé (20251772), Rima Boujenane (20235550)
// ce fichier contient les definitions des methodes de la classe CareerCalculator
// this file contains the definitions of the methods of the CareerCalculator class

using namespace std;

CareerCalculator::CareerCalculator()
{
}

bool CareerCalculator::CalculateMaxCareer(const vector<int>& Steps) {
    int n = Steps.size();
    int maxReach = 0;
    
    // On parcourt chaque case
    for (int i = 0; i < n; i++) {
        // Si la case actuelle n'est pas atteignable, on ne peut plus avancer 
        if (i > maxReach) {
            return false; }
        
        // On met à jour la portée maximale que l'on peut atteindre à partir 
        // de la position actuelle
        maxReach = max(maxReach, i + Steps[i]);
        
        // Si on peut atteindre ou dépasser la dernière case, l'objectif est réalisable
        if (maxReach >= n - 1) {
            return true;
        }
    }
    
    // Si la boucle se termine sans atteindre la dernière case, l'objectif n'est pas réalisable
    return false;
}

