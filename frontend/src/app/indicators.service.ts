/**
 * EN: Retrieve available months and backend-calculated indicators.
 * Each indicator request uses one observation month and an optional
 * subscription plan. Omitting the plan includes all subscriptions.
 * Errors are passed to the caller for display and retry handling.
 *
 * FR: Récupérer les mois disponibles et les indicateurs du backend.
 * Chaque demande utilise un mois d'observation et, éventuellement,
 * un abonnement. Omettre l'abonnement inclut tous les abonnements.
 * Les erreurs sont transmises au code appelant pour gérer l'affichage
 * et les nouvelles tentatives.
 */

import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  MonthlyIndicators,
  ObservationMonthsResponse,
  PlanComparisonsResponse,
  PlanSelection,
} from './indicators.models';

@Injectable({
  providedIn: 'root',
})
export class IndicatorsService {
  private readonly http = inject(HttpClient);

  getAvailableMonths(): Observable<ObservationMonthsResponse> {
    //EN: Retrieve available months, summary indicators and plan comparisons.
    // EN: Retrieve available months, summary indicators and plan comparisons.
    return this.http.get<ObservationMonthsResponse>(
      '/api/observation-months'
    );
  }

  getMonthlyIndicators(
    observationMonth: string,
    plan: PlanSelection = null,
  ): Observable<MonthlyIndicators> {
    // EN: Every request targets exactly one observation month.
    //FR: Récupérer les mois disponibles, les indicateurs et les comparaisons.
    const params: Record<string, string> = {
      observation_month: observationMonth,
    };

    // EN: Send a plan only when a specific subscription is selected.
    // FR: Envoyer un abonnement uniquement si un choix précis est fait.
    if (plan !== null) {
      params['plan'] = plan;
    }

    return this.http.get<MonthlyIndicators>('/api/indicators', {
      params,
    });
  }

    getPlanComparisons(
    observationMonth: string,
    plan: PlanSelection = null,
  ): Observable<PlanComparisonsResponse> {
    // EN: Use the same filter parameters as the summary indicators.
    // FR: Utiliser les mêmes paramètres que pour les indicateurs du résumé.
    const params: Record<string, string> = {
      observation_month: observationMonth,
    };

    // EN: All plans omits the plan parameter.
    // FR: All plans omet le paramètre d'abonnement.
    if (plan !== null) {
      params['plan'] = plan;
    }

    return this.http.get<PlanComparisonsResponse>(
      '/api/plan-comparisons',
      { params },
    );
  }
}