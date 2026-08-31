import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]

    # Households that use a plot/land for farming
    su_hh = df_su.loc[df_su["su01"] == 1, ["folio"]].dropna().drop_duplicates()

    # Households that own poultry
    ah_hh = df_ah.loc[df_ah["ah03m"] == 1, ["folio"]].dropna().drop_duplicates()

    # Intersection: households satisfying both conditions
    hh_both = su_hh.merge(ah_hh, on="folio", how="inner")

    if hh_both.empty:
        return pd.DataFrame(columns=["state", "n_households", "state_avg_age"])

    # Household mean age and state (ent)
    portad_sub = df_portad[df_portad["folio"].isin(hh_both["folio"])]
    hh_age = (
        portad_sub.groupby("folio", as_index=False)
        .agg(hh_mean_age=("edad", "mean"), ent=("ent", "first"))
        .dropna(subset=["hh_mean_age", "ent"])
    )

    if hh_age.empty:
        return pd.DataFrame(columns=["state", "n_households", "state_avg_age"])

    # Overall average of household mean ages across all such households
    overall_avg = hh_age["hh_mean_age"].mean()

    # State-level stats
    state_stats = (
        hh_age.groupby("ent", as_index=False)
        .agg(n_households=("folio", "nunique"), state_avg_age=("hh_mean_age", "mean"))
    )

    # Filter states with at least 25 households and avg above overall average
    result = state_stats[
        (state_stats["n_households"] >= 25) & (state_stats["state_avg_age"] > overall_avg)
    ].copy()

    if result.empty:
        return pd.DataFrame(columns=["state", "n_households", "state_avg_age"])

    # Prepare final output
    result = result.sort_values("state_avg_age", ascending=False)
    result = result.rename(columns={"ent": "state"})
    # Cast state to integer if possible
    try:
        result["state"] = result["state"].astype("Int64")
    except Exception:
        pass

    return result[["state", "n_households", "state_avg_age"]]