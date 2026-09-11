import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()
    df_se = tables["ii_se"].copy()

    # Households with at least one adult (18+), and state per household
    df_portad["is_adult"] = df_portad["edad"] >= 18
    hh_adult = (
        df_portad.groupby("folio")
        .agg(ent=("ent", "first"), has_adult=("is_adult", "any"))
        .reset_index()
    )
    hh_adult = hh_adult[hh_adult["has_adult"]].copy()

    # Households that produced/sold meat
    hh_meat = df_inr[df_inr["inr02c"] == 1.0][["folio"]].drop_duplicates()

    # Households with disease/accident/hospitalization in last 5 years
    hh_disease = df_se[df_se["se01b"] == 1.0][["folio"]].drop_duplicates()

    # Eligible households: adult + meat + disease
    eligible = (
        hh_adult.merge(hh_meat, on="folio", how="inner")
        .merge(hh_disease, on="folio", how="inner")
    )

    # Counts per state
    if not eligible.empty:
        eligible["ent"] = eligible["ent"].astype("Int64")
        counts = (
            eligible.groupby("ent", dropna=False)
            .agg(household_count=("folio", "nunique"))
            .reset_index()
        )
    else:
        counts = pd.DataFrame(columns=["ent", "household_count"])

    # Ensure all states present in dataset are considered (zeros included)
    all_states = (
        df_portad["ent"].dropna().astype("Int64").drop_duplicates().sort_values()
    )
    counts_full = pd.DataFrame({"ent": all_states})
    counts_full = counts_full.merge(counts, on="ent", how="left")
    counts_full["household_count"] = counts_full["household_count"].fillna(0).astype("Int64")

    # Average across all states
    avg_count = counts_full["household_count"].mean()

    # States with count >= average
    result = counts_full[counts_full["household_count"] >= avg_count].copy()
    result = result.sort_values(["household_count", "ent"], ascending=[False, True]).reset_index(drop=True)

    return result