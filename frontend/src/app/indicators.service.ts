/**
 * EN: Connect the Angular interface to the monthly indicator API.
 * This service retrieves available observation months and the indicators
 * for a requested month, including all subscription plans.
 * Calculations remain in the backend. Errors are passed to the caller
 * so the interface can show an error message and offer a retry.
 *
 * FR: Relier l'interface Angular à l'API des indicateurs mensuels.
 * Ce service récupère les mois d'observation disponibles et les indicateurs
 * du mois demandé, pour tous les abonnements.
 * Les calculs restent dans le backend. Les erreurs sont transmises au code
 * appelant pour que l'interface affiche un message et propose de réessayer.
 */


import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  MonthlyIndicators,
  ObservationMonthsResponse,
} from './indicators.models';

@Injectable({
  providedIn: 'root',
})
export class IndicatorsService {
  private readonly http = inject(HttpClient);

  getAvailableMonths(): Observable<ObservationMonthsResponse> {
    // EN: Read the stored months in the order provided by the API.
    // FR: Lire les mois stockés dans l'ordre fourni par l'API.
    return this.http.get<ObservationMonthsResponse>(
      '/api/observation-months'
    );
  }

  getMonthlyIndicators(
    observationMonth: string
  ): Observable<MonthlyIndicators> {
    // EN: Omit the plan parameter to include all subscription plans.
    // FR: Omettre le paramètre plan pour inclure tous les abonnements.
    return this.http.get<MonthlyIndicators>('/api/indicators', {
      params: {
        observation_month: observationMonth,
      },
    });
  }
}