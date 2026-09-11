def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    in_df = tables["ii_in"]

    # Filter households with at least one member aged 60 or older
    seniors = portad[portad["edad"] >= 60]
    senior_folios = seniors["folio"].unique()

    # Filter crh for these households with total debts + interests > 0
    crh_seniors = crh[crh["folio"].isin(senior_folios)]
    crh_seniors = crh_seniors[crh_seniors["crh04_1"] == 1]  # total debts + interests reported
    crh_seniors = crh_seniors[crh_seniors["crh04_2"] > 0]  # amount > 0

    # Compute average of crh04_2 for these households
    avg_debt_amount = crh_seniors["crh04_2"].mean()

    # Filter households with total debts + interests above the average
    households_above_avg_debt = crh_seniors[crh_seniors["crh04_2"] > avg_debt_amount]
    households_folios = households_above_avg_debt["folio"].unique()

    # Filter in_df for these households and where they received from the "Other Government Program"
    in_filtered = in_df[
        (in_df["folio"].isin(households_folios))
        & (in_df["in01a10_1"] == 1)  # Participated and received income
    ]

    # Calculate the mean amount received directly from the "Other Government Program"
    mean_amount = in_filtered["in02a10"].mean()

    # Return as DataFrame
    return pd.DataFrame(
        {"average_amount": [mean_amount]}
    )