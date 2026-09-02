def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    in_df = tables["ii_in"]
    ah = tables["ii_ah"]
    vlh = tables["ii_vlh"]
    ah_enriched = tables["ii_ah_enriched"]
    vlh_enriched = tables["ii_vlh_enriched"]
    # Filter households that received Liconsa Milk in last 12 months and feel very safe or safe at home
    # Conditions:
    # in03a == 1 (Yes to Liconsa Milk)
    # vlh04 in [1, 2] (Very safe or Safe)
    mask_in = in_df["in03a"] == 1
    mask_vlh = vlh["vlh04"].isin([1, 2])
    households_mask = mask_in & mask_vlh
    households = in_df.loc[households_mask, "folio"].unique()

    # Filter portad for these households
    portad_filtered = portad[portad["folio"].isin(households)]

    # Merge portad with ah_enriched on folio
    portad_ah = portad_filtered.merge(ah_enriched, on=["folio", "ls"], how="left")

    # Merge with vlh_enriched on folio
    portad_vlh = portad_ah.merge(vlh_enriched, on=["folio", "ls"], how="left")

    # Filter for feeling very safe or safe at home
    # Already filtered above, but ensure vlh04 in [1,2]
    # Now, focus on electronic devices
    # Columns for electronic devices:
    # From ii_ah_enriched: ah04e_1, ah04e_2
    # We want the total value of electronic devices per household:
    # Sum of ah04e_2 (value in pesos), ignoring NaNs
    # First, group by folio to get per-household sums
    household_elec = (
        portad_vlh.groupby("folio")
        .agg({"ah04e_2": "sum"})
        .rename(columns={"ah04e_2": "total_electronic_value"})
        .reset_index()
    )

    # Calculate overall average of total electronic device value
    overall_avg = household_elec["total_electronic_value"].mean()

    # Merge back with household info to get state
    household_info = portad_vlh[["folio", "ent"]].drop_duplicates()
    household_elec = household_elec.merge(household_info, on="folio", how="left")

    # Filter households with total electronic value above overall average
    above_avg = household_elec[household_elec["total_electronic_value"] > overall_avg]

    # Map ent (state code) to state name
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

    # Add state name
    above_avg["state"] = above_avg["ent"].map(state_map)

    # Count and rank states from highest to lowest total electronic device value
    result = (
        above_avg.groupby("state")
        .agg({"total_electronic_value": "mean"})
        .sort_values(by="total_electronic_value", ascending=False)
        .reset_index()
    )

    # Rename columns for clarity
    result = result.rename(columns={"total_electronic_value": "avg_electronic_value"})

    return result