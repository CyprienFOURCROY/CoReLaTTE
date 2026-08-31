import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]

    # Oaxaca households
    oax_folios = set(df_portad.loc[df_portad["ent"] == 20.0, "folio"].dropna().unique())

    # Households that sold eggs last month (positive quantity)
    eggs = df_inr.loc[
        df_inr["folio"].isin(oax_folios) & df_inr["inr04d"].notna() & (df_inr["inr04d"] > 0),
        ["folio", "inr04d"]
    ]

    # Use a plot/land
    su_use_land = df_su.loc[df_su["su01"] == 1.0, ["folio"]]

    base = eggs.merge(su_use_land, on="folio", how="inner")

    # Merge business status
    base = base.merge(df_nna[["folio", "nna01"]], on="folio", how="left")

    # Average among comparable households WITH a non-ag business
    avg_biz = base.loc[base["nna01"] == 1.0, "inr04d"].mean()

    if np.isnan(avg_biz):
        return pd.DataFrame(columns=["folio", "inr04d"])

    # Households WITHOUT a non-ag business exceeding that average
    result = (
        base.loc[(base["nna01"] == 2.0) & (base["inr04d"] > avg_biz), ["folio", "inr04d"]]
        .sort_values("inr04d", ascending=False)
        .reset_index(drop=True)
    )

    return result