import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Households with at least one member aged 65+
    elderly_households = (
        df_portad.loc[df_portad["edad"].ge(65, fill_value=False), "folio"]
        .dropna()
        .unique()
    )

    # Aggregate ii_in at household level
    df_in_grouped = (
        df_in.groupby("folio", as_index=False)
        .agg(
            participated_received=(
                "in01a11_1",
                lambda s: bool((s == 1.0).any()),
            ),
            in02a11=(
                "in02a11",
                lambda s: s.dropna().sum(),
            ),
            licon_yes=(
                "in03a",
                lambda s: bool((s == 1.0).any()),
            ),
        )
    )

    # Universe: elderly HHs that participated and received positive direct payment
    universe = df_in_grouped[
        (df_in_grouped["participated_received"])
        & (df_in_grouped["in02a11"] > 0)
        & (df_in_grouped["folio"].isin(elderly_households))
    ].copy()

    # Average among those that also received Liconsa milk
    avg_liconsa = universe.loc[universe["licon_yes"], "in02a11"].mean()

    if pd.isna(avg_liconsa):
        return pd.DataFrame({"folio": pd.Series(dtype="object"), "in02a11": pd.Series(dtype="float64")})

    result = (
        universe.loc[universe["in02a11"] > avg_liconsa, ["folio", "in02a11"]]
        .sort_values(by="in02a11", ascending=False)
        .reset_index(drop=True)
    )

    return result