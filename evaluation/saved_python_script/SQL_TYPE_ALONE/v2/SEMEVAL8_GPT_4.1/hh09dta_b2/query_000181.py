def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]

    # Filter adults (age 18+)
    df_adults = df_portad[df_portad["edad"] >= 18]

    # Get households with at least one adult
    hh_with_adult = df_adults["folio"].unique()

    # Filter ii_portad to only those households
    df_portad_hh = df_portad[df_portad["folio"].isin(hh_with_adult)]

    # Get state for each household (take first occurrence)
    hh_state = df_portad_hh.groupby("folio")["ent"].first().reset_index()

    # Count number of households with at least one adult per state
    hh_state_counts = hh_state["ent"].value_counts().reset_index()
    hh_state_counts.columns = ["ent", "n_households"]

    # Only keep states with at least 50 such households
    valid_states = hh_state_counts[hh_state_counts["n_households"] >= 50]["ent"]

    # Filter households to only those in valid states
    hh_state_valid = hh_state[hh_state["ent"].isin(valid_states)]

    # Now, for these households, check if they own an electronic device
    # Merge with ii_ah to get asset ownership
    df_ah_hh = df_ah[df_ah["folio"].isin(hh_state_valid["folio"])]

    # For each household, check if any member owns an electronic device (ah03e == 1)
    owns_electronic = df_ah_hh.groupby("folio")["ah03e"].apply(lambda x: (x == 1).any()).reset_index()
    owns_electronic = owns_electronic[owns_electronic["ah03e"]]

    # Merge with state info
    owns_electronic = owns_electronic.merge(hh_state_valid, on="folio", how="left")

    # Count number of such households per state
    result = owns_electronic.groupby("ent")["folio"].nunique().reset_index()
    result.columns = ["state", "households_owning_electronic_device"]

    # Sort from highest to lowest
    result = result.sort_values("households_owning_electronic_device", ascending=False).reset_index(drop=True)

    return result