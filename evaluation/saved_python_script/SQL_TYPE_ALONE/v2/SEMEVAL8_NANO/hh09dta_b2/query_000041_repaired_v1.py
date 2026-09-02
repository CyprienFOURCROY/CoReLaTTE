def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]

    # Filter households where HHM owns a domestic appliance (ah03g == 1)
    ah_owned = df_ah[df_ah["ah03g"] == 1][["folio"]].drop_duplicates()

    # Merge with portad to get 'ent' (state) info
    portad_with_state = pd.merge(ah_owned, df_portad[["folio", "ent"]], on="folio", how="inner")

    # For each household, determine if any member owns a domestic appliance
    # Since 'ah03g' is per individual, check if any individual in household owns it
    ah_individuals = df_ah[["folio", "ah03g"]]
    household_appliance = ah_individuals.groupby("folio")["ah03g"].any().reset_index()
    household_appliance = household_appliance.rename(columns={"ah03g": "has_domestic_appliance"})

    # Merge with portad to get 'ent'
    household_data = pd.merge(household_appliance, df_portad[["folio", "ent"]], on="folio", how="inner")

    # Filter households with at least 25 households per state
    household_counts = household_data.groupby("ent").size()
    states_with_25 = household_counts[household_counts >= 25].index.tolist()

    # Filter data for these states
    filtered = household_data[household_data["ent"].isin(states_with_25)]

    # For each household, get 'vlh12a_c' (no forced home entry since 2005) and 'vlh12a' (forced entry since 2005)
    # Merge with ii_vlh to get 'vlh12a_c' and 'vlh12a'
    df_vlh = tables["ii_vlh"]
    household_vlh = pd.merge(filtered[["folio", "ent"]], df_vlh[["folio", "vlh12a_c", "vlh12a"]], on="folio", how="inner")

    # Count total households, households with 'vlh12a_c' == 3 (no since 2005), and 'vlh12a' == 1 (yes since current dwelling)
    result_list = []
    for state in states_with_25:
        state_households = household_vlh[household_vlh["ent"] == state]
        total_households = len(state_households)
        no_since_2005 = len(state_households[state_households["vlh12a_c"] == 3])
        yes_current_since_2005 = len(state_households[state_households["vlh12a"] == 1])
        result_list.append({
            "ent": state,
            "total_households": total_households,
            "no_since_2005": no_since_2005,
            "yes_since_2005": yes_current_since_2005
        })

    # Create DataFrame
    result_df = pd.DataFrame(result_list)

    # Map 'ent' codes to state names for clarity (optional, but not required)
    # For now, return as is
    return result_df