def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Households that use a plot/land for farming (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1.0][["folio", "su237"]]

    # Households that have bank savings (crh01_1b == 2)
    crh_bank = df_crh[df_crh["crh01_1b"] == 2.0][["folio"]]

    # Merge to get households that satisfy both conditions
    merged = su_plot.merge(crh_bank, on="folio", how="inner")

    # Only consider those with a valid expense on workers (su237 not null)
    merged = merged[merged["su237"].notnull()]

    # Calculate the average expense on workers among these households
    avg_expense = merged["su237"].mean()

    # Filter households that spent more than the average
    result = merged[merged["su237"] > avg_expense].copy()

    # Sort from highest to lowest expense
    result = result.sort_values(by="su237", ascending=False)

    # Return only Household ID and amount spent
    return result[["folio", "su237"]].rename(columns={"folio": "Household ID", "su237": "Amount Spent"}).reset_index(drop=True)