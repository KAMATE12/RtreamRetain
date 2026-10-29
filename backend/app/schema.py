"""Database table definitions for synthetic customer observations."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    Table,
    Text,
)


# EN: Collect the table definitions in one shared object.
# FR: Regrouper les définitions des tables dans un objet commun.
metadata = MetaData()


# EN: Store one identity per synthetic customer.
# FR: Stocker une seule identité par client synthétique.
customer = Table(
    "customer",
    metadata,

    # EN: The primary key uniquely identifies each customer.
    # FR: La clé primaire identifie chaque client de manière unique.
    Column(
        "customer_id",
        Text,
        primary_key=True,
        nullable=False,
    ),

    # EN: Reject empty identifiers and identifiers containing only spaces.
    # FR: Refuser les identifiants vides ou composés uniquement d'espaces.
    CheckConstraint(
        "length(trim(customer_id)) > 0",
        name="ck_customer_id_not_blank",
    ),
)

# EN: Store one observation per customer and calendar month.
# FR: Stocker une observation par client et par mois civil.
customer_month = Table(
    "customer_month",
    metadata,

    # EN: Reference an existing customer.
    # FR: Référencer un client existant.
    Column(
        "customer_id",
        Text,
        ForeignKey(
            "customer.customer_id",
            name="fk_customer_month_customer",
        ),
        primary_key=True,
        nullable=False,
    ),

    # EN: Together with customer_id, this forms the composite primary key.
    # FR: Avec customer_id, cette colonne forme la clé primaire composée.
    Column(
        "observation_month",
        Date,
        primary_key=True,
        nullable=False,
    ),

    # EN: All observation fields are required.
    # FR: Tous les champs de l'observation sont obligatoires.
    Column("plan", Text, nullable=False),
    Column("tenure_months", Integer, nullable=False),

    # EN: Preserve decimal values without forcing two decimal places.
    # FR: Conserver les décimales sans imposer deux chiffres après la virgule.
    Column("viewing_hours", Numeric(asdecimal=True), nullable=False),

    Column("payment_failures", Integer, nullable=False),
    Column("support_requests", Integer, nullable=False),
    Column("cancelled_in_month", Boolean, nullable=False),

    # EN: Store the first day as the identifier of the observation month.
    # FR: Utiliser le premier jour pour identifier le mois d'observation.
    CheckConstraint(
        "EXTRACT(DAY FROM observation_month) = 1",
        name="ck_customer_month_first_day",
    ),

    # EN: Accept only the three fictional subscription plans.
    # FR: Accepter uniquement les trois formules fictives prévues.
    CheckConstraint(
        "plan IN ('Basic', 'Standard', 'Premium')",
        name="ck_customer_month_plan",
    ),

    # EN: Reject negative durations and event counts.
    # FR: Refuser les anciennetés et nombres d'événements négatifs.
    CheckConstraint(
        "tenure_months >= 0",
        name="ck_customer_month_tenure_non_negative",
    ),
    CheckConstraint(
        "payment_failures >= 0",
        name="ck_customer_month_payment_failures_non_negative",
    ),
    CheckConstraint(
        "support_requests >= 0",
        name="ck_customer_month_support_requests_non_negative",
    ),

    # EN: Require non-negative viewing hours and reject special numeric values.
    # FR: Exiger des heures positives ou nulles et refuser les valeurs spéciales.
    CheckConstraint(
        "viewing_hours >= 0 "
        "AND viewing_hours NOT IN "
        "('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)",
        name="ck_customer_month_viewing_hours_valid",
    ),
)