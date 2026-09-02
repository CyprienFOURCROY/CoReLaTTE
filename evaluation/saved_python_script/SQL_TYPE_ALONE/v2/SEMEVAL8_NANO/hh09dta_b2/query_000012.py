def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    
    # Filter households that use a plot/land for farming/vegetables and report positive total debt
    # 1. Households that use land for farming/vegetables: su01 == 1
    su_use_land = su[su["su01"] == 1]
    
    # 2. Merge with crh to get debt info
    merged = pd.merge(su_use_land[["folio"]], crh[["folio", "crh04_1", "crh04_2"]]], on="folio", how="inner")
    
    # 3. Filter households with positive total debt (crh04_1 == 1 and crh04_2 > 0)
    # Note: crh04_1 == 1 indicates total debts + interests, crh04_2 > 0 indicates positive amount
    debt_positive = merged[(merged["crh04_1"] == 1) & (merged["crh04_2"] > 0)]
    
    # 4. Merge with portad to get household size (number of individuals)
    household_sizes = pd.merge(debt_positive, portad[["folio", "rel"]], on="folio", how="left")
    
    # 5. Calculate household size as the count of 'rel' per household
    household_size = household_sizes.groupby("folio")["rel"].sum().reset_index(name="household_size")
    
    # 6. Merge back with debt info to get total debt
    debt_info = pd.merge(debt_positive, household_size, on="folio", how="left")
    
    # 7. Merge with portad to get state info
    final_df = pd.merge(debt_info, portad[["folio", "ent"]], on="folio", how="left")
    
    # 8. Group by state ('ent'), compute average total debt and average household size, count households
    result = (
        final_df.groupby("ent")
        .agg(
            avg_total_debt=pd.NamedAgg(column="crh04_2", aggfunc="mean"),
            avg_household_size=pd.NamedAgg(column="household_size", aggfunc="mean"),
            household_count=pd.NamedAgg(column="folio", aggfunc="count")
        )
        .reset_index()
    )
    
    # 9. Rank by average total debt descending
    result = result.sort_values(by="avg_total_debt", ascending=False).reset_index(drop=True)
    
    # 10. Map 'ent' codes to state names for clarity (optional, not required)
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
    # Reorder columns for clarity
    result = result[["state", "ent", "avg_total_debt", "avg_household_size", "household_count"]]
    return result