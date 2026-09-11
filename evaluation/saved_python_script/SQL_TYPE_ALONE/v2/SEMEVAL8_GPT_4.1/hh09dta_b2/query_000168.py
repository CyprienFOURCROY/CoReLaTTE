def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Step 1: Identify households with at least one adult (age >= 18)
    adults = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = adults["folio"].unique()

    # Step 2: Households that use a plot/land for farming (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1]
    hh_with_plot = su_plot["folio"].unique()

    # Step 3: Households that reported owing money on credit/loans in last 12 months (crh02_1 == 1)
    crh_owed = df_crh[df_crh["crh02_1"] == 1]
    hh_owed = crh_owed["folio"].unique()

    # Step 4: Intersection of all three conditions
    eligible_hh = set(hh_with_adult) & set(hh_with_plot) & set(hh_owed)

    # Step 5: For these households, get their state (ent) from df_portad (one row per household)
    # Use the first occurrence of each folio
    df_hh_state = df_portad[df_portad["folio"].isin(eligible_hh)][["folio", "ent"]].drop_duplicates("folio")

    # Step 6: Count number of such households per state
    state_counts = df_hh_state.groupby("ent").size().reset_index(name="num_households")

    # Step 7: Compute the average number of such households per state
    avg_num = state_counts["num_households"].mean()

    # Step 8: Filter states with more than the average
    above_avg = state_counts[state_counts["num_households"] > avg_num]

    # Step 9: Rank from highest to lowest
    result = above_avg.sort_values("num_households", ascending=False).reset_index(drop=True)

    return result