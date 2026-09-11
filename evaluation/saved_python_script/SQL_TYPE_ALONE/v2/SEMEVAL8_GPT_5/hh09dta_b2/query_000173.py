import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]

    # Households that reported a death in the last 5 years (any member indicating yes)
    death_flag = (
        df_se.assign(death=df_se["se01a"] == 1)
        .groupby("folio", as_index=False)["death"]
        .any()
    )
    death_hh = death_flag[death_flag["death"]][["folio"]]

    # State per household (take first occurrence)
    state_map = df_portad.groupby("folio", as_index=False).agg(ent=("ent", "first"))

    # Has at least one adult (age >= 18) in the household
    adult_df = (
        df_portad.assign(is_adult=df_portad["edad"] >= 18)
        .groupby("folio", as_index=False)["is_adult"]
        .any()
        .rename(columns={"is_adult": "has_adult"})
    )

    # Has at least one member who owns a domestic appliance (ah03g == 1)
    domestic_df = (
        df_ah.assign(has_domestic=df_ah["ah03g"] == 1)
        .groupby("folio", as_index=False)["has_domestic"]
        .any()
    )

    # Base: households with reported death and known state
    base = (
        death_hh.merge(state_map, on="folio", how="inner")
        .merge(adult_df, on="folio", how="left")
        .merge(domestic_df, on="folio", how="left")
    )

    base["has_adult"] = base["has_adult"].fillna(False).astype(bool)
    base["has_domestic"] = base["has_domestic"].fillna(False).astype(bool)
    base["both"] = base["has_adult"] & base["has_domestic"]

    result = (
        base.groupby("ent")
        .agg(
            households_with_adult_and_domestic=("both", "sum"),
            total_death_households=("folio", "nunique"),
        )
        .reset_index()
        .sort_values("ent")
    )

    return result