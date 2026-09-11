def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_vlh = tables["ii_vlh"]
    df_nna = tables["ii_nna"]

    # 1. Households with at least one member aged 18–29
    hh_with_young = df_portad.loc[
        df_portad["edad"].between(18, 29, inclusive="both"),
        "folio"
    ].unique()

    # 2. Households with any shock in last 5 years (any se01a-f == 1)
    shock_cols = ["se01a", "se01b", "se01c", "se01d", "se01e", "se01f"]
    df_se_shock = df_se.loc[df_se[shock_cols].eq(1).any(axis=1), "folio"].unique()

    # 3. Households with at least one break-in/robbery of house, business, or parcel since 2005
    # (vlh12a_a == 1 or vlh12a_b == 2 or vlh14a == 1 or vlh16a == 1)
    df_vlh_robbery = df_vlh[
        (df_vlh["vlh12a_a"] == 1) |
        (df_vlh["vlh12a_b"] == 2) |
        (df_vlh["vlh14a"] == 1) |
        (df_vlh["vlh16a"] == 1)
    ]["folio"].unique()

    # Intersection of all three conditions
    eligible_folios = set(hh_with_young) & set(df_se_shock) & set(df_vlh_robbery)

    # 4. For these households, get nna02 (number of non-ag businesses owned/shared in last 12 months)
    df_nna_eligible = df_nna[df_nna["folio"].isin(eligible_folios)]

    # Only consider rows where nna02 is not null
    nna02_vals = df_nna_eligible["nna02"].dropna()

    # Compute average (if no eligible, result is np.nan)
    avg_nna02 = nna02_vals.mean() if not nna02_vals.empty else np.nan

    return pd.DataFrame({"average_non_ag_businesses_last_12_months": [avg_nna02]})