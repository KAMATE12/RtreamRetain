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
  PlanSelection,
} from './indicators.models';

@Injectable({
  providedIn: 'root',
})
export class IndicatorsService {
  private readonly http = inject(HttpClient);

  getAvailableMonths(): Observable<ObservationMonthsResponse> {
    // EN: Preserve the newest-first order supplied by the API.
    // FR: Conserver l'ordre décroissant des mois fourni par l'API.
    return this.http.get<ObservationMonthsResponse>(
      '/api/observation-months'
    );
  }

  getMonthlyIndicators(
    observationMonth: string,
    plan: PlanSelection = null,
  ): Observable<MonthlyIndicators> {
    // EN: Every request targets exactly one observation month.
    // FR: Chaque demande concerne exactement un mois d'observation.
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
}