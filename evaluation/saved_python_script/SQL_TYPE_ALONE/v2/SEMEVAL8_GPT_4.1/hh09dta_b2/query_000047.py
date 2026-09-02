def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]
    df_nna = tables["ii_nna"]

    # 1. Households with at least one member who owns financial assets/afores (ah03h == 1)
    owns_fin_assets = df_ah[df_ah["ah03h"] == 1.0]["folio"].unique()

    # 2. For each household, get the total number of times their house, business, or parcel has been entered/robbed since 2005 (vlh18a)
    # Use the maximum vlh18a per household (since it's household-level)
    df_vlh_agg = df_vlh.groupby("folio", as_index=False)["vlh18a"].max()

    # 3. Households that do NOT own or share a non-ag business (nna01 != 1)
    # nna01: 1 = Yes, 2 = No
    # For each household, if any member has nna01 == 1, then the household owns/shares a non-ag business
    nna_agg = df_nna.groupby("folio")["nna01"].min().reset_index()
    # Households where nna01 != 1 (i.e., min != 1)
    no_nonagbiz_folios = nna_agg[nna_agg["nna01"] != 1.0]["folio"].unique()

    # 4. Compute average vlh18a for households that do NOT own/share a non-ag business
    # Merge to get vlh18a for these households
    df_no_nonagbiz = df_vlh_agg[df_vlh_agg["folio"].isin(no_nonagbiz_folios)]
    avg_vlh18a_no_nonagbiz = df_no_nonagbiz["vlh18a"].mean(skipna=True)

    # 5. Select households that:
    #   - have at least one member who owns financial assets/afores
    #   - whose total number of times entered/robbed since 2005 > average for households that do not own/share a non-ag business
    df_result = df_vlh_agg[
        (df_vlh_agg["folio"].isin(owns_fin_assets)) &
        (df_vlh_agg["vlh18a"] > avg_vlh18a_no_nonagbiz)
    ][["folio", "vlh18a"]].reset_index(drop=True)

    df_result = df_result.rename(columns={"folio": "Household ID", "vlh18a": "Total times entered/robbed since 2005"})
    return df_result