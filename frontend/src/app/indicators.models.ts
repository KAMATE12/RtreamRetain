/**
 * EN: Describe API responses, dashboard filters and display states.
 * A null plan means all subscription plans. Nullable indicators
 * distinguish unavailable values from measured zeros.
 * These types do not validate incoming JSON at runtime.
 *
 * FR: Décrire les réponses API, les filtres et les états d'affichage.
 * Un abonnement null représente tous les abonnements. Les indicateurs
 * pouvant être null distinguent une valeur indisponible d'un zéro mesuré.
 * Ces types ne valident pas le JSON reçu à l'exécution.
 */

/** EN: Subscription plans accepted by the API.
 *  FR: Abonnements acceptés par l'API. */
export type SubscriptionPlan = 'Basic' | 'Standard' | 'Premium';

/** EN: Null means that no subscription-plan restriction applies.
 *  FR: Null signifie qu'aucune restriction d'abonnement ne s'applique. */
export type PlanSelection = SubscriptionPlan | null;

/** EN: Shared filter scope for indicators and future comparisons.
 *  FR: Périmètre commun aux indicateurs et aux futures comparaisons. */
export interface IndicatorSelection {
  observationMonth: string;
  plan: PlanSelection;
}

/** EN: Available months, ordered newest first by the API.
 *  FR: Mois disponibles, classés du plus récent au plus ancien par l'API. */
export interface ObservationMonthsResponse {
  observation_months: string[];
}

/** EN: Monthly indicators calculated by the backend.
 *  FR: Indicateurs mensuels calculés par le backend. */
export interface MonthlyIndicators {
  observation_month: string;
  cohort_size: number;
  cancellation_count: number;

  // EN: Null means unavailable; zero is a measured result.
  // FR: Null signifie indisponible ; zéro est un résultat mesuré.
  cancellation_rate: number | null;
  average_viewing_hours: number | null;
}

/** EN: Explicit states used by the indicator interface.
 *  FR: États explicites utilisés par l'interface des indicateurs. */
export type IndicatorsState = 'loading' | 'ready' | 'empty' | 'error';