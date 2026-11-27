import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  RetentionAction,
  RetentionActionCreate,
  RetentionActionStatus,
  RetentionActionsResponse,
} from './retention-actions.models';

@Injectable({
  providedIn: 'root',
})
export class RetentionActionsService {
  private readonly http = inject(HttpClient);

  listActions(): Observable<RetentionActionsResponse> {
    // EN: List all saved actions independently of dashboard filters.
    // FR: Lister les actions indépendamment des filtres du tableau de bord.
    return this.http.get<RetentionActionsResponse>(
      '/api/retention-actions',
    );
  }

  createAction(
    request: RetentionActionCreate,
  ): Observable<RetentionAction> {
    // EN: Submit once; propagate errors without automatic retry.
    // FR: Envoyer une fois ; transmettre les erreurs sans nouvelle tentative.
    return this.http.post<RetentionAction>(
      '/api/retention-actions',
      request,
    );
  }

  updateStatus(
    actionId: string,
    status: RetentionActionStatus,
  ): Observable<RetentionAction> {
    // EN: Send only the target status and return the server-confirmed action.
    // FR: Envoyer uniquement le statut cible et recevoir l'action confirmée.
    // EN: Never retry automatically when the update outcome is uncertain.
    // FR: Ne jamais réessayer automatiquement si le résultat est incertain.
    return this.http.patch<RetentionAction>(
      `/api/retention-actions/${encodeURIComponent(actionId)}/status`,
      { status },
    );
  }
}