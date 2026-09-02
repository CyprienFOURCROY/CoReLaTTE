def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]

    # 1. Households that received Liconsa milk in the last 12 months: in03a == 1
    df_in_liconsa = df_in[df_in["in03a"] == 1.0][["folio"]]

    # 2. Merge with df_vlh to get feeling of safety at home (vlh04)
    df_liconsa_vlh = df_in_liconsa.merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")

    # 3. Keep only those who feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_liconsa_vlh_unsafe = df_liconsa_vlh[df_liconsa_vlh["vlh04"].isin([3.0, 4.0])][["folio"]]

    # 4. Merge with df_portad to get state (ent)
    df_unsafe_ent = df_liconsa_vlh_unsafe.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # 5. Count number of such households per state
    state_counts = df_unsafe_ent.groupby("ent").size().reset_index(name="num_households")

    # 6. Compute cross-state average (only states with at least one household)
    avg_count = state_counts["num_households"].mean()

    # 7. Restrict to states with counts >= average
    state_counts_filtered = state_counts[state_counts["num_households"] >= avg_count]

    # 8. Get top five states by count (descending), tie-breaking by state code ascending
    state_counts_filtered = state_counts_filtered.sort_values(
        by=["num_households", "ent"], ascending=[False, True]
    ).head(5)

    # 9. Convert ent to int for cleaner output
    state_counts_filtered["ent"] = state_counts_filtered["ent"].astype(int)

    # 10. Reset index for output
    state_counts_filtered = state_counts_filtered.reset_index(drop=True)

    return state_counts_filtered.rename(columns={"ent": "state", "num_households": "num_households_unsafe"})