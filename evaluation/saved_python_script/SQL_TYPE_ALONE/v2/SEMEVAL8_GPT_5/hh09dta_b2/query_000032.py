import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # Households in Oaxaca
    hh_oax = df_portad.loc[df_portad["ent"] == 20.0, ["folio"]].drop_duplicates()

    # Merge with safety perception and debt information
    oax_all = (
        hh_oax
        .merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")
        .merge(df_crh[["folio", "crh04_1", "crh04_2"]], on="folio", how="left")
    )

    # Compute average debt among Oaxaca households who feel unsafe or very unsafe and reported a value
    mask_unsafe = oax_all["vlh04"].isin([3.0, 4.0])
    mask_reported = oax_all["crh04_1"] == 1.0
    avg_debt = oax_all.loc[mask_reported & mask_unsafe, "crh04_2"].mean()

    # Select households with reported values greater than this average
    res = oax_all.loc[mask_reported & (oax_all["crh04_2"] > avg_debt), ["folio", "crh04_2"]].copy()

    # Order from highest to lowest amount
    res = res.sort_values(by="crh04_2", ascending=False).reset_index(drop=True)

    return res