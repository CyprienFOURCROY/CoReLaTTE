import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_vlh = tables["ii_vlh"]

    # Households that did not produce/sell any listed goods in the last 12 months (all No=3 across inr02a-k)
    inr_cols = ["inr02a", "inr02b", "inr02c", "inr02d", "inr02e", "inr02f", "inr02g", "inr02h", "inr02i", "inr02j", "inr02k"]
    df_inr_nogoods = df_inr.loc[(df_inr[inr_cols] == 3).all(axis=1), ["folio"]].drop_duplicates()

    # Households where respondent knows a family/friend robbed in last five years (vlh08a == 1)
    df_vlh_know_robbed = df_vlh.loc[df_vlh["vlh08a"] == 1, ["folio", "vlh04"]].drop_duplicates(subset=["folio"])

    # Merge eligible households
    df_elig = pd.merge(df_inr_nogoods, df_vlh_know_robbed, on="folio", how="inner")

    # Map households to state (ent)
    folio_ent = df_portad[["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates(subset=["folio"])
    df_elig = pd.merge(df_elig, folio_ent, on="folio", how="inner")

    if df_elig.empty:
        return pd.DataFrame(columns=["ent", "total_eligible", "unsafe_count"])

    # Compute unsafe indicator (vlh04 in {3,4})
    df_elig["unsafe"] = df_elig["vlh04"].isin([3.0, 4.0])

    # Aggregate by state
    agg = df_elig.groupby("ent").agg(
        total_eligible=("folio", "nunique"),
        unsafe_count=("unsafe", "sum"),
    ).reset_index()

    # Filter states with at least 30 eligible households
    agg_30 = agg.loc[agg["total_eligible"] >= 30].copy()
    if agg_30.empty:
        return pd.DataFrame(columns=["ent", "total_eligible", "unsafe_count"])

    # Compute average unsafe count across these states
    avg_unsafe = agg_30["unsafe_count"].mean()

    # Select states with above-average number of unsafe households
    result = agg_30.loc[agg_30["unsafe_count"] > avg_unsafe, ["ent", "total_eligible", "unsafe_count"]]

    # Sort by unsafe_count descending
    result = result.sort_values(by=["unsafe_count", "ent"], ascending=[False, True]).reset_index(drop=True)

    return result