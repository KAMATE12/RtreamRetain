/**
 * EN: Verify rendered filters and indicators using controlled HTTP responses.
 * Cover two months, multiple plans, empty results, retry, stale-value removal
 * and cancellation of obsolete requests. No real database is contacted.
 *
 * FR: Vérifier les filtres et indicateurs avec des réponses HTTP contrôlées.
 * Couvrir deux mois, plusieurs abonnements, les résultats vides, les erreurs,
 * les nouvelles tentatives et l'annulation des demandes dépassées.
 * Aucune base de données réelle n'est contactée.
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { IndicatorsPanel } from './indicators-panel';
import {
  MonthlyIndicators,
  PlanSelection,
} from './indicators.models';

describe('IndicatorsPanel', () => {
  let fixture: ComponentFixture<IndicatorsPanel>;
  let httpTesting: HttpTestingController;
  let element: HTMLElement;

  const september = '2026-09-01';
  const october = '2026-10-01';
  const monthsUrl = '/api/observation-months';

  // EN: Expected responses are written explicitly, not recalculated by tests.
  // FR: Les réponses attendues sont explicites, sans recalcul dans les tests.
  const septemberAll: MonthlyIndicators = {
    observation_month: september,
    cohort_size: 4,
    cancellation_count: 1,
    cancellation_rate: 25,
    average_viewing_hours: 30,
  };

  const septemberBasic: MonthlyIndicators = {
    observation_month: september,
    cohort_size: 2,
    cancellation_count: 1,
    cancellation_rate: 50,
    average_viewing_hours: 20,
  };

  const septemberPremium: MonthlyIndicators = {
    observation_month: september,
    cohort_size: 2,
    cancellation_count: 0,
    cancellation_rate: 0,
    average_viewing_hours: 40,
  };

  const octoberAll: MonthlyIndicators = {
    observation_month: october,
    cohort_size: 2,
    cancellation_count: 1,
    cancellation_rate: 50,
    average_viewing_hours: 10,
  };

  const octoberBasic: MonthlyIndicators = {
    observation_month: october,
    cohort_size: 1,
    cancellation_count: 0,
    cancellation_rate: 0,
    average_viewing_hours: 0,
  };

  const octoberPremium: MonthlyIndicators = {
    observation_month: october,
    cohort_size: 1,
    cancellation_count: 1,
    cancellation_rate: 100,
    average_viewing_hours: 20,
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
    fixture.detectChanges();
  });

  afterEach(() => {
    httpTesting.verify();
  });

  function text(): string {
    return (element.textContent ?? '').replace(/\s+/g, ' ').trim();
  }

  function values(): string[] {
    return Array.from(element.querySelectorAll('dd')).map(
      (node) => (node.textContent ?? '').replace(/\s+/g, ' ').trim()
    );
  }

  function select(id: string): HTMLSelectElement {
    const control = element.querySelector<HTMLSelectElement>(`#${id}`);
    expect(control).not.toBeNull();
    return control!;
  }

  function change(id: string, value: string): void {
    // EN: Exercise the actual HTML control and its change event.
    // FR: Utiliser le vrai contrôle HTML et son événement de changement.
    const control = select(id);
    control.value = value;
    control.dispatchEvent(new Event('change', { bubbles: true }));
    fixture.detectChanges();
  }

  function respondWithMonths(): void {
    httpTesting.expectOne(monthsUrl).flush({
      observation_months: [october, september],
    });
    fixture.detectChanges();
  }

  function expectIndicators(month: string, plan: PlanSelection = null) {
    const request = httpTesting.expectOne(
      (candidate) =>
        candidate.url === '/api/indicators' &&
        candidate.params.get('observation_month') === month &&
        candidate.params.get('plan') === plan
    );
    expect(request.request.method).toBe('GET');
    return request;
  }

  function respond(
    result: MonthlyIndicators,
    plan: PlanSelection = null,
  ): void {
    expectIndicators(result.observation_month, plan).flush(result);
    fixture.detectChanges();
  }

  function initialize(): void {
    respondWithMonths();
    respond(octoberAll);
  }

  function retry(): void {
    const button = element.querySelector<HTMLButtonElement>('button');
    expect(button).not.toBeNull();
    button!.click();
    fixture.detectChanges();
  }

  it('shows loading without measured values during both initial requests', () => {
    expect(text()).toContain('Loading monthly indicators');
    expect(values()).toEqual([]);

    respondWithMonths();

    expect(values()).toEqual([]);
    expect(
      element.querySelector('[aria-live]')?.getAttribute('aria-busy')
    ).toBe('true');

    respond(octoberAll);

    expect(
      element.querySelector('[aria-live]')?.getAttribute('aria-busy')
    ).toBe('false');
    expect(element.querySelector('[role="status"]')).toBeNull();
  });

  it('populates months and four plans with the documented defaults', () => {
    initialize();

    expect(
      Array.from(select('observation-month').options).map(
        (option) => option.value
      )
    ).toEqual([october, september]);

    expect(
      Array.from(select('subscription-plan').options).map(
        (option) => option.textContent
      )
    ).toEqual(['All plans', 'Basic', 'Standard', 'Premium']);

    expect(select('observation-month').value).toBe(october);
    expect(select('subscription-plan').value).toBe('');
    expect(values()).toEqual(['2', '1', '50%', '10 hours']);
    expect(text()).toContain('Observation month: 2026-10');
    expect(text()).toContain('Subscription plan: All plans');
    expect(text()).toContain('Synthetic data only.');
    expect(text()).toContain(
      'Associations do not establish causation or actual IVI behavior.'
    );
  });

  it('rounds API values only for display', () => {
    respondWithMonths();
    respond({
      ...octoberAll,
      average_viewing_hours: 57.1351,
    });

    expect(values()).toEqual(['2', '1', '50%', '57.14 hours']);
  });

  it('requests another month and hides previous results while loading', () => {
    initialize();
    change('observation-month', september);

    expect(values()).toEqual([]);
    expect(text()).toContain('Observation month: 2026-09');
    expect(text()).toContain('Loading monthly indicators');

    respond(septemberAll);

    expect(values()).toEqual(['4', '1', '25%', '30 hours']);
    httpTesting.expectNone(monthsUrl);
  });

  it('applies plan changes to all values and restores all-plan results', () => {
    initialize();

    change('subscription-plan', 'Premium');
    respond(octoberPremium, 'Premium');
    expect(values()).toEqual(['1', '1', '100%', '20 hours']);
    expect(text()).toContain('Subscription plan: Premium');

    change('subscription-plan', '');
    respond(octoberAll);
    expect(values()).toEqual(['2', '1', '50%', '10 hours']);
    expect(text()).toContain('Subscription plan: All plans');
  });

  it('preserves Basic when changing months and displays measured zeros', () => {
    initialize();

    change('subscription-plan', 'Basic');
    respond(octoberBasic, 'Basic');
    expect(values()).toEqual(['1', '0', '0%', '0 hours']);
    expect(text()).not.toContain('No data');

    change('observation-month', september);
    expect(select('subscription-plan').value).toBe('Basic');

    respond(septemberBasic, 'Basic');
    expect(values()).toEqual(['2', '1', '50%', '20 hours']);
    expect(text()).toContain('Observation month: 2026-09');
    expect(text()).toContain('Subscription plan: Basic');
  });

  it('displays the known Premium results for September', () => {
    initialize();
    change('observation-month', september);
    respond(septemberAll);

    change('subscription-plan', 'Premium');
    respond(septemberPremium, 'Premium');

    expect(values()).toEqual(['2', '0', '0%', '40 hours']);
  });

  it('keeps an absent plan selected and displays No data across months', () => {
    initialize();
    change('subscription-plan', 'Standard');

    respond({
      observation_month: october,
      cohort_size: 0,
      cancellation_count: 0,
      cancellation_rate: null,
      average_viewing_hours: null,
    }, 'Standard');

    expect(values()).toEqual(['0', '0', 'No data', 'No data']);
    expect(text()).toContain(
      'No observations are available for this month and plan selection.'
    );

    change('observation-month', september);
    expect(select('subscription-plan').value).toBe('Standard');

    respond({
      observation_month: september,
      cohort_size: 0,
      cancellation_count: 0,
      cancellation_rate: null,
      average_viewing_hours: null,
    }, 'Standard');

    expect(values()).toEqual(['0', '0', 'No data', 'No data']);
    expect(text()).toContain('Subscription plan: Standard');
  });

  it('does not request indicators when no observation months exist', () => {
    httpTesting.expectOne(monthsUrl).flush({ observation_months: [] });
    fixture.detectChanges();

    httpTesting.expectNone(
      (request) => request.url === '/api/indicators'
    );
    expect(element.querySelector('select')).toBeNull();
    expect(text()).toContain('No observation months are available.');
    expect(values()).toEqual(['0', '0', 'No data', 'No data']);
  });

  it('retries month discovery after its initial failure', () => {
    httpTesting.expectOne(monthsUrl).flush(
      { detail: 'INTERNAL_TEST_DETAIL' },
      { status: 503, statusText: 'Service Unavailable' }
    );
    fixture.detectChanges();

    expect(text()).not.toContain('INTERNAL_TEST_DETAIL');
    expect(element.querySelector('[role="alert"]')).not.toBeNull();

    retry();
    respondWithMonths();
    respond(octoberAll);

    expect(values()).toEqual(['2', '1', '50%', '10 hours']);
    expect(element.querySelector('[role="alert"]')).toBeNull();
  });

  it('preserves filters after failure and retries the current selection', () => {
    initialize();
    change('observation-month', september);
    respond(septemberAll);
    change('subscription-plan', 'Basic');

    expectIndicators(september, 'Basic').flush(
      { detail: 'INTERNAL_TEST_DETAIL' },
      { status: 503, statusText: 'Service Unavailable' }
    );
    fixture.detectChanges();

    expect(values()).toEqual([]);
    expect(select('observation-month').value).toBe(september);
    expect(select('subscription-plan').value).toBe('Basic');
    expect(text()).toContain('Subscription plan: Basic');
    expect(text()).not.toContain('INTERNAL_TEST_DETAIL');

    retry();
    expect(values()).toEqual([]);
    httpTesting.expectNone(monthsUrl);
    respond(septemberBasic, 'Basic');

    expect(values()).toEqual(['2', '1', '50%', '20 hours']);
    expect(element.querySelector('[role="alert"]')).toBeNull();
    expect(element.querySelector('button')).toBeNull();
  });

  it('allows a different selection after a failed request', () => {
    initialize();
    change('subscription-plan', 'Basic');

    expectIndicators(october, 'Basic').flush(
      {},
      { status: 503, statusText: 'Service Unavailable' }
    );
    fixture.detectChanges();

    change('subscription-plan', 'Premium');
    expect(element.querySelector('[role="alert"]')).toBeNull();
    respond(octoberPremium, 'Premium');

    expect(values()).toEqual(['1', '1', '100%', '20 hours']);
  });

  it('cancels obsolete requests during rapid month and plan changes', () => {
    respondWithMonths();
    const initialRequest = expectIndicators(october);

    change('subscription-plan', 'Basic');
    const basicRequest = expectIndicators(october, 'Basic');

    expect(initialRequest.cancelled).toBe(true);

    change('observation-month', september);
    expect(basicRequest.cancelled).toBe(true);
    expect(values()).toEqual([]);

    // EN: The latest request completes before the obsolete requests.
    // FR: La dernière demande se termine avant les demandes dépassées.
    respond(septemberBasic, 'Basic');
    expect(values()).toEqual(['2', '1', '50%', '20 hours']);

    // EN: Angular's HTTP test backend refuses late delivery after cancellation.
    // FR: Le simulateur HTTP refuse une réponse tardive après annulation.
    expect(() => initialRequest.flush(octoberAll)).toThrow();
    expect(() => basicRequest.flush(octoberBasic)).toThrow();

    fixture.detectChanges();
    expect(values()).toEqual(['2', '1', '50%', '20 hours']);
    expect(text()).toContain('Observation month: 2026-09');
    expect(text()).toContain('Subscription plan: Basic');
  });

  it('cancels a pending indicator request when the panel is destroyed', () => {
    respondWithMonths();
    const request = expectIndicators(october);

    fixture.destroy();

    expect(request.cancelled).toBe(true);
  });
});