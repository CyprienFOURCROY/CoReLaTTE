def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]
    df_in = tables["ii_in"]

    # 1. Households in Oaxaca (ent==20) with at least one member aged 60+
    oaxaca_60plus = df_portad.loc[(df_portad["ent"] == 20) & (df_portad["edad"] >= 60), "folio"].unique()

    # 2. Households that use land for farming (su01==1)
    land_farming = df_su.loc[df_su["su01"] == 1, "folio"].unique()

    # 3. Households that own/share a non-ag business (nna01==1)
    nonag_biz = df_nna.loc[df_nna["nna01"] == 1, "folio"].unique()

    # 4. Households that reported receiving income from Other Government Program in last 12 months
    # (in01a10_1==1) and have a direct receipt amount (in02a10 not null)
    df_in_ogp = df_in.loc[(df_in["in01a10_1"] == 1) & (~df_in["in02a10"].isna()), ["folio", "in02a10"]]

    # 5. Intersect all conditions
    eligible_folios = set(oaxaca_60plus) & set(land_farming) & set(nonag_biz)
    df_in_ogp = df_in_ogp[df_in_ogp["folio"].isin(eligible_folios)]

    # 6. Per-household average amount of direct receipts from that program
    df_avg = df_in_ogp.groupby("folio", as_index=False)["in02a10"].mean()

    # 7. Compute overall average for this group
    overall_avg = df_avg["in02a10"].mean()

    # 8. Filter households above the overall average
    df_result = df_avg[df_avg["in02a10"] > overall_avg].copy()

    # 9. Sort highest to lowest
    df_result = df_result.sort_values("in02a10", ascending=False).reset_index(drop=True)

    # 10. Rename columns for clarity
    df_result = df_result.rename(columns={"folio": "Household ID", "in02a10": "Average Direct Receipts (Other Gov Program)"})

    return df_result