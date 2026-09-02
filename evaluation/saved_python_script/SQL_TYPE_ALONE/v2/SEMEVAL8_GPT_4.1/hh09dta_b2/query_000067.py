def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]

    # Step 1: Oaxaca households (ent == 20)
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0][["folio"]]

    # Step 2: Households that use a plot/land (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1.0][["folio"]]

    # Step 3: Households that sold eggs last month (inr04d not null)
    inr_eggs = df_inr[~df_inr["inr04d"].isna()][["folio", "inr04d"]]

    # Step 4: Merge to get relevant households
    merged = (
        oaxaca_folios
        .merge(su_plot, on="folio")
        .merge(inr_eggs, on="folio")
    )

    # Step 5: Add non-ag business info (nna01: 1=Yes, 2=No)
    merged = merged.merge(df_nna[["folio", "nna01"]], on="folio", how="left")

    # Step 6: Split into with and without non-ag business
    with_nonag = merged[merged["nna01"] == 1.0]
    without_nonag = merged[merged["nna01"] == 2.0]

    # Step 7: Compute average eggs sold last month for with_nonag
    avg_eggs_with_nonag = with_nonag["inr04d"].mean()

    # Step 8: Select households without non-ag business and inr04d > avg
    result = without_nonag[without_nonag["inr04d"] > avg_eggs_with_nonag][["folio", "inr04d"]]

    # Step 9: Sort from highest to lowest quantity
    result = result.sort_values(by="inr04d", ascending=False).reset_index(drop=True)
    result = result.rename(columns={"inr04d": "last_month_eggs_sold_qty"})

    return result