/**
 * EN: Display monthly indicators for the active month and subscription plan.
 * Load available months once, preserve filters after errors, and cancel
 * obsolete indicator requests when the user changes the selection.
 * Backend calculations remain the source of all displayed indicator values.
 *
 * FR: Afficher les indicateurs du mois et de l'abonnement sélectionnés.
 * Charger les mois disponibles, conserver les filtres après une erreur
 * et annuler les demandes dépassées lors d'un changement de sélection.
 * Les valeurs affichées proviennent exclusivement des calculs du backend.
 */

import {
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EMPTY, Subject, catchError, switchMap } from 'rxjs';

import { IndicatorsService } from './indicators.service';
import {
  IndicatorSelection,
  IndicatorsState,
  MonthlyIndicators,
  SubscriptionPlan,
} from './indicators.models';

@Component({
  selector: 'app-indicators-panel',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './indicators-panel.html',
  styleUrl: './indicators-panel.css',
})
export class IndicatorsPanel implements OnInit {
  private readonly service = inject(IndicatorsService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly requests = new Subject<IndicatorSelection>();
  private monthsLoading = false;

  readonly plans: readonly SubscriptionPlan[] = [
    'Basic',
    'Standard',
    'Premium',
  ];

  readonly availableMonths = signal<string[]>([]);
  readonly selection = signal<IndicatorSelection | null>(null);
  readonly state = signal<IndicatorsState>('loading');
  readonly indicators = signal<MonthlyIndicators | null>(null);

  readonly planLabel = computed(
    () => this.selection()?.plan ?? 'All plans'
  );

  ngOnInit(): void {
    // EN: Each new selection replaces the previous indicator request.
    // FR: Chaque sélection remplace la demande d'indicateurs précédente.
    this.requests.pipe(
      switchMap((selection) => {
        this.indicators.set(null);
        this.state.set('loading');

        return this.service.getMonthlyIndicators(
          selection.observationMonth,
          selection.plan,
        ).pipe(
          // EN: Catch errors inside switchMap so future selections still work.
          // FR: Traiter l'erreur ici pour permettre les sélections suivantes.
          catchError(() => {
            this.indicators.set(null);
            this.state.set('error');
            return EMPTY;
          }),
        );
      }),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe((result) => {
      this.indicators.set(result);
      this.state.set(result.cohort_size === 0 ? 'empty' : 'ready');
    });

    this.loadAvailableMonths();
  }

  private loadAvailableMonths(): void {
    if (this.monthsLoading) {
      return;
    }

    this.monthsLoading = true;
    this.indicators.set(null);
    this.state.set('loading');

    this.service.getAvailableMonths().pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (response) => {
        this.monthsLoading = false;
        this.availableMonths.set(response.observation_months);

        // EN: The API returns months from newest to oldest.
        // FR: L'API renvoie les mois du plus récent au plus ancien.
        const latestMonth = response.observation_months[0];

        if (!latestMonth) {
          this.selection.set(null);
          this.state.set('empty');
          return;
        }

        this.selection.set({
          observationMonth: latestMonth,
          plan: null,
        });
        this.loadIndicators();
      },
      error: () => {
        this.monthsLoading = false;
        this.state.set('error');
      },
    });
  }

  changeMonth(month: string): void {
    const current = this.selection();

    // EN: Accept only a month present in the API's available-month list.
    // FR: Accepter uniquement un mois présent dans la liste de l'API.
    if (
      current === null ||
      !this.availableMonths().includes(month) ||
      current.observationMonth === month
    ) {
      return;
    }

    // EN: Preserve the plan even if the new combination has no observations.
    // FR: Conserver l'abonnement même si la combinaison ne contient rien.
    this.selection.set({ ...current, observationMonth: month });
    this.loadIndicators();
  }

  changePlan(value: string): void {
    const current = this.selection();

    if (current === null) {
      return;
    }

    // EN: An empty select value represents All plans, not an API plan.
    // FR: Une valeur vide représente All plans, pas un abonnement de l'API.
    let plan: SubscriptionPlan | null;

    if (value === '') {
      plan = null;
    } else if (
      value === 'Basic' ||
      value === 'Standard' ||
      value === 'Premium'
    ) {
      plan = value;
    } else {
      return;
    }

    if (current.plan === plan) {
      return;
    }

    this.selection.set({ ...current, plan });
    this.loadIndicators();
  }

  loadIndicators(): void {
    const current = this.selection();

    // EN: Retry month discovery only when no valid selection exists yet.
    // FR: Réessayer la liste des mois seulement sans sélection valide.
    if (current === null) {
      this.loadAvailableMonths();
      return;
    }

    // EN: Retry and filter changes always use the current selection.
    // FR: Les nouvelles tentatives utilisent toujours la sélection actuelle.
    this.requests.next(current);
  }
}