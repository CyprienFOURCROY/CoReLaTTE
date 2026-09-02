import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()
    df_ah = tables["ii_ah"].copy()

    # Household-level flag for producing/selling fattening animals
    inr_agg = (
        df_inr[["folio", "inr02j"]]
        .groupby("folio", as_index=False)
        .min()
    )

    # Household-level bull/cow asset value
    ah_agg = (
        df_ah[["folio", "ah04j_2"]]
        .groupby("folio", as_index=False)
        .max()
    )

    # Merge and filter households that produce/sell fattening animals
    hh = inr_agg.merge(ah_agg, on="folio", how="inner")
    mask_produce = hh["inr02j"] == 1.0

    # Average bull/cow value among producing/selling households
    avg_bull_value = hh.loc[mask_produce & hh["ah04j_2"].notna(), "ah04j_2"].mean()

    # Households with bull/cow value greater than the average
    selected_folios = hh.loc[mask_produce & (hh["ah04j_2"] > avg_bull_value), "folio"].unique()

    # Adults (18+) per household
    adult_counts = (
        df_portad.assign(is_adult=df_portad["edad"] >= 18)
        .groupby("folio")["is_adult"]
        .sum()
    )

    # Average number of adults among selected households
    avg_adults = adult_counts.reindex(selected_folios).dropna().mean()

    return pd.DataFrame({"average_adults": [avg_adults]})