import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { RetentionActionsPanel } from './retention-actions-panel';
import { RetentionSuggestion } from './indicators.models';

describe('RetentionActionsPanel', () => {
  let fixture: ComponentFixture<RetentionActionsPanel>;
  let component: RetentionActionsPanel;
  let http: HttpTestingController;
  let element: HTMLElement;

  const url = '/api/retention-actions';
  const month = '2026-09-01';

  const suggestion: RetentionSuggestion = {
    rule_id: 'PLAN_RATE_ABOVE_OVERALL',
    rule_version: 1,
    plan: 'Premium',
    cohort_size: 43,
    cancellation_count: 9,
    cancellation_rate: 900 / 43,
    proposed_action: 'Investigate Premium cancellation requests.',
    rationale: '9 requests among 43 customers, versus 19 among 100 overall.',
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RetentionActionsPanel],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    http = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(RetentionActionsPanel);
    component = fixture.componentInstance;
    element = fixture.nativeElement as HTMLElement;
    fixture.detectChanges();
  });

  afterEach(() => {
    http.verify();
  });

  function finishInitialList(): void {
    http.expectOne(url).flush({ actions: [] });
    fixture.detectChanges();
  }

  function text(): string {
    return (element.textContent ?? '').replace(/\s+/g, ' ').trim();
  }

  async function openReview(): Promise<void> {
    component.openReview(month, suggestion);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
  }

  function edit(id: string, value: string): void {
    const input = element.querySelector<HTMLTextAreaElement>(`#${id}`)!;
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    fixture.detectChanges();
  }

  function submit(): void {
    element.querySelector<HTMLFormElement>('form')!.dispatchEvent(
      new Event('submit', { bubbles: true, cancelable: true })
    );
    fixture.detectChanges();
  }

  it('shows loading followed by an understandable empty list', () => {
    expect(text()).toContain('Loading saved actions');
    finishInitialList();
    expect(text()).toContain('No proposed actions have been saved yet.');
  });

  it('opens a review without automatically saving', async () => {
    finishInitialList();
    await openReview();

    expect(text()).toContain('2026-09');
    expect(text()).toContain('Premium');
    expect(text()).toContain('PLAN_RATE_ABOVE_OVERALL');
    expect(text()).toContain('Version: 1');

    expect(
      element.querySelector<HTMLTextAreaElement>('#action-text')!.value
    ).toBe(suggestion.proposed_action);

    http.expectNone(url);
  });

  it('preserves an existing draft when another review is requested', async () => {
    finishInitialList();
    await openReview();
    edit('action-text', 'My edited proposal.');

    component.openReview('2026-10-01', {
      ...suggestion,
      plan: 'Basic',
    });
    fixture.detectChanges();

    expect(component.draft()?.observation_month).toBe(month);
    expect(component.draft()?.plan).toBe('Premium');
    expect(component.actionText).toBe('My edited proposal.');
    http.expectNone(url);
  });

  it('saves edited text once and refreshes the list after confirmation', async () => {
    finishInitialList();
    await openReview();
    edit('action-text', '  Review support history.  ');
    edit('action-rationale', '  An edited investigation rationale.  ');

    submit();
    const save = http.expectOne(url);

    expect(save.request.method).toBe('POST');
    expect(save.request.body).toEqual({
      observation_month: month,
      plan: 'Premium',
      proposed_action: 'Review support history.',
      rationale: 'An edited investigation rationale.',
      rule_id: suggestion.rule_id,
      rule_version: 1,
    });
    expect(element.querySelector<HTMLFieldSetElement>('fieldset')!.disabled)
      .toBe(true);
    expect(component.successMessage()).toBe('');

    // EN: Also verify protection against repeated handler calls.
    // FR: Vérifier aussi la protection contre les appels répétés.
    component.saveAction();
    component.closeReview();
    http.expectNone(url);
    expect(component.draft()).not.toBeNull();

    const saved = {
      ...save.request.body,
      id: '00000000-0000-0000-0000-000000000001',
      status: 'Proposed',
      created_at: '2026-11-24T12:00:00+00:00',
    };
    save.flush(saved, { status: 201, statusText: 'Created' });

    const refresh = http.expectOne(url);
    expect(refresh.request.method).toBe('GET');
    refresh.flush({ actions: [saved] });
    fixture.detectChanges();

    expect(element.querySelector('form')).toBeNull();
    expect(text()).toContain('Proposal saved with status Proposed.');
    expect(text()).toContain('Review support history.');
    expect(text()).toContain('2026-11-24 12:00:00 UTC');
  });

  it.each([
    ['action-text', '   '],
    ['action-text', 'x'.repeat(1001)],
    ['action-rationale', '\t\n '],
    ['action-rationale', 'x'.repeat(3001)],
  ])('rejects invalid %s before sending a request', async (id, value) => {
    finishInitialList();
    await openReview();
    edit(id, value);
    submit();

    expect(element.querySelector('[role="alert"]')).not.toBeNull();
    expect(component.saving()).toBe(false);
    http.expectNone(url);
  });

  it.each([422, 409, 503])(
    'preserves entered text after HTTP %s without automatic retry',
    async (status) => {
      finishInitialList();
      await openReview();
      edit('action-text', 'My investigation proposal.');
      edit('action-rationale', 'My reviewed rationale.');
      submit();

      http.expectOne(url).flush(
        { detail: 'PRIVATE_INTERNAL_DETAIL' },
        { status, statusText: 'Request failed' },
      );
      fixture.detectChanges();

      expect(component.actionText).toBe('My investigation proposal.');
      expect(component.rationaleText).toBe('My reviewed rationale.');
      expect(component.draft()?.observation_month).toBe(month);
      expect(component.saving()).toBe(false);
      expect(component.successMessage()).toBe('');
      expect(element.querySelector('[role="alert"]')).not.toBeNull();
      expect(text()).not.toContain('PRIVATE_INTERNAL_DETAIL');
      http.expectNone(url);
    },
  );

  it('handles a lost response without retrying the POST', async () => {
    finishInitialList();
    await openReview();
    submit();

    http.expectOne(url).error(new ProgressEvent('error'));
    fixture.detectChanges();

    expect(text()).toContain('The save could not be confirmed.');
    expect(text()).toContain('the action may already have been saved');
    expect(component.actionText).toBe(suggestion.proposed_action);
    expect(component.draft()).not.toBeNull();
    http.expectNone(url);
  });

  it('retries a failed list request through the refresh button', () => {
    http.expectOne(url).flush(
      {},
      { status: 503, statusText: 'Service Unavailable' },
    );
    fixture.detectChanges();

    expect(text()).toContain('Unable to load saved actions.');
    expect(text()).not.toContain('No proposed actions have been saved yet.');

    const refresh = Array.from(element.querySelectorAll('button'))
      .find((button) => button.textContent?.includes('Refresh saved actions'))!;
    refresh.click();

    const request = http.expectOne(url);
    expect(request.request.method).toBe('GET');
    request.flush({ actions: [] });
    fixture.detectChanges();

    expect(text()).toContain('No proposed actions have been saved yet.');
  });

  it('keeps confirmed save success distinct from a failed list refresh', async () => {
    finishInitialList();
    await openReview();
    submit();

    const save = http.expectOne(url);
    save.flush({
      ...save.request.body,
      id: '00000000-0000-0000-0000-000000000001',
      status: 'Proposed',
      created_at: '2026-11-24T12:00:00+00:00',
    }, { status: 201, statusText: 'Created' });

    http.expectOne(url).flush(
      {},
      { status: 503, statusText: 'Service Unavailable' },
    );
    fixture.detectChanges();

    expect(text()).toContain('Proposal saved with status Proposed.');
    expect(text()).toContain('Unable to load saved actions.');
    expect(element.querySelector('form')).toBeNull();
    http.expectNone(url);
  });

  it('cancels an obsolete list request when refreshing', () => {
    const oldRequest = http.expectOne(url);

    component.loadActions();
    expect(oldRequest.cancelled).toBe(true);

    http.expectOne(url).flush({ actions: [] });
    fixture.detectChanges();

    expect(() => oldRequest.flush({ actions: [] })).toThrow();
    expect(component.listState()).toBe('ready');
  });

  it('cancels the pending list request when destroyed', () => {
    const request = http.expectOne(url);
    fixture.destroy();
    expect(request.cancelled).toBe(true);
  });
});