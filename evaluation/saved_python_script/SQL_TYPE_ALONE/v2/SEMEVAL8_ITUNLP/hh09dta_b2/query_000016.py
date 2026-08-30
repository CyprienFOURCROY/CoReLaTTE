import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_in = tables["ii_in"].copy()

    # Households with positive amount received from "Other Government Program"
    df_in_pos = df_in.loc[(df_in["in02a10"].notna()) & (df_in["in02a10"] > 0), ["folio", "in02a10"]]

    # Households with at least one member who owns an electronic device (ah03e == 1)
    has_device = (
        df_ah.assign(has_device=df_ah["ah03e"] == 1.0)
        .groupby("folio", as_index=False)["has_device"]
        .any()
    )
    hh_eligible = df_in_pos.merge(has_device[has_device["has_device"]], on="folio", how="inner")

    # Map households to state
    folio_ent = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])

    df = hh_eligible.merge(folio_ent, on="folio", how="left")
    df = df[df["ent"].notna()]

    res = (
        df.groupby("ent", as_index=False)
        .agg(avg_in02a10=("in02a10", "mean"), n_households=("folio", "nunique"))
    )

    res = res[(res["n_households"] >= 30) & (res["avg_in02a10"] > 2000)]
    res = res.sort_values("avg_in02a10", ascending=False).reset_index(drop=True)

    # Cast state code to integer-like
    res["ent"] = res["ent"].astype("Int64")

    return res[["ent", "avg_in02a10", "n_households"]]