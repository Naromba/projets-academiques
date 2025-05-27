#include "MaxToysCalculator.h"
#include <vector>
#include <math.h>
#include <iostream>

// Rima Boujenane (20235550), Naromba Condé (20251772)
// ce fichier contient les definitions des methodes de la classe MaxToysCalculator
// this file contains the definitions of the methods of the MaxToysCalculator class

using namespace std;

MaxToysCalculator::MaxToysCalculator()
{
}

int MaxToysCalculator::CalculateMaxToys(const vector<int>& Toys, int S) {
    int n = static_cast<int>(Toys.size());
    int maxSegment = 0;
    int currentSum = 0;
    int left = 0;

  // Parcours de tous les jouets
    for (int right = 0; right < n; right++)
    {
        // On ajoute le prix du jouet à l'indice "right" à la somme
        currentSum += Toys[right];

        // Tant que la somme dépasse le budget, on retire des jouets
        // depuis le debut
        while (left <= right && currentSum > S)
        {   currentSum -= Toys[left];
            left++; // On déplace le début de la fenêtre vers la droite
        }
        // Mise à jour de la longueur maximale du segment
        maxSegment = max(maxSegment, right - left + 1);
    }

    return maxSegment;
}
