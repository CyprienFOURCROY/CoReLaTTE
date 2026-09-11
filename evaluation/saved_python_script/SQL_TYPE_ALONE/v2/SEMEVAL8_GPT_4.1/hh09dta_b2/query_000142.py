def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_nna = tables["ii_nna"]
    df_vlh = tables["ii_vlh"]

    # 1. Households that own/share a non-ag business (nna01 == 1)
    nna = df_nna[df_nna["nna01"] == 1]

    # 2. Merge with vlh to get safety-at-home and robbery counts
    merged = nna.merge(df_vlh, on="folio", how="inner")

    # 3. Filter for feeling unsafe or very unsafe at home (vlh04 == 3 or 4)
    unsafe = merged[merged["vlh04"].isin([3.0, 4.0])]

    # 4. Only consider those with a non-null vlh18a (total times entered/robbed since 2005)
    unsafe = unsafe[~unsafe["vlh18a"].isnull()]

    # 5. Compute average vlh18a for this group
    avg_vlh18a = unsafe["vlh18a"].mean()

    # 6. Select those above the average
    above_avg = unsafe[unsafe["vlh18a"] > avg_vlh18a]

    # 7. Prepare output: Household ID, safety-at-home response, and count, sorted descending by count
    result = above_avg[["folio", "vlh04", "vlh18a"]].copy()
    result = result.rename(columns={"folio": "Household ID", "vlh04": "SafetyAtHome", "vlh18a": "RobberyCountSince2005"})
    result = result.sort_values(by="RobberyCountSince2005", ascending=False).reset_index(drop=True)

    return result