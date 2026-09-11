def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_se = tables["ii_se"]

    # 1. Households with at least one adult (age 18+)
    adults = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = set(adults["folio"].unique())

    # 2. Households that produced or sold meat in last 12 months (inr02c == 1)
    meat_hh = set(df_inr[df_inr["inr02c"] == 1]["folio"].unique())

    # 3. Households that experienced disease/accident/hospitalization in past 5 years (se01b == 1)
    disease_hh = set(df_se[df_se["se01b"] == 1]["folio"].unique())

    # 4. Intersection: households meeting all three criteria
    eligible_hh = hh_with_adult & meat_hh & disease_hh

    # 5. Get state for each eligible household
    eligible_portad = df_portad[df_portad["folio"].isin(eligible_hh)][["folio", "ent"]].drop_duplicates()

    # 6. Count households per state (unique folio per ent)
    state_counts = eligible_portad.groupby("ent")["folio"].nunique().reset_index()
    state_counts = state_counts.rename(columns={"folio": "household_count"})

    # 7. Compute average count across all states
    avg_count = state_counts["household_count"].mean()

    # 8. Filter states with count >= average
    result = state_counts[state_counts["household_count"] >= avg_count].copy()
    result["ent"] = result["ent"].astype(int)

    return result.reset_index(drop=True)