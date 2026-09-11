def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Households with a value for total debts + interests (crh04_2 not null)
    crh_debt = df_crh.loc[df_crh["crh04_2"].notnull(), ["folio"]].drop_duplicates()

    # Households with at least one member who owns an electronic device (ah03e == 1)
    ah_electronic = df_ah.loc[df_ah["ah03e"] == 1, ["folio"]].drop_duplicates()

    # Intersection: households that satisfy both conditions
    eligible_households = pd.merge(crh_debt, ah_electronic, on="folio", how="inner")

    # Get state for each household (from ii_portad, one row per folio)
    folio_ent = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])
    eligible_households = pd.merge(eligible_households, folio_ent, on="folio", how="left")

    # Count households per state
    state_counts = eligible_households.groupby("ent").agg(household_count=("folio", "nunique")).reset_index()

    # Compute average count across states
    avg_count = state_counts["household_count"].mean()

    # Filter states with count >= average
    result = state_counts[state_counts["household_count"] >= avg_count].copy()
    result = result.rename(columns={"ent": "state"})

    return result.reset_index(drop=True)