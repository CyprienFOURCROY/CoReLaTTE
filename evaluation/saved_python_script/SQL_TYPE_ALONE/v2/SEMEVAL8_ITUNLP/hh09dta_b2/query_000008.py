import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_ah = tables["ii_ah"]

    # Households with reported total debt (value provided)
    crh = df_crh.loc[(df_crh["crh04_1"] == 1) & (df_crh["crh04_2"].notna()), ["folio", "crh04_2"]].copy()
    overall_avg = crh["crh04_2"].mean()

    # Households that own a motor vehicle (any member says yes)
    ah_mv = (
        df_ah.assign(own_vehicle=df_ah["ah03d"] == 1)
        .groupby("folio", as_index=False)["own_vehicle"]
        .any()
    )
    ah_mv = ah_mv.loc[ah_mv["own_vehicle"]]

    # Map household to state
    folio_ent = (
        df_portad.loc[:, ["folio", "ent"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"])
    )

    # Merge: reported debt + own motor vehicle + state
    df = crh.merge(ah_mv[["folio"]], on="folio", how="inner").merge(folio_ent, on="folio", how="left")

    # Compute state averages and filter by exceeding overall average
    state_avg = (
        df.groupby("ent", as_index=False)["crh04_2"]
        .mean()
        .rename(columns={"crh04_2": "average_total_debt"})
    )
    result = state_avg.loc[state_avg["average_total_debt"] > overall_avg].sort_values(
        by="average_total_debt", ascending=False
    ).head(10).reset_index(drop=True)

    return result