import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Household state (one ent per household)
    house_state = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"], keep="first")
    )

    # Households with at least one adult (18+)
    adult_folios = (
        df_portad[df_portad["edad"].ge(18.0)][["folio"]]
        .dropna()
        .drop_duplicates()
    )
    adult_folios["adult_flag"] = True

    # Households with at least one member who owns an electronic device
    df_device = df_ah[["folio", "ah03e"]].copy()
    df_device["has_device"] = df_device["ah03e"] == 1.0
    df_device = df_device.groupby("folio", as_index=False)["has_device"].any()
    df_device = df_device[df_device["has_device"]]

    # Households that report feeling very safe or safe at home
    df_safe = (
        df_vlh[df_vlh["vlh04"].isin([1.0, 2.0])][["folio"]]
        .dropna()
        .drop_duplicates()
    )

    # Eligible households meeting all three criteria
    eligible = (
        adult_folios.merge(df_device[["folio"]], on="folio", how="inner")
        .merge(df_safe[["folio"]], on="folio", how="inner")
        .merge(house_state[["folio", "ent"]], on="folio", how="left")
        .dropna(subset=["ent"])
    )

    # Count eligible households by state (ent)
    counts = eligible.groupby("ent").size().reset_index(name="num_households")
    counts["ent"] = counts["ent"].astype("Int64")

    # Include all states present in the dataset (with zero counts where applicable)
    ent_unique = house_state[["ent"]].dropna().drop_duplicates()
    ent_unique["ent"] = ent_unique["ent"].astype("Int64")
    counts_full = ent_unique.merge(counts, on="ent", how="left")
    counts_full["num_households"] = counts_full["num_households"].fillna(0).astype("int64")

    # Compute average and filter states above average
    avg = counts_full["num_households"].mean()
    above = counts_full[counts_full["num_households"] > avg].copy()

    # Map ent codes to state names
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
        32: "Zacatecas",
    }

    above["state"] = above["ent"].map(state_map).fillna(above["ent"].astype(str))
    result = above.sort_values(["num_households", "state"], ascending=[False, True])[
        ["state", "num_households"]
    ].reset_index(drop=True)

    return result