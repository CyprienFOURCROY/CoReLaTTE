import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_crh = tables["ii_crh"].copy()

    # Oaxaca households
    oax_ind = df_portad[df_portad["ent"] == 20.0]
    oax_folio_set = set(oax_ind["folio"].dropna().unique().tolist())

    # Households that own a motor vehicle
    hh_vehicle_folios = set(df_ah.loc[df_ah["ah03d"] == 1.0, "folio"].dropna().unique().tolist())

    # Oaxaca households with reported total debts + interest (crh04_1 == 1 and crh04_2 not null)
    crh_oax = df_crh[df_crh["folio"].isin(oax_folio_set)]
    reported_mask = (crh_oax["crh04_1"] == 1.0) & (crh_oax["crh04_2"].notna())
    crh_oax_reported = crh_oax[reported_mask].copy()

    mean_debt = crh_oax_reported["crh04_2"].mean()

    if pd.isna(mean_debt):
        exceed_set = set()
    else:
        exceed_set = set(crh_oax_reported.loc[crh_oax_reported["crh04_2"] > mean_debt, "folio"].unique().tolist())

    # Target households: Oaxaca, own motor vehicle, and exceed average debts
    target_hh_set = oax_folio_set & hh_vehicle_folios & exceed_set

    # Count adults (18+) in those households
    adults_mask = (
        (df_portad["ent"] == 20.0) &
        (df_portad["edad"].notna()) &
        (df_portad["edad"] >= 18.0) &
        (df_portad["folio"].isin(target_hh_set))
    )
    adults_count = int(adults_mask.sum())

    return pd.DataFrame({"adults_count": [adults_count]})