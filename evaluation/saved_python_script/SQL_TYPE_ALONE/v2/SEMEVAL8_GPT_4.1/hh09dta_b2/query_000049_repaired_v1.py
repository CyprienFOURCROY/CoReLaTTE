def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_vlh = tables["ii_vlh"]

    # 1. Households with at least one member younger than 30
    df_young = df_portad[df_portad["edad"] < 30]
    young_folios = set(df_young["folio"].unique())

    # 2. Households that own/share a non-ag business (nna01 == 1)
    df_nna_yes = df_nna[df_nna["nna01"] == 1.0]
    nna_folios = set(df_nna_yes["folio"].unique())

    # 3. Households with zero robbery/break-in incidents since 2005 (vlh18a == 0.0 or nan)
    df_vlh_zero = df_vlh[(df_vlh["vlh18a"].isna()) | (df_vlh["vlh18a"] == 0.0)]
    vlh_folios = set(df_vlh_zero["folio"].unique())

    # 4. Intersection of all three sets
    eligible_folios = young_folios & nna_folios & vlh_folios

    # 5. For these folios, get the state (ent) from ii_portad (one row per household)
    df_households = df_portad[df_portad["folio"].isin(eligible_folios)][["folio", "ent"]].drop_duplicates("folio")

    # 6. Group by state and count households, sort descending
    result = (
        df_households.groupby("ent")
        .size()
        .reset_index(name="household_count")
        .sort_values("household_count", ascending=False)
        .reset_index(drop=True)
    )

    return result