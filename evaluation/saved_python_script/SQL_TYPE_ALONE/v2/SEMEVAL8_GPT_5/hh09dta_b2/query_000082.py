import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_crh = tables["ii_crh"][["folio", "crh02_1"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh01t", "vlh12a_a", "vlh12a_b", "vlh14a", "vlh16a", "vlh18a"]].copy()

    df = pd.merge(df_crh, df_vlh, on="folio", how="inner")

    # Average favors frequency among households that did not incur debts (crh02_1 == 2)
    valid_favors = df["vlh01t"].isin([1, 2, 3, 4])
    no_debt_mask = (df["crh02_1"] == 2) & valid_favors
    avg_no_debt = df.loc[no_debt_mask, "vlh01t"].mean()

    # Households that incurred debts and had at least one robbery/forced entry since 2005
    debt_mask = df["crh02_1"] == 1
    rob_mask = (
        (df["vlh18a"].fillna(0) > 0)
        | (df["vlh12a_a"] == 1)
        | (df["vlh12a_b"] == 2)
        | (df["vlh14a"] == 1)
        | (df["vlh16a"] == 1)
    )

    if pd.isna(avg_no_debt):
        count = 0
    else:
        count = df.loc[debt_mask & rob_mask & valid_favors & (df["vlh01t"] > avg_no_debt), "folio"].nunique()

    return pd.DataFrame({"num_households": [int(count)]})