import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]

    # Household-level state (ent)
    portad_ent = (
        df_portad.loc[~df_portad["ent"].isna(), ["folio", "ent"]]
        .assign(ent=lambda d: d["ent"].astype("int64"))
        .drop_duplicates(subset=["folio"], keep="first")
    )

    # Household-level land use: any member with su01 == 1
    su_land = (
        df_su.assign(land_use=df_su["su01"] == 1)
        .groupby("folio", as_index=False, sort=False)["land_use"]
        .any()
    )
    land_households = su_land.loc[su_land["land_use"]]

    # Household-level honey production: any member with inr02i == 1
    inr_honey = (
        df_inr.assign(honey=df_inr["inr02i"] == 1)
        .groupby("folio", as_index=False, sort=False)["honey"]
        .any()
    )

    # Merge to get state and honey flags for land-using households
    land_with_state = land_households.merge(portad_ent, on="folio", how="left")
    land_with_state = land_with_state.loc[~land_with_state["ent"].isna()].copy()
    land_with_state["ent"] = land_with_state["ent"].astype("int64")
    land_with_state = land_with_state.merge(inr_honey, on="folio", how="left")
    land_with_state["honey"] = land_with_state["honey"].fillna(False)

    # Aggregate by state
    agg = (
        land_with_state.groupby("ent", as_index=False)
        .agg(
            land_households=("folio", "nunique"),
            honey_households=("honey", "sum"),
        )
    )

    # Apply thresholds
    filt = agg[(agg["land_households"] >= 30) & (agg["honey_households"] >= 10)]

    # Map state codes to names
    ent_name_map = {
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        9: "Distrito Federal",
        10: "Durango",
        11: "Guanajuato",
        12: "Guerrero",
        13: "Hidalgo",
        14: "Jalisco",
        15: "Estado de México",
        16: "Michoacán",
        17: "Morelos",
        18: "Nayarit",
        19: "Nuevo León",
        20: "Oaxaca",
        21: "Puebla",
        22: "Querétaro",
        25: "Sinaloa",
        26: "Sonora",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas",
    }
    filt = filt.assign(
        state=filt["ent"].map(ent_name_map).fillna(filt["ent"].astype(str))
    )

    result = (
        filt.sort_values(by=["honey_households", "state"], ascending=[False, True])
        .loc[:, ["state", "honey_households"]]
        .reset_index(drop=True)
    )

    return result