def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Filter Oaxaca households (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]]

    # Only consider households that received direct income from Other Government Program (in02a10 > 0)
    df_in_ogp = df_in[df_in["in02a10"].notna() & (df_in["in02a10"] > 0)][["folio", "in02a10"]]

    # Compute overall average among all recipients
    avg_ogp = df_in_ogp["in02a10"].mean()

    # Merge Oaxaca households with OGP recipients
    oaxaca_ogp = pd.merge(oaxaca_households, df_in_ogp, on="folio", how="inner")

    # Filter those who received more than the average
    result = oaxaca_ogp[oaxaca_ogp["in02a10"] > avg_ogp].copy()

    # Rename columns for clarity
    result = result.rename(columns={"in02a10": "direct_income_other_gov_program"})

    # Reset index for clean output
    result = result.reset_index(drop=True)

    return result[["folio", "direct_income_other_gov_program"]]