import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].dropna(subset=["folio"])
    df_in = tables["ii_in"][["folio", "in02a10"]]
    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh01l"]]

    # Oaxaca households
    oax_folios = df_portad.loc[df_portad["ent"] == 20, "folio"].dropna().unique()

    # Average among Oaxaca households with positive receipts
    df_in_oax = df_in[df_in["folio"].isin(oax_folios)].copy()
    avg_positive = df_in_oax.loc[df_in_oax["in02a10"] > 0, "in02a10"].mean()

    # Households that feel very safe or safe and agree people help neighbors
    cond_vlh = df_vlh[
        df_vlh["folio"].isin(oax_folios)
        & df_vlh["vlh04"].isin([1.0, 2.0])
        & df_vlh["vlh01l"].isin([1.0, 2.0])
    ].copy()

    merged = cond_vlh.merge(df_in, on="folio", how="left")

    count = merged.loc[merged["in02a10"] > avg_positive, "folio"].nunique()

    return pd.DataFrame({"households_count": [int(count)]})