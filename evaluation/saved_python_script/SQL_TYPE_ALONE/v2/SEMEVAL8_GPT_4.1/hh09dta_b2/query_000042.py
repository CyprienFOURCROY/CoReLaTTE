def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]

    # Filter Oaxaca households
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # Merge with ii_nna to get non-ag business ownership
    oaxaca_nna = oaxaca_households.merge(df_nna, on="folio", how="left")

    # Merge with ii_ah to get domestic appliance values
    # Only keep one row per household (folio) for max value
    df_ah_dom = df_ah[["folio", "ah04g_2"]].copy()

    # For each household, get the highest-valued domestic appliance (ah04g_2)
    df_ah_dom_max = df_ah_dom.groupby("folio", as_index=False)["ah04g_2"].max()

    # Merge with oaxaca_nna
    oaxaca_full = oaxaca_nna.merge(df_ah_dom_max, on="folio", how="left")

    # Households with non-ag business (nna01 == 1.0)
    with_business = oaxaca_full[oaxaca_full["nna01"] == 1.0].copy()

    # Households without non-ag business (nna01 == 2.0)
    without_business = oaxaca_full[oaxaca_full["nna01"] == 2.0].copy()

    # Compute average of highest-valued domestic appliance among households without business
    avg_domestic_appliance = without_business["ah04g_2"].dropna().mean()

    # Select households with business whose highest-valued domestic appliance > average
    result = with_business[
        (with_business["ah04g_2"].notna()) &
        (with_business["ah04g_2"] > avg_domestic_appliance)
    ][["folio", "ah04g_2"]].sort_values("ah04g_2", ascending=False).reset_index(drop=True)

    result = result.rename(columns={"ah04g_2": "highest_domestic_appliance_value"})

    return result