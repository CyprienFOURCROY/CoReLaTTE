def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    inr = tables["ii_inr"]
    nna = tables["ii_nna"]
    se = tables["ii_se"]
    
    # Filter households where individual with ls=2 (adult) reported producing/selling dairy products
    # First, find households with ls=2
    adult_households = portad[portad["ls"] == 2][["folio", "ent"]]
    
    # Merge with inr to get dairy production info
    inr_dairy = inr[["folio", "inr02a"]]
    merged = adult_households.merge(inr_dairy, on="folio", how="left")
    
    # Filter households where inr02a == 1 (produced/sold dairy in last 12 months)
    dairy_households = merged[merged["inr02a"] == 1]
    
    # Calculate mean quantity sold of dairy products per household
    inr_qty = inr[["folio", "inr03a"]]
    dairy_qty = inr_qty[inr_qty["folio"].isin(dairy_households["folio"])]
    # Group by folio to get household total
    household_dairy_qty = dairy_qty.groupby("folio")["inr03a"].sum(min_count=1)
    
    # Merge with portad to get state info
    household_state = portad[["folio", "ent"]]
    household_dairy = household_state[household_state["folio"].isin(household_dairy_qty.index)]
    household_dairy = household_dairy.set_index("folio")
    household_dairy["dairy_qty"] = household_dairy_qty
    
    # Drop households with NaN dairy_qty (no data)
    household_dairy = household_dairy.dropna(subset=["dairy_qty"])
    
    # Compute overall mean of household dairy quantities
    overall_mean = household_dairy["dairy_qty"].mean()
    
    # Filter households with above-average dairy quantities
    above_avg = household_dairy[household_dairy["dairy_qty"] > overall_mean]
    
    # Compute mean dairy quantity per state for above-average households
    state_means = (
        above_avg.groupby("ent")["dairy_qty"]
        .mean()
        .reset_index()
        .rename(columns={"ent": "ent", "dairy_qty": "mean_dairy_qty"})
    )
    
    # Filter states with mean above the overall average
    result = state_means[state_means["mean_dairy_qty"] > overall_mean]
    
    # Map state codes to state names
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
    result = result[["state", "mean_dairy_qty"]]
    result = result.rename(columns={"mean_dairy_qty": "average_dairy_quantity"})
    return result