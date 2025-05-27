#include "MinCostRechargeCalculator.h"
#include <vector>
#include <math.h>
#include <iostream>
#include <algorithm> // for std::max

// Nom(s) étudiant(s) / Name(s) of student(s): Naromba Condé, Rima Boujenane

// ce fichier contient les definitions des methodes de la classe MinCostRechargeCalculator
// this file contains the definitions of the methods of the MinCostRechargeCalculator class

using namespace std;

MinCostRechargeCalculator::MinCostRechargeCalculator()
{
}

int MinCostRechargeCalculator::CalculateMinCostRecharge(const vector<int>& RechargeCost)
{
    int n = RechargeCost.size();

    // valeur très grande pour représenter l'infini sans risquer un débordement
    // recommandé sur LeetCode/Codeforces discussions
    const int INF = numeric_limits<int>::max() / 2;

    // coût minimum pour atteindre la position i (borne ou arrivée)
    vector<int> minCost(n + 2, INF);
    
    // départ : coût 0
    minCost[0] = 0;

    // remplir minCost pour chaque position (bornes + arrivée)
    for (int i = 1; i <= n + 1; ++i) {
        // le camion peut venir des 3 positions précédentes (i-1, i-2, i-3)
        for (int j = 1; j <= 3; ++j) {
            if (i - j >= 0) {
                int cost = minCost[i - j];
                // si on arrive sur une borne (pas à l'arrivée), on doit payer son prix
                if (i <= n) {
                    cost += RechargeCost[i - 1];
                }
                // mise à jour du coût minimum pour arriver à i
                minCost[i] = min(minCost[i], cost);
            }
        }
    }

    // coût minimum pour atteindre la destination
    return minCost[n + 1];
}