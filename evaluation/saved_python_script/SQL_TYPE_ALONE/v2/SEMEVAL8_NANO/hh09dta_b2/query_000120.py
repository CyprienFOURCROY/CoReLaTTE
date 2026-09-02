def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    crh = tables["ii_crh"]
    en = tables["ii_enriched"]
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]

    # Merge household info with crh on 'folio'
    merged = pd.merge(oaxaca_households, crh, on="folio", how="inner")

    # Filter households that reported amounts for both 'crh02d' and 'crh04d'
    # 'crh02d' is money owed credit/loans last 12 months
    # 'crh04d' is total debts + interests
    filtered = merged[
        (~merged["crh02d"].isna()) & (~merged["crh04d"].isna())
    ]

    # For each household, determine if they own at least one motor vehicle
    # Motor vehicle ownership is indicated by 'ah03d' == 1 (Yes)
    # Merge with ah table on 'folio' and 'ls' (individual id)
    ah_filtered = pd.merge(
        filtered[["folio", "ls"]],
        ah[["folio", "ls", "ah03d"]],
        on=["folio", "ls"],
        how="left"
    )

    # For each household, check if any individual owns a motor vehicle
    ownership = ah_filtered.groupby("folio")["ah03d"].apply(
        lambda x: any(x == 1)
    ).reset_index()

    # Merge ownership info back to main dataframe
    final_df = pd.merge(filtered, ownership, on="folio", how="left")
    final_df.rename(columns={"ah03d": "owns_motor_vehicle"}, inplace=True)

    # Group by ownership status
    group_stats = final_df.groupby("owns_motor_vehicle").agg(
        household_count=("folio", "nunique"),
        average_debt=("crh04d", "mean")
    ).reset_index()

    # Map boolean to descriptive string for clarity
    group_stats["owns_motor_vehicle"] = group_stats["owns_motor_vehicle"].map({True: "Owns at least one motor vehicle", False: "Does not own motor vehicle"})

    return group_stats[['owns_motor_vehicle', 'household_count', 'average_debt']]