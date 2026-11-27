"""
EN: Store reviewed proposals and retrieve their original context.
FR: Enregistrer les propositions examinées et relire leur contexte.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.retention_action_status import validate_status_transition

from sqlalchemy import select
from sqlalchemy.engine import Connection

from app.indicators import get_plan_comparisons
from app.retention_action_models import RetentionActionCreate
from app.schema import retention_action
from app.suggestions import build_plan_suggestions


class SuggestionUnavailableError(ValueError):
    """The requested suggestion no longer matches the stored observations."""


def create_retention_action(
    connection: Connection,
    *,
    request: RetentionActionCreate,
) -> dict:
    """Validate eligibility and insert within the caller's transaction."""

    # EN: Recheck the suggestion using all plans for the selected month.
    # FR: Revérifier la suggestion avec tous les abonnements du mois.
    comparisons = get_plan_comparisons(
        connection,
        observation_month=request.observation_month,
        plan=None,
    )
    result = build_plan_suggestions(
        comparisons,
        observation_month=request.observation_month,
        plan=request.plan,
    )

    matching_suggestion = any(
        suggestion["plan"] == request.plan
        and suggestion["rule_id"] == request.rule_id
        and suggestion["rule_version"] == request.rule_version
        for suggestion in result["suggestions"]
    )

    if not matching_suggestion:
        raise SuggestionUnavailableError(
            "This suggestion is no longer available. "
            "Refresh the dashboard and review the suggestion again."
        )

    # EN: Preserve reviewed text; generate server-owned fields here.
    # FR: Conserver les textes examinés et générer les champs du serveur.
    values = {
        **request.model_dump(),
        "id": uuid4(),
        "created_at": datetime.now(timezone.utc),
        "status": "Proposed",
    }

    stored = connection.execute(
        retention_action.insert()
        .values(**values)
        .returning(*retention_action.c)
    ).mappings().one()

    # EN: The caller must commit before reporting successful creation.
    # FR: L'appelant doit valider la transaction avant d'annoncer le succès.
    return dict(stored)


def list_retention_actions(connection: Connection) -> list[dict]:
    """List all actions, newest first, with a deterministic tie-breaker."""

    statement = select(retention_action).order_by(
        retention_action.c.created_at.desc(),
        retention_action.c.id.desc(),
    )

    return [
        dict(row)
        for row in connection.execute(statement).mappings()
    ]

class RetentionActionNotFoundError(LookupError):
    """The requested saved action does not exist."""


def update_retention_action_status(
    connection: Connection,
    *,
    action_id: UUID,
    target_status: str,
) -> dict:
    """
    EN: Lock, validate and update within the caller's transaction.
    FR: Verrouiller, valider et modifier dans la transaction de l'appelant.
    """

    # EN: Lock this action before inspecting its stored current status.
    # FR: Verrouiller cette action avant de vérifier son statut enregistré.
    statement = (
        select(retention_action)
        .where(retention_action.c.id == action_id)
        .with_for_update()
    )

    stored = connection.execute(statement).mappings().one_or_none()

    if stored is None:
        raise RetentionActionNotFoundError(
            "The requested action does not exist."
        )

    current_action = dict(stored)

    requires_update = validate_status_transition(
        current_action["status"],
        target_status,
    )

    # EN: Return the unchanged action without issuing an UPDATE.
    # FR: Renvoyer l'action inchangée sans exécuter d'UPDATE.
    if not requires_update:
        return current_action

    # EN: Modify only status; preserve creation time and original context.
    # FR: Modifier uniquement le statut ; conserver date et contexte.
    updated = connection.execute(
        retention_action.update()
        .where(retention_action.c.id == action_id)
        .values(status=target_status)
        .returning(*retention_action.c)
    ).mappings().one()

    # EN: The caller must commit before reporting success.
    # FR: L'appelant doit valider la transaction avant d'annoncer le succès.
    return dict(updated)