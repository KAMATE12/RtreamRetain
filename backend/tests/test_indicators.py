"""Tests for monthly customer indicators."""

import pytest

from app.indicators import calculate_cancellation_rate

def test_twelve_cancellations_among_one_hundred_customers():
    # EN: Arrange a cohort with known counts.
    # FR: Préparer une cohorte avec des effectifs connus.
    cohort_size = 100
    cancellation_count = 12

    # EN: Act by calculating the cancellation percentage.
    # FR: Exécuter le calcul du pourcentage d'annulation.
    result = calculate_cancellation_rate(
        cohort_size=cohort_size,
        cancellation_count=cancellation_count,
    )

    # EN: Assert that the calculated percentage is correct.
    # FR: Vérifier que le pourcentage calculé est correct.
    assert result == 12

def test_empty_cohort_has_no_cancellation_rate():
    # EN: Arrange an empty cohort with no cancellations.
    # FR: Préparer une cohorte vide sans annulation.
    cohort_size = 0
    cancellation_count = 0

    # EN: Calculate the rate for the empty cohort.
    # FR: Calculer le taux pour la cohorte vide.
    result = calculate_cancellation_rate(
        cohort_size=cohort_size,
        cancellation_count=cancellation_count,
    )

    # EN: An undefined rate must not be represented as zero percent.
    # FR: Un taux indéfini ne doit pas être représenté par zéro pour cent.
    assert result is None


@pytest.mark.parametrize(
    "cohort_size, cancellation_count",
    [
        (10, 12),
        (0, 1),
    ],
)
def test_cancellations_cannot_exceed_cohort_size(
    cohort_size,
    cancellation_count,
):
    # EN: Reject more cancellations than customers in the cohort.
    # FR: Refuser plus d'annulations que de clients dans la cohorte.
    with pytest.raises(ValueError):
        calculate_cancellation_rate(
            cohort_size=cohort_size,
            cancellation_count=cancellation_count,
        )

@pytest.mark.parametrize(
    "cohort_size, cancellation_count",
    [
        (-1, 0),
        (100, -1),
        (-1, -2),
    ],
)
def test_negative_counts_are_rejected(
    cohort_size,
    cancellation_count,
):
    # EN: Reject negative customer or cancellation counts.
    # FR: Refuser les nombres négatifs de clients ou d'annulations.
    with pytest.raises(ValueError):
        calculate_cancellation_rate(
            cohort_size=cohort_size,
            cancellation_count=cancellation_count,
        )

@pytest.mark.parametrize(
    "cohort_size, cancellation_count, expected_rate",
    [
        (100, 0, 0.0),
        (100, 100, 100.0),
        (8, 1, 12.5),
        (3, 1, 100 / 3),
    ],
)
def test_valid_cancellation_rates(
    cohort_size,
    cancellation_count,
    expected_rate,
):
    # EN: Calculate the percentage for valid counts.
    # FR: Calculer le pourcentage pour des effectifs valides.
    result = calculate_cancellation_rate(
        cohort_size=cohort_size,
        cancellation_count=cancellation_count,
    )

    # EN: Allow tiny floating-point representation differences.
    # FR: Tolérer les infimes différences de représentation des flottants.
    assert result == pytest.approx(expected_rate)


@pytest.mark.parametrize(
    "cohort_size, cancellation_count",
    [
        (100.5, 12),
        (100, 12.5),
        ("100", 12),
        (100, "12"),
        (None, 0),
        (100, None),
        (True, 0),
        (100, False),
    ],
)
def test_non_integer_counts_are_rejected(
    cohort_size,
    cancellation_count,
):
    # EN: Counts must be integers, excluding Boolean values.
    # FR: Les effectifs doivent être des entiers, sans accepter les booléens.
    with pytest.raises(TypeError):
        calculate_cancellation_rate(
            cohort_size=cohort_size,
            cancellation_count=cancellation_count,
        )