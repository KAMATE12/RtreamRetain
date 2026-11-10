/**
 * EN: Test the dashboard's rendered content using controlled HTTP responses.
 * Cover loading, latest-month selection, rounding, zeros, missing data,
 * errors, retry and removal of stale results without contacting PostgreSQL.
 *
 * FR: Tester le contenu affiché avec des réponses HTTP contrôlées.
 * Couvrir le chargement, le dernier mois, les arrondis, les zéros,
 * les données absentes, les erreurs, la nouvelle tentative et le retrait
 * des anciens résultats, sans contacter PostgreSQL.
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { IndicatorsPanel } from './indicators-panel';
import { MonthlyIndicators } from './indicators.models';

describe('IndicatorsPanel', () => {
  let fixture: ComponentFixture<IndicatorsPanel>;
  let httpTesting: HttpTestingController;
  let element: HTMLElement;

  const monthsUrl = '/api/observation-months';
  const indicatorsUrl =
    '/api/indicators?observation_month=2026-09-01';

  const knownIndicators: MonthlyIndicators = {
    observation_month: '2026-09-01',
    cohort_size: 100,
    cancellation_count: 19,
    cancellation_rate: 19,
    average_viewing_hours: 57.1351,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IndicatorsPanel],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    httpTesting = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(IndicatorsPanel);
    element = fixture.nativeElement as HTMLElement;

    // EN: Render the component and trigger its initial request.
    // FR: Afficher le composant et déclencher sa requête initiale.
    fixture.detectChanges();
  });

  afterEach(() => {
    httpTesting.verify();
  });

  function text(): string {
    return (element.textContent ?? '').replace(/\s+/g, ' ').trim();
  }

  function displayedValues(): string[] {
    // EN: Read the four displayed indicator values in their defined order.
    // FR: Lire les quatre valeurs affichées dans leur ordre défini.
    return Array.from(element.querySelectorAll('dd')).map(
      (node) => (node.textContent ?? '').replace(/\s+/g, ' ').trim()
    );
  }

  function respondWithMonths(): void {
    httpTesting.expectOne(monthsUrl).flush({
      observation_months: ['2026-09-01', '2026-08-01'],
    });
  }

  function respondWithIndicators(
    result: MonthlyIndicators = knownIndicators
  ): void {
    httpTesting.expectOne(indicatorsUrl).flush(result);
    fixture.detectChanges();
  }

  it('shows loading without measured values during both requests', () => {
    expect(text()).toContain('Loading monthly indicators');
    expect(displayedValues()).toEqual([]);
    expect(
      element.querySelector('[aria-live]')?.getAttribute('aria-busy')
    ).toBe('true');

    respondWithMonths();
    fixture.detectChanges();

    // EN: Loading continues until the indicator response arrives.
    // FR: Le chargement continue jusqu'à la réponse des indicateurs.
    expect(text()).toContain('Loading monthly indicators');
    expect(displayedValues()).toEqual([]);

    respondWithIndicators();

    expect(element.querySelector('[role="status"]')).toBeNull();
    expect(
      element.querySelector('[aria-live]')?.getAttribute('aria-busy')
    ).toBe('false');
  });

  it('displays the latest month, API values and rounded average', () => {
    respondWithMonths();
    respondWithIndicators();

    expect(text()).toContain('Observation month: 2026-09');
    expect(displayedValues()).toEqual([
      '100',
      '19',
      '19%',
      '57.14 hours',
    ]);
    expect(text()).toContain('Synthetic data only.');
    expect(text()).toContain('All subscription plans.');
    expect(text()).toContain(
      'Associations do not establish causation or actual IVI behavior.'
    );
  });

  it('displays measured zeros instead of No data', () => {
    respondWithMonths();
    respondWithIndicators({
      ...knownIndicators,
      cohort_size: 1,
      cancellation_count: 0,
      cancellation_rate: 0,
      average_viewing_hours: 0,
    });

    expect(displayedValues()).toEqual(['1', '0', '0%', '0 hours']);
    expect(text()).not.toContain('No data');
    expect(text()).not.toContain(
      'No observations are available for this month.'
    );
  });

  it('displays zero counts and No data for an empty cohort', () => {
    respondWithMonths();
    respondWithIndicators({
      ...knownIndicators,
      cohort_size: 0,
      cancellation_count: 0,
      cancellation_rate: null,
      average_viewing_hours: null,
    });

    expect(text()).toContain('Observation month: 2026-09');
    expect(text()).toContain(
      'No observations are available for this month.'
    );
    expect(displayedValues()).toEqual([
      '0', '0', 'No data', 'No data',
    ]);
  });

  it('shows an empty state without requesting indicators when no months exist', () => {
    httpTesting.expectOne(monthsUrl).flush({
      observation_months: [],
    });
    fixture.detectChanges();

    httpTesting.expectNone(
      (request) => request.url === '/api/indicators'
    );

    expect(text()).toContain('No observation months are available.');
    expect(text()).not.toContain('Observation month:');
    expect(displayedValues()).toEqual([
      '0', '0', 'No data', 'No data',
    ]);
  });

  it.each(['months', 'indicators'] as const)(
    'recovers through the retry button after a %s request failure',
    (failedRequest) => {
      // EN: Exercise failure of either endpoint independently.
      // FR: Tester séparément l'échec de chacune des deux routes.
      if (failedRequest === 'indicators') {
        respondWithMonths();
      }

      const url =
        failedRequest === 'months' ? monthsUrl : indicatorsUrl;

      httpTesting.expectOne(url).flush(
        { detail: 'INTERNAL_TEST_DETAIL' },
        { status: 503, statusText: 'Service Unavailable' }
      );
      fixture.detectChanges();

      expect(text()).toContain(
        'Unable to load the indicators. Please try again.'
      );
      expect(text()).not.toContain('INTERNAL_TEST_DETAIL');
      expect(displayedValues()).toEqual([]);
      expect(text()).not.toContain('Observation month:');

      // EN: Use the actual button, not a direct call to the retry method.
      // FR: Utiliser le vrai bouton, sans appeler directement la méthode.
      const button = element.querySelector('button');
      expect(button).not.toBeNull();
      button!.click();
      fixture.detectChanges();

      expect(text()).toContain('Loading monthly indicators');
      expect(element.querySelector('[role="alert"]')).toBeNull();

      respondWithMonths();
      respondWithIndicators();

      expect(displayedValues()).toEqual([
        '100', '19', '19%', '57.14 hours',
      ]);
      expect(element.querySelector('[role="alert"]')).toBeNull();
      expect(element.querySelector('button')).toBeNull();
    }
  );

  it('removes previous results during a reload and after its failure', () => {
    respondWithMonths();
    respondWithIndicators();
    expect(displayedValues()).toHaveLength(4);

    // EN: Trigger another load to verify the stale-result protection.
    // FR: Déclencher un rechargement pour vérifier le retrait des anciens résultats.
    fixture.componentInstance.loadIndicators();
    fixture.detectChanges();

    expect(text()).toContain('Loading monthly indicators');
    expect(displayedValues()).toEqual([]);
    expect(text()).not.toContain('Observation month:');

    httpTesting.expectOne(monthsUrl).flush(
      {},
      { status: 503, statusText: 'Service Unavailable' }
    );
    fixture.detectChanges();

    expect(element.querySelector('[role="alert"]')).not.toBeNull();
    expect(displayedValues()).toEqual([]);
    expect(text()).not.toContain('57.14 hours');
  });
});