import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_su = tables["ii_su"].copy()

    # Household-level state and adult presence
    df_portad["is_adult"] = df_portad["edad"] >= 18
    hh_state_adult = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), has_adult=("is_adult", "max"))
    )

    # Household-level motor vehicle ownership (any member with ah03d == 1)
    df_ah["has_motor_member"] = df_ah["ah03d"] == 1.0
    hh_motor = (
        df_ah.groupby("folio", as_index=False)["has_motor_member"]
        .max()
        .rename(columns={"has_motor_member": "has_motor"})
    )

    # Household-level land use and fuel expenses (deduplicate by folio just in case)
    hh_su = (
        df_su.groupby("folio", as_index=False)
        .agg(su01=("su01", "first"), su239=("su239", "first"))
    )

    # Merge all household-level info
    hh = (
        hh_su.merge(hh_state_adult, on="folio", how="left")
        .merge(hh_motor, on="folio", how="left")
    )
    hh["has_adult"] = hh["has_adult"].fillna(False)
    hh["has_motor"] = hh["has_motor"].fillna(False)

    # Filter to Oaxaca (20) or Puebla (21) and land-using households
    in_states = hh["ent"].isin([20.0, 21.0])
    land_using = hh["su01"] == 1.0
    land_using_states = hh[in_states & land_using]

    # Compute overall average su239 among land-using households in those states
    avg_su239 = land_using_states["su239"].mean()

    # Apply additional conditions and compare to average
    qualified = land_using_states[
        (land_using_states["has_adult"])
        & (land_using_states["has_motor"])
        & (land_using_states["su239"].notna())
        & (land_using_states["su239"] > avg_su239)
    ]

    count = int(qualified.shape[0])

    return pd.DataFrame({"households_count": [count]})