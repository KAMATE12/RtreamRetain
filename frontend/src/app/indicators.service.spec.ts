/**
 * EN: Verify indicator HTTP requests using controlled responses.
 * Check available-month ordering, month and plan parameters, switching
 * back to all plans, and preservation of unavailable indicator values.
 * No real API or database is contacted.
 *
 * FR: Vérifier les requêtes HTTP avec des réponses contrôlées.
 * Contrôler l'ordre des mois, les paramètres mois et abonnement,
 * le retour à tous les abonnements et les valeurs indisponibles.
 * Aucune API ni base de données réelle n'est contactée.
 */

import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { IndicatorsService } from './indicators.service';
import {
  MonthlyIndicators,
  SubscriptionPlan,
} from './indicators.models';

describe('IndicatorsService', () => {
  let service: IndicatorsService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        // EN: Replace real HTTP transport with controlled test requests.
        // FR: Remplacer le transport HTTP réel par des requêtes contrôlées.
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(IndicatorsService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // EN: Fail if an unexpected or unhandled request remains.
    // FR: Échouer si une requête inattendue ou non traitée subsiste.
    httpTesting.verify();
  });

  it('retrieves the available months in API order', () => {
    const expected = {
      observation_months: ['2026-10-01', '2026-09-01'],
    };

    let actual: unknown;

    service.getAvailableMonths().subscribe((response) => {
      actual = response;
    });

    const request = httpTesting.expectOne('/api/observation-months');
    expect(request.request.method).toBe('GET');

    // EN: Supply the response that would normally come from the API.
    // FR: Fournir la réponse normalement reçue de l'API.
    request.flush(expected);

    expect(actual).toEqual(expected);
  });

  it('requests the selected month for all plans and preserves nulls', () => {
    const expected: MonthlyIndicators = {
      observation_month: '2026-09-01',
      cohort_size: 0,
      cancellation_count: 0,
      cancellation_rate: null,
      average_viewing_hours: null,
    };

    let actual: MonthlyIndicators | undefined;

    service.getMonthlyIndicators('2026-09-01').subscribe((response) => {
      actual = response;
    });

    const request = httpTesting.expectOne(
      '/api/indicators?observation_month=2026-09-01'
    );

    expect(request.request.method).toBe('GET');

    // EN: An omitted plan includes all subscription plans.
    // FR: L'absence du paramètre plan inclut tous les abonnements.
    expect(request.request.params.has('plan')).toBe(false);

    request.flush(expected);

    // EN: Unavailable values must remain null rather than becoming zero.
    // FR: Les valeurs indisponibles doivent rester null, et non devenir zéro.
    expect(actual).toEqual(expected);
  });

  const plans: SubscriptionPlan[] = ['Basic', 'Standard', 'Premium'];

  it.each(plans)(
    'forwards the selected month and %s plan without changing API values',
    (plan) => {
      const expected: MonthlyIndicators = {
        observation_month: '2026-10-01',
        cohort_size: 8,
        cancellation_count: 1,
        cancellation_rate: 12.5,
        average_viewing_hours: 23.456,
      };

      let actual: MonthlyIndicators | undefined;

      service.getMonthlyIndicators('2026-10-01', plan)
        .subscribe((response) => {
          actual = response;
        });

      // EN: Match the endpoint independently of query-parameter order.
      // FR: Identifier l'adresse sans dépendre de l'ordre des paramètres.
      const request = httpTesting.expectOne(
        (candidate) => candidate.url === '/api/indicators'
      );

      expect(request.request.method).toBe('GET');
      expect(request.request.params.get('observation_month'))
        .toBe('2026-10-01');
      expect(request.request.params.get('plan')).toBe(plan);
      expect(request.request.params.keys().sort())
        .toEqual(['observation_month', 'plan']);

      request.flush(expected);

      // EN: The service forwards values; display rounding belongs to the UI.
      // FR: Le service transmet les valeurs ; l'interface gère leur arrondi.
      expect(actual).toEqual(expected);
    }
  );

  it('omits the plan when returning to all plans after a filtered request', () => {
    const filtered: MonthlyIndicators = {
      observation_month: '2026-09-01',
      cohort_size: 2,
      cancellation_count: 1,
      cancellation_rate: 50,
      average_viewing_hours: 20,
    };

    const allPlans: MonthlyIndicators = {
      observation_month: '2026-09-01',
      cohort_size: 4,
      cancellation_count: 1,
      cancellation_rate: 25,
      average_viewing_hours: 30,
    };

    // EN: First complete a request restricted to Basic.
    // FR: Terminer d'abord une demande limitée à Basic.
    service.getMonthlyIndicators('2026-09-01', 'Basic').subscribe();

    const filteredRequest = httpTesting.expectOne(
      (candidate) => candidate.url === '/api/indicators'
    );

    expect(filteredRequest.request.params.get('plan')).toBe('Basic');
    filteredRequest.flush(filtered);

    let actual: MonthlyIndicators | undefined;

    // EN: Explicit null represents the user's All plans selection.
    // FR: Null représente explicitement le choix All plans de l'utilisateur.
    service.getMonthlyIndicators('2026-09-01', null)
      .subscribe((response) => {
        actual = response;
      });

    const allPlansRequest = httpTesting.expectOne(
      (candidate) => candidate.url === '/api/indicators'
    );

    expect(allPlansRequest.request.method).toBe('GET');
    expect(allPlansRequest.request.params.get('observation_month'))
      .toBe('2026-09-01');
    expect(allPlansRequest.request.params.has('plan')).toBe(false);
    expect(allPlansRequest.request.params.keys())
      .toEqual(['observation_month']);

    allPlansRequest.flush(allPlans);

    expect(actual).toEqual(allPlans);
  });
});