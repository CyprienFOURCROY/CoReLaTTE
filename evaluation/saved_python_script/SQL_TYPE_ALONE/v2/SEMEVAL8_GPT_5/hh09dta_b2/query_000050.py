import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_se = tables["ii_se"].copy()

    # Adults per household
    df_portad["adult"] = (df_portad["edad"] >= 18)
    adult_count = (
        df_portad.groupby("folio", as_index=False)["adult"]
        .sum()
        .rename(columns={"adult": "adult_count"})
    )

    # State per household
    ent_per_hh = df_portad.groupby("folio", as_index=False)["ent"].first()

    # Household-level program variables
    in_agg = df_in.groupby("folio", as_index=False).agg(
        {"in03a": "min", "in02a10": "max"}
    )

    # Household-level shocks
    se_agg = df_se.groupby("folio", as_index=False).agg({"se01b": "min"})

    # Merge all household-level info
    hh = (
        adult_count.merge(ent_per_hh, on="folio", how="left")
        .merge(in_agg, on="folio", how="left")
        .merge(se_agg, on="folio", how="left")
    )

    # Average adults among households that received Liconsa milk (in03a == 1)
    avg_adults_liconsa = hh.loc[hh["in03a"] == 1, "adult_count"].mean()

    # Filters:
    # - positive amount from Other Gov Program
    # - experienced illness/accident/hospitalization in last 5 years (se01b == 1)
    # - more adults than average among Liconsa households
    cond = (hh["ent"].notna()) & (hh["in02a10"] > 0) & (hh["se01b"] == 1)
    if pd.notna(avg_adults_liconsa):
        cond = cond & (hh["adult_count"] > avg_adults_liconsa)
    else:
        cond = cond & False  # no baseline means no households meet the adult-count condition

    filtered = hh.loc[cond, ["ent", "in02a10"]]

    result = (
        filtered.groupby("ent", as_index=False)["in02a10"]
        .mean()
        .rename(columns={"in02a10": "average_in02a10"})
        .sort_values("average_in02a10", ascending=False)
        .reset_index(drop=True)
    )

    # Cast state code to integer where possible
    result["ent"] = result["ent"].astype("Int64")

    return result