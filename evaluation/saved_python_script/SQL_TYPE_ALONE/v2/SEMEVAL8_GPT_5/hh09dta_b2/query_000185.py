import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()

    # Household-level aggregates from roster
    hh_agg = (
        df_portad.groupby("folio")
        .agg(
            oldest_age=("edad", "max"),
            has_adult=("edad", lambda s: (s >= 18).any()),
            in_oaxaca=("ent", lambda s: (s == 20.0).any()),
        )
        .reset_index()
    )

    # Households that reported producing/selling eggs in last 12 months
    eggs_flag = (
        df_inr.assign(eggs_flag=df_inr["inr02d"] == 1.0)
        .groupby("folio")["eggs_flag"]
        .any()
        .reset_index()
    )

    # Filter households: in Oaxaca, with eggs activity, and at least one adult
    eligible_hh = (
        hh_agg.merge(eggs_flag, on="folio", how="inner")
        .loc[lambda d: d["in_oaxaca"] & d["has_adult"] & d["eggs_flag"]]
    )

    average_age = eligible_hh["oldest_age"].mean()

    return pd.DataFrame({"average_age": [average_age]})