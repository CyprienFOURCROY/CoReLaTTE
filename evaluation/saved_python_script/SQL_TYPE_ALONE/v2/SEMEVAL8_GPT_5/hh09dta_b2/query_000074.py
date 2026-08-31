import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_inr = tables["ii_inr"]

    oax_folios = set(df_portad.loc[df_portad["ent"] == 20, "folio"].dropna().unique())

    s_mv = df_ah.assign(is_mv=df_ah["ah03d"] == 1).groupby("folio")["is_mv"].any()
    s_crafts = df_inr.assign(is_craft=df_inr["inr02f"] == 1).groupby("folio")["is_craft"].any()

    df_comb = pd.concat([s_mv, s_crafts], axis=1).fillna(False)

    df_filtered = df_comb[(df_comb["is_mv"]) & (df_comb["is_craft"])]
    df_filtered = df_filtered[df_filtered.index.isin(oax_folios)]

    return pd.DataFrame({"households_count": [int(len(df_filtered))]})