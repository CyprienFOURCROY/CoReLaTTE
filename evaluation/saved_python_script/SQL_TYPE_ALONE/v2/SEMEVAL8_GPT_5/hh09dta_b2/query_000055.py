import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()
    df_nna = tables["ii_nna"].copy()
    df_ah = tables["ii_ah"].copy()

    # Household-level state and adult presence
    # Adult: any household member with edad >= 18
    hh_adult = (
        df_portad.groupby("folio", as_index=True)["edad"]
        .max(min_count=1)
        .rename("max_edad")
    )
    hh_has_adult = (hh_adult >= 18).rename("has_adult")

    # State per household (take first occurrence)
    hh_ent = (
        df_portad.groupby("folio", as_index=True)["ent"]
        .first()
        .rename("ent")
    )

    hh_info = pd.concat([hh_has_adult, hh_ent], axis=1).reset_index()

    # Filter households with at least one adult
    hh_info = hh_info[hh_info["has_adult"] == True].drop(columns=["has_adult"])

    # Households that own/share a non-ag business
    nna_filt = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()

    # Households that did not incur debts in last 12 months
    crh_filt = df_crh[df_crh["crh02_1"] == 2.0][["folio"]].drop_duplicates()

    # Households that reported a value for washing machine/stove assets
    ah_filt = df_ah[(df_ah["ah04f_1"] == 1.0) & (df_ah["ah04f_2"].notna())][["folio", "ah04f_2"]].drop_duplicates()

    # Merge all conditions
    eligible = (
        hh_info.merge(nna_filt, on="folio", how="inner")
        .merge(crh_filt, on="folio", how="inner")
        .merge(ah_filt, on="folio", how="inner")
    )

    # Drop rows without state info
    eligible = eligible[eligible["ent"].notna()]

    if eligible.empty:
        return pd.DataFrame({"state": pd.Series(dtype=object), "average_value": pd.Series(dtype=float)})

    # National average among eligible households
    national_avg = eligible["ah04f_2"].mean()

    # Average by state
    state_avg = (
        eligible.groupby("ent", as_index=False)["ah04f_2"]
        .mean()
        .rename(columns={"ah04f_2": "average_value"})
    )

    # Keep states above national average
    state_avg = state_avg[state_avg["average_value"] > national_avg]

    if state_avg.empty:
        return pd.DataFrame({"state": pd.Series(dtype=object), "average_value": pd.Series(dtype=float)})

    # Map state codes to names
    ent_to_name = {
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

    # Prepare final DataFrame with state names
    state_avg = state_avg.copy()
    ent_codes = state_avg["ent"].astype("Int64")
    state_avg["state"] = ent_codes.map(ent_to_name).fillna(ent_codes.astype(str))

    # Rank from highest to lowest
    result = state_avg.sort_values(by="average_value", ascending=False)[["state", "average_value"]].reset_index(drop=True)

    return result