def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_nna = tables["ii_nna"]

    # 1. Compute overall average age
    overall_avg_age = df_portad["edad"].mean()

    # 2. Compute average age per state
    state_avg_age = df_portad.groupby("ent")["edad"].mean()

    # 3. Find states where avg age > overall avg
    states_higher_avg = state_avg_age[state_avg_age > overall_avg_age].index.tolist()

    # 4. Get folios in those states
    folios_in_states = df_portad[df_portad["ent"].isin(states_higher_avg)]["folio"].unique()

    # 5. Households that lost total crop in last 5 years (se01e == 1)
    lost_crop_folios = df_se[df_se["se01e"] == 1]["folio"].unique()

    # 6. Households that own/share non-ag business (nna01 == 1)
    own_nonag_folios = df_nna[df_nna["nna01"] == 1]["folio"].unique()

    # 7. Intersection: folios in states with higher avg age, lost crop, own/share non-ag business
    eligible_folios = set(folios_in_states) & set(lost_crop_folios) & set(own_nonag_folios)

    # 8. Count households
    count = len(eligible_folios)

    return pd.DataFrame({"household_count": [count]})