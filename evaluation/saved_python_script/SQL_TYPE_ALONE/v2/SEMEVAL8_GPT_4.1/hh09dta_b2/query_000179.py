def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # Adults (18+) in Oaxaca (ent==20)
    adults_oaxaca = df_portad[(df_portad["ent"] == 20) & (df_portad["edad"] >= 18)]

    # Merge with ii_vlh on folio to get forced-entry robbery since 2005 (vlh12a_a==1)
    merged = adults_oaxaca.merge(df_vlh[["folio", "vlh12a_a"]], on="folio", how="inner")
    robbed = merged[merged["vlh12a_a"] == 1]

    # Merge with ii_ah to get poultry ownership (ah03m==1 for any HHM in household)
    # Poultry ownership is at household level, so check for any ah03m==1 per folio
    poultry_ownership = (
        df_ah.groupby("folio")["ah03m"]
        .apply(lambda x: 1 if (x == 1).any() else 0)
        .reset_index()
        .rename(columns={"ah03m": "owns_poultry"})
    )

    robbed = robbed.merge(poultry_ownership, on="folio", how="left")
    robbed["owns_poultry"] = robbed["owns_poultry"].fillna(0).astype(int)

    # Compute overall mean age in this group
    mean_age = robbed["edad"].mean()

    # For each poultry ownership group, compute:
    # - average age
    # - number of adults older than the group's mean age
    result = []
    for owns_poultry, group in robbed.groupby("owns_poultry"):
        avg_age = group["edad"].mean()
        count_older = (group["edad"] > avg_age).sum()
        result.append({
            "owns_poultry": owns_poultry,
            "average_age": avg_age,
            "num_older_than_group_mean": count_older
        })

    return pd.DataFrame(result)