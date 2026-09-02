def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_in = tables["ii_in"]

    # 1. Find households with at least one member aged 65 or older
    elderly_households = df_portad.loc[df_portad["edad"] >= 65, "folio"].unique()

    # 2. Filter crh for those households, and where total debts + interests is reported (crh04_1 == 1 and crh04_2 not null)
    crh_elderly = df_crh[
        (df_crh["folio"].isin(elderly_households)) &
        (df_crh["crh04_1"] == 1.0) &
        (~df_crh["crh04_2"].isna())
    ][["folio", "crh04_2"]]

    # 3. Compute average debt for elderly households (use only those with a value)
    avg_debt = crh_elderly["crh04_2"].mean()

    # 4. Keep only those with debt > average
    crh_above_avg = crh_elderly[crh_elderly["crh04_2"] > avg_debt]

    # 5. Merge with ii_in to get Other Government Program amount (in02a10)
    # Only keep positive amounts
    df_in_ogp = df_in[["folio", "in02a10"]].copy()
    merged = crh_above_avg.merge(df_in_ogp, on="folio", how="left")
    result = merged[(~merged["in02a10"].isna()) & (merged["in02a10"] > 0)]

    # 6. Sort by debt descending
    result = result.sort_values("crh04_2", ascending=False)

    # 7. Rename columns as requested
    result = result.rename(columns={
        "folio": "Household ID",
        "crh04_2": "total debts + interests",
        "in02a10": "Other Government Program amount"
    })[["Household ID", "total debts + interests", "Other Government Program amount"]]

    return result.reset_index(drop=True)