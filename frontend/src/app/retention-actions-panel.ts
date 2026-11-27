import {
  Component,
  DestroyRef,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subscription } from 'rxjs';

import { RetentionSuggestion } from './indicators.models';
import {
  RetentionAction,
  RetentionActionCreate,
  RetentionActionStatus,
} from './retention-actions.models';
import { RetentionActionsService } from './retention-actions.service';

@Component({
  selector: 'app-retention-actions-panel',
  standalone: true,
  imports: [FormsModule, DatePipe],
  templateUrl: './retention-actions-panel.html',
  styleUrl: './retention-actions-panel.css',
})
export class RetentionActionsPanel implements OnInit {
  private readonly service = inject(RetentionActionsService);
  private readonly destroyRef = inject(DestroyRef);
  private listRequest?: Subscription;

  readonly draft = signal<RetentionActionCreate | null>(null);
  readonly saving = signal(false);
  readonly saveError = signal('');
  readonly successMessage = signal('');
  readonly actions = signal<RetentionAction[]>([]);
  readonly listState = signal<'loading' | 'ready' | 'error'>('loading');
  readonly updatingActionId = signal<string | null>(null);
  readonly statusErrors = signal<Record<string, string>>({});
  readonly statusMessages = signal<Record<string, string>>({});

  allowedNextStatuses(
    status: RetentionActionStatus,
  ): readonly RetentionActionStatus[] {
    switch (status) {
      case 'Proposed':
        return ['In Progress', 'Dismissed'];
      case 'In Progress':
        return ['Completed', 'Dismissed'];
      default:
        return [];
    }
  }

  updateStatus(
    actionId: string,
    targetStatus: RetentionActionStatus,
  ): void {
    // EN: Serialize writes and require a refreshed state after an error.
    // FR: Éviter les écritures simultanées et actualiser après une erreur.
    if (
      this.updatingActionId() !== null ||
      this.saving() ||
      this.listState() !== 'ready' ||
      this.statusErrors()[actionId]
    ) {
      return;
    }

    const action = this.actions().find((item) => item.id === actionId);

    if (
      !action ||
      !this.allowedNextStatuses(action.status).includes(targetStatus)
    ) {
      return;
    }

    this.updatingActionId.set(actionId);
    this.statusMessages.set({});

    // EN: Keep the last confirmed status while awaiting the server.
    // FR: Garder le dernier statut confirmé pendant l'attente du serveur.
    this.service.updateStatus(actionId, targetStatus).pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (confirmed) => {
        this.actions.update((actions) =>
          actions.map((item) =>
            item.id === actionId ? confirmed : item
          ),
        );
        this.updatingActionId.set(null);
        this.statusMessages.set({
          [actionId]: `Status confirmed: ${confirmed.status}.`,
        });
      },
      error: (error: HttpErrorResponse) => {
        this.updatingActionId.set(null);

        let message: string;

        if (error.status === 409) {
          message =
            'This transition is not allowed from the stored status. ' +
            'The displayed status is the last confirmed value. ' +
            'Refresh saved actions before trying again.';
        } else if (error.status === 404) {
          message =
            'This action could not be found. ' +
            'Refresh saved actions to retrieve the current list.';
        } else if (error.status === 422) {
          message =
            'The server rejected this status request. ' +
            'The displayed status is the last confirmed value. ' +
            'Refresh saved actions before trying again.';
        } else {
          message =
            'The status update could not be confirmed. ' +
            'The displayed status is the last confirmed value; ' +
            'the change may already have been saved. ' +
            'Refresh saved actions before trying again.';
        }

        this.statusErrors.update((errors) => ({
          ...errors,
          [actionId]: message,
        }));
      },
    });
  }

  actionText = '';
  rationaleText = '';

  ngOnInit(): void {
    this.loadActions();
  }

  openReview(month: string, suggestion: RetentionSuggestion): void {
    // EN: Keep an existing draft until the manager saves or closes it.
    // FR: Conserver le brouillon jusqu'à son enregistrement ou sa fermeture.
    if (this.draft() !== null || this.saving()) {
      return;
    }

    this.draft.set({
      observation_month: month,
      plan: suggestion.plan,
      proposed_action: suggestion.proposed_action,
      rationale: suggestion.rationale,
      rule_id: suggestion.rule_id,
      rule_version: suggestion.rule_version,
    });

    this.actionText = suggestion.proposed_action;
    this.rationaleText = suggestion.rationale;
    this.saveError.set('');
    this.successMessage.set('');
  }

  closeReview(): void {
    if (this.saving()) {
      return;
    }

    this.draft.set(null);
    this.actionText = '';
    this.rationaleText = '';
    this.saveError.set('');
  }

  saveAction(): void {
    const context = this.draft();

    if (
      context === null ||
      this.saving() ||
      this.updatingActionId() !== null
    ) {
      return;
    }

    const proposedAction = this.actionText.trim();
    const rationale = this.rationaleText.trim();

    // EN: Count Unicode code points, matching Python string length.
    // FR: Compter les points de code Unicode comme les chaînes Python.
    if (
      proposedAction.length === 0 ||
      rationale.length === 0 ||
      Array.from(proposedAction).length > 1000 ||
      Array.from(rationale).length > 3000 ||
      proposedAction.includes('\u0000') ||
      rationale.includes('\u0000')
    ) {
      this.saveError.set(
        'Enter an action of 1–1000 characters and a rationale of ' +
        '1–3000 characters. Blank text and null characters are not accepted.',
      );
      return;
    }

    const request: RetentionActionCreate = {
      ...context,
      proposed_action: proposedAction,
      rationale,
    };

    this.saving.set(true);
    this.saveError.set('');
    this.successMessage.set('');

    // EN: Save independently of dashboard filter requests; never retry here.
    // FR: Enregistrer indépendamment des filtres, sans nouvelle tentative.
    this.service.createAction(request).pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (saved) => {
        this.saving.set(false);
        this.draft.set(null);
        this.actionText = '';
        this.rationaleText = '';
        this.successMessage.set(
          `Proposal saved with status ${saved.status}. No intervention was executed.`,
        );
        this.loadActions();
      },
      error: (error: HttpErrorResponse) => {
        this.saving.set(false);

        if (error.status === 409) {
          this.saveError.set(
            'This suggestion is no longer available. Your text is preserved. ' +
            'Review refreshed dashboard results before preparing another proposal.',
          );
        } else if (error.status === 422) {
          this.saveError.set(
            'The server rejected the submitted fields. Your text is preserved. ' +
            'Check the text and suggestion context.',
          );
        } else {
          this.saveError.set(
            'The save could not be confirmed. Your text is preserved. ' +
            'Refresh the saved-action list before trying again: ' +
            'the action may already have been saved.',
          );
        }
      },
    });
  }

  loadActions(): void {
    // EN: Do not let a list response race with a pending write.
    // FR: Éviter une réponse de liste concurrente à une écriture en cours.
    if (this.updatingActionId() !== null || this.saving()) {
      return;
    }

    // EN: Cancel an obsolete list request before requesting a new one.
    // FR: Annuler l'ancienne requête avant de demander une nouvelle liste.
    this.listRequest?.unsubscribe();
    this.listState.set('loading');
    this.statusMessages.set({});

    this.listRequest = this.service.listActions().pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (response) => {
        this.actions.set(response.actions);
        this.statusErrors.set({});
        this.listState.set('ready');
      },
      error: () => {
        this.listState.set('error');
      },
    });
  }
}