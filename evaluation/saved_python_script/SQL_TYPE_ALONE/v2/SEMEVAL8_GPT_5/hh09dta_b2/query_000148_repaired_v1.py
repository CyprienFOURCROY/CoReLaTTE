import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()

    # Households with at least one member aged 60+
    portad_grp = (
        df_portad.groupby("folio")
        .agg(
            has60plus=("edad", lambda s: (s >= 60).any()),
            ent=("ent", "first"),
        )
        .reset_index()
    )
    portad_grp["ent"] = portad_grp["ent"].astype("Int64")

    # Households where respondent feels unsafe or very unsafe at home
    unsafe_hh = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]].drop_duplicates()

    # Debts + interests value in pesos
    crh_valid = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())]
    debt_by_folio = (
        crh_valid.groupby("folio", as_index=False)["crh04_2"]
        .first()
        .rename(columns={"crh04_2": "total_debt"})
    )

    # Merge conditions
    cond_df = (
        portad_grp[portad_grp["has60plus"]]
        .merge(unsafe_hh, on="folio", how="inner")
        .merge(debt_by_folio, on="folio", how="inner")
    )

    if cond_df.empty:
        return pd.DataFrame({"state": [], "average_total_debt": []})

    overall_avg = cond_df["total_debt"].mean()

    state_avg = (
        cond_df.groupby("ent", as_index=False)["total_debt"]
        .mean()
        .rename(columns={"total_debt": "average_total_debt"})
    )

    state_avg_filt = state_avg[state_avg["average_total_debt"] >= overall_avg]
    if state_avg_filt.empty:
        return pd.DataFrame({"state": [], "average_total_debt": []})

    max_avg = state_avg_filt["average_total_debt"].max()
    top_states = state_avg_filt[state_avg_filt["average_total_debt"] == max_avg].copy()

    ent_map = {
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

    ent_int = top_states["ent"].astype("Int64")
    top_states["state"] = ent_int.map(ent_map)
    mask_na = top_states["state"].isna()
    if mask_na.any():
        top_states.loc[mask_na, "state"] = ent_int[mask_na].astype(str)

    result = top_states[["state", "average_total_debt"]].sort_values(
        by=["average_total_debt", "state"], ascending=[False, True]
    ).reset_index(drop=True)

    return result