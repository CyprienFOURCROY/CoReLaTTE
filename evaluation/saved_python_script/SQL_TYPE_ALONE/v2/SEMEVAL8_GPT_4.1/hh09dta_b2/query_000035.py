def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]

    # 1. Filter Oaxaca households
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]]

    # 2. Households with positive amount received directly from Other Government Program
    df_in_ogp = df_in[df_in["in02a10"].notna() & (df_in["in02a10"] > 0)][["folio", "in02a10"]]

    # 3. Merge to get only Oaxaca households with positive OGP amount
    oaxaca_ogp = pd.merge(oaxaca_households, df_in_ogp, on="folio", how="inner")

    # 4. Get total debts + interests for these households
    df_crh_debt = df_crh[df_crh["crh04_2"].notna()][["folio", "crh04_2"]]

    # 5. Merge to get debts for Oaxaca households with positive OGP amount
    merged = pd.merge(oaxaca_ogp, df_crh_debt, on="folio", how="inner")

    # 6. Compute Oaxaca average total debts + interests
    oaxaca_debts = pd.merge(oaxaca_households, df_crh_debt, on="folio", how="inner")
    oaxaca_avg_debt = oaxaca_debts["crh04_2"].mean()

    # 7. Filter households with debts above Oaxaca average
    result = merged[merged["crh04_2"] > oaxaca_avg_debt]

    # 8. Sort from highest to lowest debt
    result = result.sort_values("crh04_2", ascending=False)

    # 9. Rename columns as requested
    result = result.rename(columns={
        "folio": "household_id",
        "crh04_2": "debt_amount",
        "in02a10": "received_amount"
    })[["household_id", "debt_amount", "received_amount"]]

    return result.reset_index(drop=True)