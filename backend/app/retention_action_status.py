"""
EN: Define permitted action-status transitions without database access.
FR: Définir les transitions autorisées sans accéder à la base de données.
"""

from types import MappingProxyType


# EN: Terminal statuses cannot be reopened in this task.
# FR: Les statuts finaux ne peuvent pas être rouverts dans cette tâche.
ALLOWED_TRANSITIONS = MappingProxyType({
    "Proposed": frozenset({"In Progress", "Dismissed"}),
    "In Progress": frozenset({"Completed", "Dismissed"}),
    "Completed": frozenset(),
    "Dismissed": frozenset(),
})


class InvalidStatusTransitionError(ValueError):
    """The target status is not allowed from the stored current status."""


def validate_status_transition(
    current_status: str,
    target_status: str,
) -> bool:
    """
    EN: Return True for a change and False for a successful no-op.
    Raise InvalidStatusTransitionError for unsupported transitions.

    FR: Renvoyer True pour un changement et False pour une absence
    de changement autorisée. Lever une erreur pour une transition interdite.
    """

    if (
        current_status not in ALLOWED_TRANSITIONS
        or target_status not in ALLOWED_TRANSITIONS
    ):
        raise InvalidStatusTransitionError(
            "Unsupported action status."
        )

    # EN: Repeating the stored status succeeds without changing anything.
    # FR: Redemander le statut enregistré réussit sans rien modifier.
    if current_status == target_status:
        return False

    if target_status not in ALLOWED_TRANSITIONS[current_status]:
        raise InvalidStatusTransitionError(
            "This transition is not allowed from the current status."
        )

    return True