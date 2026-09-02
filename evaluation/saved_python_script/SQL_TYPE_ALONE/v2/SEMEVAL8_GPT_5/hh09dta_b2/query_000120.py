import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()
    df_ah = tables["ii_ah"].copy()

    # Households in Oaxaca (ent == 20)
    oax_folios = (
        df_portad.loc[df_portad["ent"] == 20.0, ["folio"]]
        .dropna()
        .drop_duplicates()
    )

    # Households with reported amounts for both money owed and total debts + interest
    crh_filtered = df_crh.loc[
        df_crh["crh02_2"].notna() & df_crh["crh04_2"].notna(),
        ["folio", "crh04_2"]
    ].dropna(subset=["folio"]).drop_duplicates(subset=["folio"])

    # Restrict to Oaxaca
    crh_oax = oax_folios.merge(crh_filtered, on="folio", how="inner")

    # Motor vehicle ownership from assets table
    ah_vehicle = (
        df_ah.loc[df_ah["ah03d"].isin([1.0, 3.0]), ["folio", "ah03d"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"])
        .assign(owns_motor_vehicle=lambda d: d["ah03d"] == 1.0)
        [["folio", "owns_motor_vehicle"]]
    )

    # Merge to classify households by vehicle ownership
    df = crh_oax.merge(ah_vehicle, on="folio", how="inner")

    # Group and aggregate
    result = (
        df.groupby("owns_motor_vehicle", as_index=False)
        .agg(
            n_households=("folio", "nunique"),
            avg_total_debts_plus_interest_pesos=("crh04_2", "mean"),
        )
    )

    return result