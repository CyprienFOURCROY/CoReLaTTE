import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_se = tables["ii_se"].copy()

    # Households that experienced disease/accident/hospitalization in last 5 years
    disease_hhs = pd.DataFrame({
        "folio": df_se.loc[df_se["se01b"] == 1, "folio"].dropna().unique()
    })

    # Reported value of electronic devices per household (use max to consolidate duplicates)
    elec_val_by_hh = (
        df_ah[["folio", "ah04e_2"]]
        .groupby("folio", as_index=False, dropna=False)["ah04e_2"]
        .max()
    )

    # State per household (take first occurrence)
    state_by_hh = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["folio"])
        .groupby("folio", as_index=False)["ent"]
        .first()
    )

    # Merge: keep only households with disease and with a reported electronic value
    hh = (
        disease_hhs
        .merge(elec_val_by_hh, on="folio", how="left")
        .merge(state_by_hh, on="folio", how="left")
    )
    hh = hh[hh["ah04e_2"].notna() & hh["ent"].notna()]

    # Aggregate by state
    summary = (
        hh.groupby("ent", as_index=False)
        .agg(
            avg_electronic_value=("ah04e_2", "mean"),
            households=("folio", "nunique"),
        )
    )

    # Keep only states with at least two such households
    summary = summary[summary["households"] >= 2]

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
    summary["state_code"] = summary["ent"].astype(int)
    summary["state"] = summary["state_code"].map(state_map)

    # Top 10 states by highest average value
    summary = summary.sort_values(
        by=["avg_electronic_value", "state_code"], ascending=[False, True]
    ).head(10)

    return summary[["state_code", "state", "avg_electronic_value", "households"]].reset_index(drop=True)