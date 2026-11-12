/**
 * EN: Verify summary indicators and plan comparisons for the same selection.
 * Use controlled HTTP responses to test unequal groups, filtering, loading,
 * errors, retry and cancellation without contacting a real database.
 *
 * FR: Vérifier le résumé et les comparaisons pour une même sélection.
 * Utiliser des réponses HTTP contrôlées pour tester les groupes inégaux,
 * les filtres, le chargement, les erreurs et les annulations sans base réelle.
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
  PlanComparison,
  PlanSelection,
} from './indicators.models';

describe('IndicatorsPanel', () => {
  let fixture: ComponentFixture<IndicatorsPanel>;
  let httpTesting: HttpTestingController;
  let element: HTMLElement;

  const september = '2026-09-01';
  const october = '2026-10-01';
  const monthsUrl = '/api/observation-months';

  const septemberAll: MonthlyIndicators = {
    observation_month: september,
    cohort_size: 100,
    cancellation_count: 12,
    cancellation_rate: 12,
    average_viewing_hours: 57.1351,
  };

  const septemberGroups: PlanComparison[] = [
    {
      plan: 'Basic',
      cohort_size: 80,
      cancellation_count: 8,
      cancellation_rate: 10,
    },
    {
      plan: 'Premium',
      cohort_size: 20,
      cancellation_count: 4,
      cancellation_rate: 20,
    },
  ];

  const septemberBasic: MonthlyIndicators = {
    observation_month: september,
    cohort_size: 80,
    cancellation_count: 8,
    cancellation_rate: 10,
    average_viewing_hours: 50,
  };

  const octoberAll: MonthlyIndicators = {
    observation_month: october,
    cohort_size: 2,
    cancellation_count: 1,
    cancellation_rate: 50,
    average_viewing_hours: 10,
  };

  const octoberGroups: PlanComparison[] = [
    {
      plan: 'Basic',
      cohort_size: 1,
      cancellation_count: 0,
      cancellation_rate: 0,
    },
    {
      plan: 'Premium',
      cohort_size: 1,
      cancellation_count: 1,
      cancellation_rate: 100,
    },
  ];

  const octoberBasic: MonthlyIndicators = {
    observation_month: october,
    cohort_size: 1,
    cancellation_count: 0,
    cancellation_rate: 0,
    average_viewing_hours: 0,
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

  function cleanText(node: Element): string {
    return (node.textContent ?? '').replace(/\s+/g, ' ').trim();
  }

  function text(): string {
    return cleanText(element);
  }

  function values(): string[] {
    return Array.from(element.querySelectorAll('dd')).map(cleanText);
  }

  function rows(): string[][] {
    return Array.from(
      element.querySelectorAll('.comparison-table tbody tr')
    ).map((row) =>
      Array.from(row.querySelectorAll('th, td')).map(cleanText)
    );
  }

  function select(id: string): HTMLSelectElement {
    const control = element.querySelector<HTMLSelectElement>(`#${id}`);
    expect(control).not.toBeNull();
    return control!;
  }

  function change(id: string, value: string): void {
    // EN: Exercise the actual selector rather than calling its handler.
    // FR: Utiliser le vrai sélecteur plutôt qu'appeler sa méthode.
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

  function pending(month: string, plan: PlanSelection = null) {
    // EN: Both endpoints must receive exactly the same filter scope.
    // FR: Les deux routes doivent recevoir exactement les mêmes filtres.
    const summary = httpTesting.expectOne(
      (request) =>
        request.url === '/api/indicators' &&
        request.params.get('observation_month') === month &&
        request.params.get('plan') === plan
    );

    const comparison = httpTesting.expectOne(
      (request) =>
        request.url === '/api/plan-comparisons' &&
        request.params.get('observation_month') === month &&
        request.params.get('plan') === plan
    );

    expect(summary.request.method).toBe('GET');
    expect(comparison.request.method).toBe('GET');

    return { summary, comparison };
  }

  function respond(
    summary: MonthlyIndicators,
    comparisons: PlanComparison[],
    plan: PlanSelection = null,
  ): void {
    const requests = pending(summary.observation_month, plan);

    requests.summary.flush(summary);
    requests.comparison.flush({
      observation_month: summary.observation_month,
      plan,
      comparisons,
    });

    fixture.detectChanges();
  }

  function initialize(): void {
    respondWithMonths();
    respond(octoberAll, octoberGroups);
  }

  function retry(): void {
    const button = element.querySelector<HTMLButtonElement>('button');
    expect(button).not.toBeNull();
    button!.click();
    fixture.detectChanges();
  }

  it('populates months and plans with the documented defaults', () => {
    initialize();

    expect(
      Array.from(select('observation-month').options).map(
        (option) => option.value
      )
    ).toEqual([october, september]);

    expect(
      Array.from(select('subscription-plan').options).map(cleanText)
    ).toEqual(['All plans', 'Basic', 'Standard', 'Premium']);

    expect(select('observation-month').value).toBe(october);
    expect(select('subscription-plan').value).toBe('');
    expect(values()).toEqual(['2', '1', '50%', '10 hours']);
    expect(rows()).toEqual([
      ['Basic', '1', '0', '0%'],
      ['Premium', '1', '1', '100%'],
    ]);
    expect(text()).toContain('Synthetic data only.');
    expect(text()).toContain(
      'No statistical significance testing is implemented.'
    );
  });

  it('displays 10% and 20% groups with a 12% combined summary', () => {
    initialize();
    change('observation-month', september);
    respond(septemberAll, septemberGroups);

    expect(values()).toEqual(['100', '12', '12%', '57.14 hours']);
    expect(rows()).toEqual([
      ['Basic', '80', '8', '10%'],
      ['Premium', '20', '4', '20%'],
    ]);

    // EN: Reconcile displayed group counts with displayed summary counts.
    // FR: Comparer les effectifs affichés des groupes à ceux du résumé.
    const groupRows = rows();
    expect(groupRows.reduce((sum, row) => sum + Number(row[1]), 0))
      .toBe(Number(values()[0]));
    expect(groupRows.reduce((sum, row) => sum + Number(row[2]), 0))
      .toBe(Number(values()[1]));

    expect(values()[2]).not.toBe('15%');
    expect(cleanText(element.querySelector('caption')!))
      .toContain('Observation month: 2026-09');
  });

  it.each(['summary', 'comparison'] as const)(
    'waits for both results when %s arrives first',
    (first) => {
      expect(values()).toEqual([]);
      expect(rows()).toEqual([]);

      respondWithMonths();
      const requests = pending(october);

      const comparisonBody = {
        observation_month: october,
        plan: null,
        comparisons: octoberGroups,
      };

      if (first === 'summary') {
        requests.summary.flush(octoberAll);
      } else {
        requests.comparison.flush(comparisonBody);
      }

      fixture.detectChanges();

      expect(values()).toEqual([]);
      expect(rows()).toEqual([]);
      expect(text()).toContain('Loading monthly indicators');
      expect(
        element.querySelector('[aria-live]')?.getAttribute('aria-busy')
      ).toBe('true');

      if (first === 'summary') {
        requests.comparison.flush(comparisonBody);
      } else {
        requests.summary.flush(octoberAll);
      }

      fixture.detectChanges();

      expect(values()).toHaveLength(4);
      expect(rows()).toHaveLength(2);
      expect(
        element.querySelector('[aria-live]')?.getAttribute('aria-busy')
      ).toBe('false');
    }
  );

  it('filters both displays and restores all represented plans', () => {
    initialize();
    change('subscription-plan', 'Basic');

    expect(values()).toEqual([]);
    expect(rows()).toEqual([]);

    respond(octoberBasic, [octoberGroups[0]!], 'Basic');

    expect(values()).toEqual(['1', '0', '0%', '0 hours']);
    expect(rows()).toEqual([['Basic', '1', '0', '0%']]);
    expect(text()).not.toContain('No data');
    expect(cleanText(element.querySelector('caption')!))
      .toContain('Subscription plan: Basic');

    change('subscription-plan', '');
    respond(octoberAll, octoberGroups);

    expect(values()).toEqual(['2', '1', '50%', '10 hours']);
    expect(rows()).toHaveLength(2);
    expect(cleanText(element.querySelector('caption')!))
      .toContain('Subscription plan: All plans');
  });

  it('preserves the selected plan when changing month', () => {
    initialize();
    change('subscription-plan', 'Basic');
    respond(octoberBasic, [octoberGroups[0]!], 'Basic');

    change('observation-month', september);

    expect(select('subscription-plan').value).toBe('Basic');
    expect(values()).toEqual([]);
    expect(rows()).toEqual([]);

    respond(septemberBasic, [septemberGroups[0]!], 'Basic');

    expect(values()).toEqual(['80', '8', '10%', '50 hours']);
    expect(rows()).toEqual([['Basic', '80', '8', '10%']]);
    expect(text()).toContain('Observation month: 2026-09');
    httpTesting.expectNone(monthsUrl);
  });

  it('shows an empty selection without inventing a zero-rate group', () => {
    initialize();
    change('subscription-plan', 'Standard');

    respond({
      observation_month: october,
      cohort_size: 0,
      cancellation_count: 0,
      cancellation_rate: null,
      average_viewing_hours: null,
    }, [], 'Standard');

    expect(select('subscription-plan').value).toBe('Standard');
    expect(values()).toEqual(['0', '0', 'No data', 'No data']);
    expect(rows()).toEqual([]);
    expect(element.querySelector('table')).toBeNull();
    expect(text()).toContain(
      'No subscription-plan observations are available for this selection.'
    );
  });

  it('does not request either result when no months exist', () => {
    httpTesting.expectOne(monthsUrl).flush({ observation_months: [] });
    fixture.detectChanges();

    httpTesting.expectNone(
      (request) =>
        request.url === '/api/indicators' ||
        request.url === '/api/plan-comparisons'
    );

    expect(element.querySelector('select')).toBeNull();
    expect(values()).toEqual(['0', '0', 'No data', 'No data']);
    expect(rows()).toEqual([]);
    expect(text()).toContain('No observation months are available.');
  });

  it('retries available-month discovery after its failure', () => {
    httpTesting.expectOne(monthsUrl).flush(
      { detail: 'PRIVATE_DETAIL' },
      { status: 503, statusText: 'Service Unavailable' }
    );
    fixture.detectChanges();

    expect(text()).not.toContain('PRIVATE_DETAIL');
    expect(element.querySelector('[role="alert"]')).not.toBeNull();

    retry();
    respondWithMonths();
    respond(octoberAll, octoberGroups);

    expect(values()).toHaveLength(4);
    expect(rows()).toHaveLength(2);
    expect(element.querySelector('[role="alert"]')).toBeNull();
  });

  it.each(['summary', 'comparison'] as const)(
    'hides both results and retries current filters after %s failure',
    (failed) => {
      initialize();
      change('subscription-plan', 'Basic');

      const requests = pending(october, 'Basic');
      const other = failed === 'summary' ? 'comparison' : 'summary';

      requests[failed].flush(
        { detail: 'PRIVATE_DETAIL' },
        { status: 503, statusText: 'Service Unavailable' }
      );
      fixture.detectChanges();

      // EN: Failure of either request cancels its still-pending partner.
      // FR: L'échec d'une demande annule l'autre si elle attend encore.
      expect(requests[other].cancelled).toBe(true);
      expect(values()).toEqual([]);
      expect(rows()).toEqual([]);
      expect(text()).not.toContain('PRIVATE_DETAIL');
      expect(select('observation-month').value).toBe(october);
      expect(select('subscription-plan').value).toBe('Basic');

      retry();
      httpTesting.expectNone(monthsUrl);
      respond(octoberBasic, [octoberGroups[0]!], 'Basic');

      expect(values()).toEqual(['1', '0', '0%', '0 hours']);
      expect(rows()).toEqual([['Basic', '1', '0', '0%']]);
      expect(element.querySelector('[role="alert"]')).toBeNull();
    }
  );

  it('hides a completed summary if the comparison subsequently fails', () => {
    initialize();
    change('subscription-plan', 'Basic');
    const requests = pending(october, 'Basic');

    requests.summary.flush(octoberBasic);
    requests.comparison.flush(
      {},
      { status: 503, statusText: 'Service Unavailable' }
    );
    fixture.detectChanges();

    expect(values()).toEqual([]);
    expect(rows()).toEqual([]);
    expect(element.querySelector('[role="alert"]')).not.toBeNull();

    // EN: A different selection must still work after the failure.
    // FR: Une autre sélection doit rester possible après l'erreur.
    change('subscription-plan', '');
    respond(octoberAll, octoberGroups);

    expect(values()).toEqual(['2', '1', '50%', '10 hours']);
    expect(rows()).toHaveLength(2);
  });

  it('cancels both obsolete requests during rapid selection changes', () => {
    respondWithMonths();
    const initial = pending(october);

    change('subscription-plan', 'Basic');
    const intermediate = pending(october, 'Basic');

    expect(initial.summary.cancelled).toBe(true);
    expect(initial.comparison.cancelled).toBe(true);

    change('observation-month', september);

    expect(intermediate.summary.cancelled).toBe(true);
    expect(intermediate.comparison.cancelled).toBe(true);
    expect(values()).toEqual([]);
    expect(rows()).toEqual([]);

    respond(septemberBasic, [septemberGroups[0]!], 'Basic');

    // EN: The HTTP test backend rejects late delivery after cancellation.
    // FR: Le simulateur HTTP refuse les réponses tardives après annulation.
    expect(() => initial.summary.flush(octoberAll)).toThrow();
    expect(() => initial.comparison.flush({
      observation_month: october,
      plan: null,
      comparisons: octoberGroups,
    })).toThrow();

    fixture.detectChanges();

    expect(values()).toEqual(['80', '8', '10%', '50 hours']);
    expect(rows()).toEqual([['Basic', '80', '8', '10%']]);
    expect(text()).toContain('Observation month: 2026-09');
    expect(text()).toContain('Subscription plan: Basic');
  });

  it('discards a partially completed pair when the selection changes', () => {
    respondWithMonths();
    const initial = pending(october);

    initial.comparison.flush({
      observation_month: october,
      plan: null,
      comparisons: octoberGroups,
    });
    fixture.detectChanges();

    expect(rows()).toEqual([]);

    change('subscription-plan', 'Basic');
    expect(initial.summary.cancelled).toBe(true);

    respond(octoberBasic, [octoberGroups[0]!], 'Basic');

    expect(values()).toEqual(['1', '0', '0%', '0 hours']);
    expect(rows()).toEqual([['Basic', '1', '0', '0%']]);
  });

  it('cancels both pending requests when the component is destroyed', () => {
    respondWithMonths();
    const requests = pending(october);

    fixture.destroy();

    expect(requests.summary.cancelled).toBe(true);
    expect(requests.comparison.cancelled).toBe(true);
  });
});