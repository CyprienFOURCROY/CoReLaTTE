def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_su = tables["ii_su"]
    df_se = tables["ii_se"]

    # Households that use land for farming
    land_users = df_su[df_su["su01"] == 1.0].copy()

    # Merge with se table to get info about lost total crop in last 5 years
    # se01e == 1 means lost total crop, se01e == 3 means did NOT lose total crop
    df_merged = land_users.merge(df_se[["folio", "se01e"]], on="folio", how="left")

    # Compute average seed expense among land-using households that did NOT lose total crop
    mask_no_loss = df_merged["se01e"] == 3.0
    avg_seed_expense = df_merged.loc[mask_no_loss, "su234"].mean()

    # Households that use land for farming and have seed expense > average
    mask_expense = land_users["su234"] > avg_seed_expense
    result = land_users.loc[mask_expense, ["folio", "su234"]].copy()
    result = result.rename(columns={"su234": "seed_expense"})

    # Sort from highest to lowest expense
    result = result.sort_values("seed_expense", ascending=False).reset_index(drop=True)

    return result