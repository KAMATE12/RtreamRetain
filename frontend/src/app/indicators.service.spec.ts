/**
 * EN: Verify the indicator service's HTTP requests using controlled responses.
 * No real API or database is contacted. These tests check endpoint addresses,
 * month forwarding and preservation of unavailable indicator values.
 *
 * FR: Vérifier les requêtes HTTP du service avec des réponses contrôlées.
 * Aucune API ni base réelle n'est contactée. Ces tests contrôlent les adresses,
 * la transmission du mois et la conservation des valeurs indisponibles.
 */

import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { IndicatorsService } from './indicators.service';
import { MonthlyIndicators } from './indicators.models';

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
});