def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # 1. Households with at least one member owning a domestic appliance (ah03g == 1)
    df_ah_domestic = df_ah[df_ah["ah03g"] == 1]
    hh_with_domestic = df_ah_domestic["folio"].unique()

    # 2. For these households, get their state from ii_portad (one row per household)
    df_portad_hh = df_portad.drop_duplicates("folio")[["folio", "ent"]]
    df_domestic_hh = df_portad_hh[df_portad_hh["folio"].isin(hh_with_domestic)].copy()

    # 3. For these households, get forced entry since 2005 from ii_vlh
    #    - 'no since 2005': vlh12a_c == 3
    #    - 'yes to current dwelling since 2005': vlh12a_a == 1
    df_vlh_hh = df_vlh[df_vlh["folio"].isin(df_domestic_hh["folio"])]
    df_vlh_hh = df_vlh_hh[["folio", "vlh12a_a", "vlh12a_c"]]

    # 4. Merge state info
    df_merged = df_domestic_hh.merge(df_vlh_hh, on="folio", how="left")

    # 5. For each household, create flags
    df_merged["no_since_2005"] = (df_merged["vlh12a_c"] == 3).astype(int)
    df_merged["yes_current_since_2005"] = (df_merged["vlh12a_a"] == 1).astype(int)

    # 6. Group by state
    grouped = df_merged.groupby("ent").agg(
        total_households=("folio", "nunique"),
        no_since_2005=("no_since_2005", "sum"),
        yes_current_since_2005=("yes_current_since_2005", "sum")
    ).reset_index()

    # 7. Filter: at least 25 households, and no_since_2005 > yes_current_since_2005
    result = grouped[
        (grouped["total_households"] >= 25) &
        (grouped["no_since_2005"] > grouped["yes_current_since_2005"])
    ].copy()

    # 8. Rename ent to state for clarity
    result = result.rename(columns={"ent": "state"})

    # 9. Sort by state
    result = result.sort_values("state").reset_index(drop=True)

    return result[["state", "total_households", "no_since_2005", "yes_current_since_2005"]]