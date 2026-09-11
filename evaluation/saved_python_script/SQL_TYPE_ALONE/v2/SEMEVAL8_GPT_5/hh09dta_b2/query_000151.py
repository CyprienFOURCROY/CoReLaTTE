import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_vlh = tables["ii_vlh"][["folio", "vlh18a"]].copy()
    # Qualifying households: at least one incident since 2005
    df_vlh = df_vlh[df_vlh["vlh18a"].notna() & (df_vlh["vlh18a"] > 0)]
    if df_vlh.empty:
        return pd.DataFrame({"ent": [], "average_incidents_since_2005": [], "num_households": []})
    # Household -> state
    df_ent = tables["ii_portad"][["folio", "ent"]].copy()
    df_ent = df_ent.dropna(subset=["ent"]).drop_duplicates(subset=["folio"])
    # Merge to attach state
    df = df_vlh.merge(df_ent, on="folio", how="inner")
    if df.empty:
        return pd.DataFrame({"ent": [], "average_incidents_since_2005": [], "num_households": []})
    # National average among all qualifying households
    national_avg = df["vlh18a"].mean()
    # State-level stats
    state_stats = (
        df.groupby("ent")
        .agg(
            average_incidents_since_2005=("vlh18a", "mean"),
            num_households=("folio", "nunique"),
        )
        .reset_index()
    )
    # Filter: at least 30 qualifying households and above national average
    result = state_stats[
        (state_stats["num_households"] >= 30)
        & (state_stats["average_incidents_since_2005"] > national_avg)
    ].sort_values("average_incidents_since_2005", ascending=False).reset_index(drop=True)
    return result