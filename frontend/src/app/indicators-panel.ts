/**
 * EN: Load monthly indicators and manage the dashboard's display states.
 * Select the latest available month and include all subscription plans.
 * Clear previous results before loading and expose a retry after failure.
 *
 * FR: Charger les indicateurs mensuels et gérer les états d'affichage.
 * Sélectionner le dernier mois disponible et inclure tous les abonnements.
 * Effacer les anciens résultats avant le chargement et permettre une
 * nouvelle tentative après une erreur.
 */

import {
  Component,
  DestroyRef,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { of, switchMap } from 'rxjs';

import { IndicatorsService } from './indicators.service';
import { IndicatorsState, MonthlyIndicators } from './indicators.models';

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
  private loadingInProgress = false;

  readonly state = signal<IndicatorsState>('loading');
  readonly indicators = signal<MonthlyIndicators | null>(null);
  readonly observationMonth = signal<string | null>(null);

  ngOnInit(): void {
    this.loadIndicators();
  }

  loadIndicators(): void {
    // EN: Prevent overlapping requests, including repeated button clicks.
    // FR: Empêcher les requêtes simultanées, notamment les clics répétés.
    if (this.loadingInProgress) {
      return;
    }

    this.loadingInProgress = true;

    // EN: Remove stale values before starting a new loading attempt.
    // FR: Retirer les anciennes valeurs avant une nouvelle tentative.
    this.indicators.set(null);
    this.observationMonth.set(null);
    this.state.set('loading');

    this.service.getAvailableMonths()
      .pipe(
        switchMap((response) => {
          // EN: The API orders months from newest to oldest.
          // FR: L'API classe les mois du plus récent au plus ancien.
          const latestMonth = response.observation_months[0];

          if (!latestMonth) {
            return of(null);
          }

          this.observationMonth.set(latestMonth);
          return this.service.getMonthlyIndicators(latestMonth);
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (result) => {
          this.indicators.set(result);
          this.state.set(
            result === null || result.cohort_size === 0
              ? 'empty'
              : 'ready'
          );
        },
        error: () => {
          // EN: Show no previous results or raw server errors.
          // FR: N'afficher ni anciens résultats ni erreurs brutes du serveur.
          this.indicators.set(null);
          this.observationMonth.set(null);
          this.state.set('error');
          this.loadingInProgress = false;
        },
        complete: () => {
          this.loadingInProgress = false;
        },
      });
  }
}