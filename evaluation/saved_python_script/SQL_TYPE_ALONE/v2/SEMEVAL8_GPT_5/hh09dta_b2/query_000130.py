import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_vlh = tables["ii_vlh"]

    # Adults per household
    df_portad = df_portad.copy()
    df_portad["is_adult"] = df_portad["edad"] >= 18
    adults_per_hh = df_portad.groupby("folio", as_index=False)["is_adult"].sum()
    adults_per_hh.rename(columns={"is_adult": "adult_count"}, inplace=True)
    avg_adults = adults_per_hh["adult_count"].mean()
    more_than_avg_adults = adults_per_hh[adults_per_hh["adult_count"] > avg_adults][["folio"]]

    # Household feels unsafe/very unsafe and has lived there since 2005 or earlier
    vlh_agg = df_vlh.groupby("folio").agg(
        unsafe=("vlh04", lambda s: ((s == 3) | (s == 4)).any()),
        year=("vlh02_2", "min"),
    ).reset_index()
    vlh_filtered = vlh_agg[(vlh_agg["unsafe"]) & (vlh_agg["year"].notna()) & (vlh_agg["year"] <= 2005)][["folio"]]

    # Eligible households
    eligible = pd.merge(more_than_avg_adults, vlh_filtered, on="folio", how="inner").drop_duplicates()
    total_households = eligible["folio"].nunique()

    # Produced or sold canned goods in last 12 months
    inr_agg = df_inr.groupby("folio").agg(
        produced_canned=("inr02b", lambda s: (s == 1).any())
    ).reset_index()
    eligible_inr = eligible.merge(inr_agg, on="folio", how="left")
    produced_canned_goods = int(eligible_inr["produced_canned"].fillna(False).sum())

    return pd.DataFrame(
        {
            "total_households": [int(total_households)],
            "produced_canned_goods": [produced_canned_goods],
        }
    )