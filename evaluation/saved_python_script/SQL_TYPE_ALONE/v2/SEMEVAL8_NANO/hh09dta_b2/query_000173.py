def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    ah = tables["ii_ah"]
    
    # Filter households with reported death in last five years (se01a == 1)
    death_mask = se["se01a"] == 1
    se_death = se[death_mask]
    
    # Merge with portad to get 'ent' (state) and 'folio' (household ID)
    merged = pd.merge(se_death[["folio"]], portad[["folio", "ent"]], on="folio", how="left")
    
    # Merge with 'ah' to get ownership of domestic appliance ('ah03f') and 'folio'
    ah_filtered = ah[["folio", "ah03f"]]
    merged = pd.merge(merged, ah_filtered, on="folio", how="left")
    
    # Merge with portad to get age ('edad') for each individual
    portad_age = portad[["folio", "edad"]]
    merged = pd.merge(merged, portad_age, on="folio", how="left")
    
    # For each household, determine if it has at least one adult (edad >= 18)
    # First, get all individuals' ages per household
    portad_full = portad[["folio", "edad"]]
    # Merge to get ages for all individuals in households with death report
    household_ages = pd.merge(merged[["folio"]], portad_full, on="folio", how="left")
    
    # Group by household to check for presence of at least one adult
    household_group = household_ages.groupby("folio").agg(
        has_adult=pd.NamedAgg(column="edad", aggfunc=lambda x: (x >= 18).any()),
        owns_domestic=pd.NamedAgg(column="ah03f", aggfunc=lambda x: (x == 1).any())
    ).reset_index()
    
    # Merge with portad to get 'ent' (state) for each household
    household_states = pd.merge(household_group, portad[["folio", "ent"]], on="folio", how="left")
    
    # Filter households that reported death and have at least one adult and own a domestic appliance
    filtered = household_states[
        (household_states["has_adult"] == True) &
        (household_states["owns_domestic"] == True)
    ]
    
    # Count per state
    result = filtered.groupby("ent").size().reset_index(name="count_with_conditions")
    
    # Total households with death report per state
    total = household_states.groupby("ent").size().reset_index(name="total_households")
    
    # Merge counts
    final = pd.merge(total, result, on="ent", how="left")
    final["count_with_conditions"] = final["count_with_conditions"].fillna(0).astype(int)
    
    # Map 'ent' codes to state names for clarity (optional, based on metadata)
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
    final["state"] = final["ent"].map(state_map)
    final = final[["state", "count_with_conditions", "total_households"]]
    return final