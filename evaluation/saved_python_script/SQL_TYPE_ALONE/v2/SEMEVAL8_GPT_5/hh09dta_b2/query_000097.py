import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    ent_by_folio = df_portad.groupby("folio", as_index=False)["ent"].max()

    df_ah = tables["ii_ah"][["folio", "ah03d"]].copy()
    has_vehicle = df_ah.groupby("folio")["ah03d"].apply(lambda s: (s == 1.0).any()).reset_index(name="has_vehicle")

    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    vlh_by_folio = df_vlh.groupby("folio", as_index=False)["vlh04"].mean()

    df = ent_by_folio.merge(has_vehicle, on="folio", how="left").merge(vlh_by_folio, on="folio", how="left")
    df["has_vehicle"] = df["has_vehicle"].fillna(False)

    mask_outside = (df["has_vehicle"]) & (df["ent"] != 20) & (~df["vlh04"].isna())
    outside_avg = df.loc[mask_outside, "vlh04"].mean()

    mask_inside = (df["ent"] == 20) & (df["has_vehicle"]) & (~df["vlh04"].isna()) & (df["vlh04"] > outside_avg)
    result = df.loc[mask_inside, ["folio", "vlh04"]].copy()

    result = result.sort_values(by="vlh04", ascending=False).reset_index(drop=True)
    return result