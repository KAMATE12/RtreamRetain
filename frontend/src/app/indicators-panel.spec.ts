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
  RetentionSuggestionsResponse,
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

    // EN: Complete the independent initial request for saved actions.
    // FR: Terminer la requête initiale indépendante des actions enregistrées.
    const actionsRequest = httpTesting.expectOne('/api/retention-actions');
    expect(actionsRequest.request.method).toBe('GET');
    actionsRequest.flush({ actions: [] });

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

    function suggestionBody(
    month: string,
    plan: PlanSelection = null,
  ): RetentionSuggestionsResponse {
    const isSeptember = month === september;
    const represented = plan === null || plan === 'Premium';

    return {
      observation_month: month,
      plan,
      reference: {
        scope: 'all_plans',
        cohort_size: isSeptember ? 100 : 2,
        cancellation_count: isSeptember ? 12 : 1,
        cancellation_rate: isSeptember ? 12 : 50,
      },
      suggestions: represented
        ? [{
            rule_id: 'PLAN_RATE_ABOVE_OVERALL',
            rule_version: 1,
            plan: 'Premium',
            cohort_size: isSeptember ? 20 : 1,
            cancellation_count: isSeptember ? 4 : 1,
            cancellation_rate: isSeptember ? 20 : 100,
            proposed_action: 'Investigate Premium cancellation requests.',
            rationale: isSeptember
              ? '4 of 20 customers, compared with 12 of 100 overall.'
              : '1 of 1 customer, compared with 1 of 2 overall.',
          }]
        : [],
    };
  }

    function pending(month: string, plan: PlanSelection = null) {
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

    const suggestions = httpTesting.expectOne(
      (request) =>
        request.url === '/api/retention-suggestions' &&
        request.params.get('observation_month') === month &&
        request.params.get('plan') === plan
    );

    expect(summary.request.method).toBe('GET');
    expect(comparison.request.method).toBe('GET');
    expect(suggestions.request.method).toBe('GET');

    return { summary, comparison, suggestions };
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
    requests.suggestions.flush(
      suggestionBody(summary.observation_month, plan)
    );

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

  it.each(['summary', 'comparison', 'suggestions'] as const)(
    'waits for all results when %s arrives last',
    (last) => {
      respondWithMonths();
      const requests = pending(october);

      const flush = {
        summary: () => requests.summary.flush(octoberAll),
        comparison: () => requests.comparison.flush({
          observation_month: october,
          plan: null,
          comparisons: octoberGroups,
        }),
        suggestions: () => requests.suggestions.flush(
          suggestionBody(october)
        ),
      };

      for (const key of ['summary', 'comparison', 'suggestions'] as const) {
        if (key !== last) {
          flush[key]();
        }
      }

      fixture.detectChanges();

      expect(values()).toEqual([]);
      expect(rows()).toEqual([]);
      expect(element.querySelector('.suggestion-card')).toBeNull();
      expect(text()).toContain('Loading monthly indicators');
      expect(
        element.querySelector('[aria-live]')?.getAttribute('aria-busy')
      ).toBe('true');

      flush[last]();
      fixture.detectChanges();

      expect(values()).toHaveLength(4);
      expect(rows()).toHaveLength(2);
      expect(element.querySelectorAll('.suggestion-card')).toHaveLength(1);
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
        request.url === '/api/plan-comparisons' ||
        request.url === '/api/retention-suggestions'
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

  it.each(['summary', 'comparison', 'suggestions'] as const)(
    'hides all results and retries current filters after %s failure',
    (failed) => {
      initialize();
      change('subscription-plan', 'Basic');
      const requests = pending(october, 'Basic');

      requests[failed].flush(
        { detail: 'PRIVATE_DETAIL' },
        { status: 503, statusText: 'Service Unavailable' }
      );
      fixture.detectChanges();

      for (const key of ['summary', 'comparison', 'suggestions'] as const) {
        if (key !== failed) {
          expect(requests[key].cancelled).toBe(true);
        }
      }

      expect(values()).toEqual([]);
      expect(rows()).toEqual([]);
      expect(element.querySelector('.suggestion-card')).toBeNull();
      expect(element.querySelector('.suggestion-reference')).toBeNull();
      expect(element.querySelector('[role="alert"]')).not.toBeNull();
      expect(text()).not.toContain('PRIVATE_DETAIL');
      expect(select('observation-month').value).toBe(october);
      expect(select('subscription-plan').value).toBe('Basic');

      retry();
      httpTesting.expectNone(monthsUrl);
      respond(octoberBasic, [octoberGroups[0]!], 'Basic');

      expect(values()).toEqual(['1', '0', '0%', '0 hours']);
      expect(rows()).toEqual([['Basic', '1', '0', '0%']]);
      expect(text()).toContain(
        'No subscription plan in this selection meets the rule.'
      );
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

  it('cancels all pending requests when the component is destroyed', () => {
    respondWithMonths();
    const requests = pending(october);

    fixture.destroy();

    expect(requests.summary.cancelled).toBe(true);
    expect(requests.comparison.cancelled).toBe(true);
    expect(requests.suggestions.cancelled).toBe(true);
  });

    it('shows the global reference when Premium is selected', () => {
    initialize();
    change('observation-month', september);
    respond(septemberAll, septemberGroups);

    change('subscription-plan', 'Premium');

    expect(element.querySelector('.suggestion-card')).toBeNull();
    expect(element.querySelector('.suggestion-reference')).toBeNull();

    respond({
      observation_month: september,
      cohort_size: 20,
      cancellation_count: 4,
      cancellation_rate: 20,
      average_viewing_hours: 60,
    }, [septemberGroups[1]!], 'Premium');

    // EN: The summary is filtered, but the reference includes all plans.
    // FR: Le résumé est filtré, mais la référence inclut tous les abonnements.
    expect(values()).toEqual(['20', '4', '20%', '60 hours']);

    const reference = cleanText(
      element.querySelector('.suggestion-reference')!
    );
    expect(reference).toContain('Reference: all plans for 2026-09.');
    expect(reference).toContain('12 cancellation requests among 100 customers');
    expect(reference).toContain('12%');

    const card = cleanText(element.querySelector('.suggestion-card')!);
    expect(card).toContain('Investigate Premium cancellation requests.');
    expect(card).toContain('4 of 20 customers');
    expect(card).toContain('PLAN_RATE_ABOVE_OVERALL');
    expect(card).toContain('Version: 1');
    expect(text()).toContain('No action is saved automatically.');
  });

  it('does not display a completed suggestion if another request fails', () => {
    respondWithMonths();
    const requests = pending(october);

    requests.suggestions.flush(suggestionBody(october));
    requests.summary.flush(octoberAll);
    fixture.detectChanges();

    expect(element.querySelector('.suggestion-card')).toBeNull();

    requests.comparison.flush(
      {},
      { status: 503, statusText: 'Service Unavailable' }
    );
    fixture.detectChanges();

    expect(element.querySelector('.suggestion-card')).toBeNull();
    expect(element.querySelector('[role="alert"]')).not.toBeNull();
    expect(values()).toEqual([]);
  });

  it('cancels obsolete suggestions and rejects late delivery', () => {
    respondWithMonths();
    const oldRequests = pending(october);

    change('subscription-plan', 'Basic');
    expect(oldRequests.suggestions.cancelled).toBe(true);

    respond(octoberBasic, [octoberGroups[0]!], 'Basic');

    expect(() => oldRequests.suggestions.flush(
      suggestionBody(october)
    )).toThrow();

    fixture.detectChanges();

    expect(element.querySelector('.suggestion-card')).toBeNull();
    expect(text()).toContain(
      'No subscription plan in this selection meets the rule.'
    );
    expect(select('subscription-plan').value).toBe('Basic');
  });

  it('preserves the reviewed context and pending save across filter changes', async () => {
    initialize();

    const reviewButton = element.querySelector<HTMLButtonElement>(
      '.suggestion-card button'
    );
    expect(reviewButton).not.toBeNull();
    reviewButton!.click();
    fixture.detectChanges();
    await fixture.whenStable();

    const panel = element.querySelector('app-retention-actions-panel')!;
    const actionInput = panel.querySelector<HTMLTextAreaElement>(
      '#action-text'
    )!;

    actionInput.value = 'Investigate the original October Premium cohort.';
    actionInput.dispatchEvent(new Event('input', { bubbles: true }));
    fixture.detectChanges();

    // EN: Change both filters while retaining the October Premium draft.
    // FR: Changer les deux filtres en conservant le brouillon Premium d'octobre.
    change('subscription-plan', 'Basic');
    respond(octoberBasic, [octoberGroups[0]!], 'Basic');
    change('observation-month', september);
    respond(septemberBasic, [septemberGroups[0]!], 'Basic');
    await fixture.whenStable();

    const context = cleanText(panel.querySelector('.context')!);
    expect(context).toContain('2026-10');
    expect(context).toContain('Premium');
    expect(actionInput.value).toBe(
      'Investigate the original October Premium cohort.'
    );

    panel.querySelector<HTMLFormElement>('form')!.dispatchEvent(
      new Event('submit', { bubbles: true, cancelable: true })
    );
    fixture.detectChanges();

    const save = httpTesting.expectOne('/api/retention-actions');
    expect(save.request.method).toBe('POST');
    expect(save.request.body.observation_month).toBe(october);
    expect(save.request.body.plan).toBe('Premium');

    // EN: Changing filters must not cancel a pending action save.
    // FR: Un changement de filtre ne doit pas annuler l'enregistrement.
    change('subscription-plan', '');
    respond(septemberAll, septemberGroups);
    expect(save.cancelled).toBe(false);

    const saved = {
      ...save.request.body,
      id: '00000000-0000-0000-0000-000000000001',
      status: 'Proposed',
      created_at: '2026-11-24T12:00:00+00:00',
    };
    save.flush(saved, { status: 201, statusText: 'Created' });

    httpTesting.expectOne('/api/retention-actions').flush({
      actions: [saved],
    });
    fixture.detectChanges();

    const savedCard = cleanText(panel.querySelector('article')!);
    expect(savedCard).toContain('2026-10');
    expect(savedCard).toContain('Premium');
    expect(select('observation-month').value).toBe(september);
    expect(select('subscription-plan').value).toBe('');
  });


});
