import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    ent_map = {20.0: "Oaxaca", 21.0: "Puebla"}

    df_portad = df_portad[df_portad["ent"].isin(ent_map.keys())]

    df_portad_agg = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), has_25plus=("edad", lambda s: bool((s >= 25).any())))
    )
    df_portad_agg = df_portad_agg[df_portad_agg["has_25plus"]]

    df = df_portad_agg.merge(df_crh, on="folio", how="inner")

    df = df[(df["crh04_1"] == 1.0) & (~df["crh04_2"].isna()) & (df["crh04_2"] >= 5000)]

    df = df.merge(df_vlh, on="folio", how="inner")
    df = df[~df["vlh04"].isna()]

    if df.empty:
        return pd.DataFrame(columns=["state", "avg_feel_safe_at_home", "avg_total_debt", "households"])

    df["state"] = df["ent"].map(ent_map)

    result = (
        df.groupby("state", as_index=False)
        .agg(
            avg_feel_safe_at_home=("vlh04", "mean"),
            avg_total_debt=("crh04_2", "mean"),
            households=("folio", "nunique"),
        )
        .sort_values(by=["avg_feel_safe_at_home", "state"], ascending=[True, True])
        .reset_index(drop=True)
    )

    return result