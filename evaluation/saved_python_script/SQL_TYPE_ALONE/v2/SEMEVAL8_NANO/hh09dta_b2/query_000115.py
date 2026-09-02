def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]

    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]

    # Merge with ii_crh on 'folio'
    crh_merged = pd.merge(oaxaca_households, df_crh, on="folio", how="inner")

    # Filter households where a household member reported disease/accident/hospitalization in last 5 years (se01b == 1)
    se_filtered = pd.merge(crh_merged, df_se, on="folio", how="inner")
    disease_households = se_filtered[se_filtered["se01b"] == 1]

    # Merge with ii_ah on 'folio' and 'ls' (individual ID)
    ah_merged = pd.merge(disease_households, df_ah, on=["folio", "ls"], how="inner")

    # Filter households where HHM owns a motor vehicle (ah03d == 1)
    motor_vehicle_owners = ah_merged[ah_merged["ah03d"] == 1]

    # Select relevant columns: 'folio', 'crh04_2' (total debts + interests), 'ah04d_2' (motor vehicle value)
    relevant_df = motor_vehicle_owners[["folio", "crh04_2", "ah04d_2"]]

    # Drop rows with missing 'crh04_2' or 'ah04d_2'
    relevant_df = relevant_df.dropna(subset=["crh04_2", "ah04d_2"])

    # Group by 'folio' to get household-level data
    household_group = relevant_df.groupby("folio").agg({
        "crh04_2": "max",
        "ah04d_2": "max"
    }).reset_index()

    # Calculate average motor vehicle value among these households
    avg_vehicle_value = household_group["ah04d_2"].mean()

    # Filter households with motor vehicle value below the average
    below_avg_vehicles = household_group[household_group["ah04d_2"] < avg_vehicle_value]

    # For these households, get the total debts + interest
    debts_below_avg = relevant_df[relevant_df["folio"].isin(below_avg_vehicles["folio"])]

    # Compute the average total debts + interest
    average_debt = debts_below_avg["crh04_2"].mean()

    return pd.DataFrame({"average_total_debt": [average_debt]})