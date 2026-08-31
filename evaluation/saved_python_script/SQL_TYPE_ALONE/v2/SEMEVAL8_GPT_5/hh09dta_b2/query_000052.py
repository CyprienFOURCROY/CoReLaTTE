import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01", "su234"]].copy()
    df_se = tables["ii_se"][["folio", "se01e"]].copy()

    # Households that use land for farming
    land_using = df_su[df_su["su01"] == 1].copy()

    # Compute average seed expense among land-using households that did not lose total crop
    land_with_se = land_using.merge(df_se, on="folio", how="left")
    ref_group = land_with_se[land_with_se["se01e"] == 3]
    avg_seed_expense = ref_group["su234"].mean()

    # Select households with seed expense greater than the computed average
    result = land_using[land_using["su234"] > avg_seed_expense][["folio", "su234"]].copy()
    result = result.sort_values(by="su234", ascending=False).reset_index(drop=True)

    return result