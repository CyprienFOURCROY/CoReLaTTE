import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh02_2"]].copy()

    # Merge necessary tables
    df = df_portad.merge(df_nna, on="folio", how="inner").merge(df_vlh, on="folio", how="inner")

    # Apply filters:
    # - adult in household (edad >= 18)
    # - has member who owns/shares non-ag business (nna01 == 1)
    # - answered "Feel safe at home" (vlh04 in {1,2,3,4})
    df = df[
        (df["edad"] >= 18)
        & (df["nna01"] == 1)
        & (df["vlh04"].isin([1.0, 2.0, 3.0, 4.0]))
    ].copy()

    # Indicator for living in home since 2005 or later
    df["post2005"] = ((df["vlh02_2"].notna()) & (df["vlh02_2"] >= 2005)).astype(int)

    # Group by state (ent)
    grouped = df.groupby("ent", as_index=False).agg(
        total_households=("folio", "nunique"),
        post2005_or_later=("post2005", "sum"),
    )

    # Qualifying states: at least 30 such households
    qualifying = grouped[grouped["total_households"] >= 30].copy()

    # If no qualifying states, return empty result with expected columns
    if qualifying.empty:
        return pd.DataFrame(columns=["state", "state_code", "total_households", "post2005_or_later"])

    # Average of post-2005 counts across qualifying states
    avg_post2005 = qualifying["post2005_or_later"].mean()

    # Keep only states with post-2005 count >= average
    qualifying = qualifying[qualifying["post2005_or_later"] >= avg_post2005].copy()

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
    qualifying["state_code"] = qualifying["ent"].astype("Int64")
    qualifying["state"] = qualifying["state_code"].map(state_map).fillna(qualifying["state_code"].astype(str))

    # Order by post-2005 count descending, then by state name ascending for tie-break
    qualifying = qualifying.sort_values(by=["post2005_or_later", "state"], ascending=[False, True])

    # Select and return final columns
    return qualifying[["state", "state_code", "total_households", "post2005_or_later"]].reset_index(drop=True)