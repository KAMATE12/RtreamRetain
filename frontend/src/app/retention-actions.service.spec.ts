import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { RetentionActionsService } from './retention-actions.service';
import {
  RetentionAction,
  RetentionActionCreate,
} from './retention-actions.models';

describe('RetentionActionsService', () => {
  let service: RetentionActionsService;
  let http: HttpTestingController;

  const payload: RetentionActionCreate = {
    observation_month: '2026-09-01',
    plan: 'Premium',
    proposed_action: 'Review support history.',
    rationale: 'Manager-reviewed investigation proposal.',
    rule_id: 'PLAN_RATE_ABOVE_OVERALL',
    rule_version: 1,
  };

  const saved: RetentionAction = {
    ...payload,
    id: '00000000-0000-0000-0000-000000000001',
    status: 'Proposed',
    created_at: '2026-11-24T12:00:00+00:00',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(RetentionActionsService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
  });

  it('lists actions without dashboard filters and preserves their context', () => {
    const historical: RetentionAction = {
      ...saved,
      id: '00000000-0000-0000-0000-000000000002',
      observation_month: '2026-08-01',
      plan: 'Basic',
    };
    const body = { actions: [saved, historical] };

    service.listActions().subscribe((response) => {
      expect(response).toEqual(body);
    });

    const request = http.expectOne('/api/retention-actions');
    expect(request.request.method).toBe('GET');
    expect(request.request.params.keys()).toEqual([]);
    request.flush(body);
  });

  it('preserves an empty action list', () => {
    service.listActions().subscribe((response) => {
      expect(response).toEqual({ actions: [] });
    });

    http.expectOne('/api/retention-actions').flush({ actions: [] });
  });

  it('sends only reviewed fields and returns the confirmed action', () => {
    const original = { ...payload };

    service.createAction(payload).subscribe((response) => {
      expect(response).toEqual(saved);
    });

    const request = http.expectOne('/api/retention-actions');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    expect(request.request.body.status).toBeUndefined();
    expect(request.request.body.id).toBeUndefined();
    expect(request.request.body.created_at).toBeUndefined();

    request.flush(saved, { status: 201, statusText: 'Created' });
    expect(payload).toEqual(original);
  });

  it('propagates an uncertain save failure without retrying', () => {
    let success = false;
    let errorStatus: number | undefined;

    service.createAction(payload).subscribe({
      next: () => {
        success = true;
      },
      error: (error) => {
        errorStatus = error.status;
      },
    });

    const request = http.expectOne('/api/retention-actions');
    request.flush(
      { detail: 'The save could not be confirmed.' },
      { status: 503, statusText: 'Service Unavailable' },
    );

    expect(success).toBe(false);
    expect(errorStatus).toBe(503);
    http.expectNone('/api/retention-actions');
  });

  it('does not turn a list failure into an empty successful result', () => {
    let success = false;
    let errorStatus: number | undefined;

    service.listActions().subscribe({
      next: () => {
        success = true;
      },
      error: (error) => {
        errorStatus = error.status;
      },
    });

    http.expectOne('/api/retention-actions').flush(
      { detail: 'Unable to load saved actions' },
      { status: 503, statusText: 'Service Unavailable' },
    );

    expect(success).toBe(false);
    expect(errorStatus).toBe(503);
  });
});