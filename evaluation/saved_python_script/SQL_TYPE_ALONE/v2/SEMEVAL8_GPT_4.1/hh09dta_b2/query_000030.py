def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # Households that use land for farming: su01 == 1
    su_land = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Households with at least one robbery (house, business, or parcel) since 2005
    # vlh13a: Number of times robbed in HH since 2005
    # vlh15a: Number times rob/force business since 2005
    # vlh17a: Number of times entered/rob parcel since 2005
    df_vlh_rob = df_vlh.copy()
    rob_cols = ["vlh13a", "vlh15a", "vlh17a"]
    df_vlh_rob["robbery_since_2005"] = (
        (df_vlh_rob[rob_cols].fillna(0).astype(float).sum(axis=1)) > 0
    )
    rob_folios = df_vlh_rob[df_vlh_rob["robbery_since_2005"]][["folio"]].drop_duplicates()

    # Households with value of electronic devices (ah04e_2) above overall mean
    # Only consider rows where ah04e_2 is not null
    df_ah_elec = df_ah[~df_ah["ah04e_2"].isnull()]
    overall_mean = df_ah_elec["ah04e_2"].mean()
    df_ah_elec = df_ah_elec[df_ah_elec["ah04e_2"] > overall_mean]

    # Merge all filters: by folio
    # Only one row per household (folio) for electronics value, take the first if duplicates
    df_ah_elec = df_ah_elec.sort_values("ah04e_2", ascending=False).drop_duplicates("folio")
    eligible_folios = set(su_land["folio"]) & set(rob_folios["folio"]) & set(df_ah_elec["folio"])

    # Get state and electronics value for eligible households
    df_eligible = df_ah_elec[df_ah_elec["folio"].isin(eligible_folios)][["folio", "ah04e_2"]]
    df_eligible = df_eligible.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Group by state, calculate average electronics value and count
    result = (
        df_eligible.groupby("ent")
        .agg(avg_electronics_value=("ah04e_2", "mean"), num_households=("folio", "count"))
        .reset_index()
    )

    # Rank by average electronics value descending
    result = result.sort_values("avg_electronics_value", ascending=False).reset_index(drop=True)

    # Map state codes to names
    state_map = {
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
        32: "Zacatecas"
    }
    result["state"] = result["ent"].map(state_map)
    result = result[["state", "avg_electronics_value", "num_households"]]

    return result.reset_index(drop=True)