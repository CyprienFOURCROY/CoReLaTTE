def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    in_df = tables["ii_in"]
    ah = tables["ii_ah"]

    # Filter households with at least one member owning a motor vehicle
    motor_vehicle_mask = ah["ah03d"] == 1
    households_with_vehicle = ah[motor_vehicle_mask][["folio"]].drop_duplicates()

    # Filter households that have at least 50 members owning a motor vehicle
    # (Assuming each row in ah corresponds to a household member, so count per household)
    vehicle_counts = ah[motor_vehicle_mask].groupby("folio").size()
    households_with_min50 = vehicle_counts[vehicle_counts >= 50].index

    # Filter households with at least one member owning a motor vehicle and count >=50
    target_households = households_with_vehicle[
        households_with_vehicle["folio"].isin(households_with_min50)
    ]["folio"]

    # Filter households in portad
    portad_filtered = portad[portad["folio"].isin(target_households)]

    # Merge in_df with portad to get 'ent' (state) info
    in_merged = in_df.merge(portad_filtered[["folio", "ent"]], on="folio", how="inner")

    # Filter households where 'in02k' (amount received directly from Other Government Program) > 0
    in02k_positive = in_merged[in_merged["in02k"] > 0]

    # Group by state ('ent') and compute mean of 'in02k'
    result = (
        in02k_positive.groupby("ent")["in02k"]
        .mean()
        .reset_index()
        .rename(columns={"ent": "state", "in02k": "avg_amount"})
    )

    # Filter states with at least 50 households (since we filtered households with >=50 members owning vehicle)
    # But the problem states "among states with at least 50 households where at least one member owns a vehicle"
    # So count households per state
    household_counts = (
        in02k_positive.groupby("ent")["folio"]
        .nunique()
        .reset_index()
        .rename(columns={"folio": "household_count"})
    )

    states_with_50_households = household_counts[
        household_counts["household_count"] >= 50
    ]["ent"]

    # Filter result to only these states
    result_filtered = result[result["state"].isin(states_with_50_households)]

    # Map 'ent' to state names for clarity (optional, but not required)
    # For ranking, just use 'avg_amount'
    result_sorted = result_filtered.sort_values(by="avg_amount", ascending=False).reset_index(drop=True)

    return result_sorted