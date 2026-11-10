/**
 * EN: Describe the API response types and the indicator interface states.
 * These definitions help TypeScript check how the application uses data.
 * Nullable indicators distinguish unavailable values from measured zeros.
 * These types do not validate incoming JSON at runtime.
 *
 * FR: Décrire les types des réponses API et les états de l'interface.
 * Ces définitions aident TypeScript à vérifier l'utilisation des données.
 * Les indicateurs pouvant être null distinguent une valeur indisponible
 * d'un zéro mesuré. Ces types ne valident pas le JSON reçu à l'exécution.
 */


/** Available observation months, ordered newest first by the API. */
export interface ObservationMonthsResponse {
  observation_months: string[];
}

/** Monthly indicators calculated by the backend. */
export interface MonthlyIndicators {
  observation_month: string;
  cohort_size: number;
  cancellation_count: number;

  // EN: Null means unavailable; zero is a measured result.
  // FR: Null signifie indisponible ; zéro est un résultat mesuré.
  cancellation_rate: number | null;
  average_viewing_hours: number | null;
}

/** Explicit states used by the indicator interface. */
export type IndicatorsState = 'loading' | 'ready' | 'empty' | 'error';