import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_ah = tables["ii_ah"].copy()

    # Household-level state (ent) per folio
    ent_by_folio = (
        df_portad.loc[:, ["folio", "ent"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"], keep="first")
    )

    # Received positive amount from Other Government Program in last 12 months
    df_in_aux = df_in.loc[:, ["folio", "in01a10_2", "in02a10"]].copy()
    cond_received = (df_in_aux["in01a10_2"].fillna(0) > 0) | (df_in_aux["in02a10"].fillna(0) > 0)
    df_received = df_in_aux.loc[cond_received, ["folio"]].dropna(subset=["folio"]).drop_duplicates()

    # Feel unsafe or very unsafe at home
    df_vlh_unsafe = df_vlh.loc[df_vlh["vlh04"].isin([3.0, 4.0]), ["folio"]].dropna(subset=["folio"]).drop_duplicates()

    # Own a motor vehicle (any HH member reports yes)
    df_ah_mv = df_ah.loc[:, ["folio", "ah03d"]].copy()
    df_ah_mv["has_mv"] = df_ah_mv["ah03d"] == 1.0
    df_mv = (
        df_ah_mv.groupby("folio", as_index=False)["has_mv"]
        .max()
        .loc[lambda d: d["has_mv"], ["folio"]]
    )

    # Eligible households: intersection of the three conditions
    df_eligible = (
        df_received.merge(df_vlh_unsafe, on="folio", how="inner")
        .merge(df_mv, on="folio", how="inner")
        .merge(ent_by_folio, on="folio", how="left")
    )

    # Count eligible households by state (ent)
    counts = df_eligible.groupby("ent", dropna=False)["folio"].nunique().reset_index(name="num_households")

    # Include states with zero counts for averaging
    all_states = ent_by_folio[["ent"]].drop_duplicates()
    counts_all = all_states.merge(counts, on="ent", how="left")
    counts_all["num_households"] = counts_all["num_households"].fillna(0).astype(int)

    mean_count = counts_all["num_households"].mean()

    above = counts_all.loc[counts_all["num_households"] > mean_count].copy()

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
        32: "Zacatecas",
    }

    above["ent_int"] = above["ent"].astype("Int64")
    above["state"] = above["ent_int"].map(state_map)
    above["state"] = above["state"].fillna(above["ent_int"].astype(str))

    result = above.loc[:, ["state", "num_households"]].sort_values(
        by=["num_households", "state"], ascending=[False, True]
    ).reset_index(drop=True)

    return result