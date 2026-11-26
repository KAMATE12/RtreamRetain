import { PlanSelection, SubscriptionPlan } from './indicators.models';

/** EN: Fields submitted after reviewing a plan-specific suggestion.
 *  FR: Champs envoyés après examen d'une suggestion par abonnement. */
export interface RetentionActionCreate {
  observation_month: string;
  plan: SubscriptionPlan;
  proposed_action: string;
  rationale: string;
  rule_id: string;
  rule_version: number;
}

export type RetentionActionStatus =
  | 'Proposed'
  | 'In Progress'
  | 'Completed'
  | 'Dismissed';

/** EN: Saved proposal with its original context and server-owned fields.
 *  FR: Proposition enregistrée avec son contexte et les champs du serveur. */
export interface RetentionAction {
  id: string;
  observation_month: string;
  plan: PlanSelection;
  proposed_action: string;
  rationale: string;
  rule_id: string;
  rule_version: number;
  status: RetentionActionStatus;
  created_at: string;
}

export interface RetentionActionsResponse {
  actions: RetentionAction[];
}