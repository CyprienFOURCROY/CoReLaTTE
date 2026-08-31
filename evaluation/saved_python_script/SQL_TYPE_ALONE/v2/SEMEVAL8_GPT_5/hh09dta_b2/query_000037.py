import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Deduplicate/aggregate household-level info
    def agg_vlh10a(s: pd.Series):
        if (s == 1.0).any():
            return 1.0
        if (s == 3.0).any():
            return 3.0
        return np.nan

    df_vlh_agg = df_vlh.groupby("folio", as_index=False).agg(
        vlh18a=("vlh18a", "min"),
        vlh10a=("vlh10a", agg_vlh10a),
    )

    # Households with zero break-ins since 2005 and who report knowing a family/friend robbed in last 12 months
    hh_mask = (df_vlh_agg["vlh18a"] == 0.0) & (df_vlh_agg["vlh10a"] == 1.0)
    hh_selected = df_vlh_agg.loc[hh_mask, ["folio", "vlh18a"]]

    # Individuals living in those households
    ind = df_portad.merge(hh_selected, on="folio", how="inner")

    # Ensure age is available
    ind = ind[ind["edad"].notna()]

    # Compute overall average age among this subset
    avg_age = ind["edad"].mean()

    # Individuals older than the average
    older = ind[ind["edad"] > avg_age]

    # Final selection and sorting
    result = older.loc[:, ["folio", "ent", "edad", "vlh18a"]].sort_values(by="edad", ascending=False).reset_index(drop=True)

    return result