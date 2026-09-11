def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # 1. Households that received a positive amount from 'Other Government Program' in the last 12 months
    # in01a10_1 == 1 (participates and received income) and in01a10_2 > 0
    df_in_pos = df_in[
        (df_in["in01a10_1"] == 1.0) &
        (df_in["in01a10_2"].notna()) &
        (df_in["in01a10_2"] > 0)
    ][["folio"]].drop_duplicates()

    # 2. Households that report feeling unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[
        df_vlh["vlh04"].isin([3.0, 4.0])
    ][["folio"]].drop_duplicates()

    # 3. Households that own a motor vehicle (ah03d == 1)
    # Need to aggregate at household level: at least one member owns a motor vehicle
    df_ah_vehicle = df_ah[
        df_ah["ah03d"] == 1.0
    ][["folio"]].drop_duplicates()

    # 4. Merge all three conditions on folio (household)
    df_merge = df_in_pos.merge(df_vlh_unsafe, on="folio") \
                        .merge(df_ah_vehicle, on="folio")

    # 5. Get state for each household from ii_portad (ent)
    # Each folio may appear multiple times in ii_portad, but ent is the same for all members
    df_folio_ent = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])
    df_merge = df_merge.merge(df_folio_ent, on="folio", how="left")

    # 6. Count number of such households per state
    state_counts = df_merge.groupby("ent")["folio"].nunique().reset_index()
    state_counts = state_counts.rename(columns={"folio": "num_households"})

    # 7. Compute average number of such households per state
    avg_households = state_counts["num_households"].mean()

    # 8. Filter states with above-average number of such households
    result = state_counts[state_counts["num_households"] > avg_households].copy()

    # 9. Map state codes to names
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
    result = result[["state", "num_households"]].sort_values("num_households", ascending=False).reset_index(drop=True)
    return result