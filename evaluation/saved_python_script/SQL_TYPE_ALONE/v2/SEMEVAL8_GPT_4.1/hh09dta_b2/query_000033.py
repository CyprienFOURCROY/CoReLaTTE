def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    import pandas as pd

    # Load tables
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # 1. Households in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one adult (edad >= 18)
    df_adults = df_oaxaca[df_oaxaca["edad"] >= 18.0]
    hh_with_adult = set(df_adults["folio"].unique())

    # 3. Households with a member's death in last 5 years (se01a == 1)
    df_se_oax = df_se[df_se["folio"].isin(hh_with_adult)]
    hh_with_death = set(df_se_oax[df_se_oax["se01a"] == 1.0]["folio"].unique())

    # 4. Households in Oaxaca, with at least one adult, and a member's death
    hh_target = hh_with_adult & hh_with_death

    # 5. For these households, determine if any member owns an electronic device (ah03e == 1)
    df_ah_oax = df_ah[df_ah["folio"].isin(hh_target)]
    owns_electronic = df_ah_oax.groupby("folio")["ah03e"].apply(lambda x: (x == 1.0).any()).reset_index()
    owns_electronic["group"] = owns_electronic["ah03e"].map({True: "any_member_owns", False: "none_owns"})
    # Map folio to group
    folio_to_group = dict(zip(owns_electronic["folio"], owns_electronic["group"]))

    # 6. Get number of times house/business/parcel was entered/robbed since 2005 (vlh18a)
    df_vlh_oax = df_vlh[df_vlh["folio"].isin(hh_target)][["folio", "vlh18a"]].copy()

    # 7. Merge group info
    df_vlh_oax["group"] = df_vlh_oax["folio"].map(folio_to_group)
    # Only keep folios with group assigned (should be all in hh_target)
    df_vlh_oax = df_vlh_oax[~df_vlh_oax["group"].isna()]

    # 8. Compute overall average (across all these households, regardless of group)
    overall_avg = df_vlh_oax["vlh18a"].mean(skipna=True)

    # 9. For each group, compute group average and count of households
    group_stats = (
        df_vlh_oax.groupby("group")
        .agg(
            avg_robbed_since_2005=("vlh18a", "mean"),
            n_households=("folio", "nunique")
        )
        .reset_index()
    )

    # 10. Select groups with average >= overall average
    group_stats = group_stats[group_stats["avg_robbed_since_2005"] >= overall_avg]

    # 11. Return group name and n_households
    return group_stats[["group", "n_households"]].reset_index(drop=True)