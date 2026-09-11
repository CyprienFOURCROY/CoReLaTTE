def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_inr = tables["ii_inr"]

    # Step 1: Households in Oaxaca (ent == 20)
    oaxaca_folios = df_portad[df_portad["ent"] == 20]["folio"].unique()

    # Step 2: Households that use a plot/land for farming (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1]["folio"].unique()

    # Step 3: Households that reported producing/selling eggs in last 12 months (inr02d == 1)
    inr_eggs = df_inr[df_inr["inr02d"] == 1][["folio", "inr04d"]]

    # Step 4: Filter to Oaxaca, plot users, and egg producers
    eligible_folios = set(oaxaca_folios) & set(su_plot)
    inr_eggs = inr_eggs[inr_eggs["folio"].isin(eligible_folios)]

    # Step 5: Compute national average eggs sold last month (inr04d), among all who produced/sold eggs
    national_eggs = df_inr[df_inr["inr02d"] == 1]["inr04d"]
    national_avg = national_eggs.dropna().mean()

    # Step 6: Households that sold at least the national average last month
    result = inr_eggs.dropna(subset=["inr04d"])
    result = result[result["inr04d"] >= national_avg]

    # Step 7: Rename columns for clarity
    result = result.rename(columns={"folio": "household_id", "inr04d": "eggs_sold_last_month"})

    # Reset index for clean output
    return result[["household_id", "eggs_sold_last_month"]].reset_index(drop=True)