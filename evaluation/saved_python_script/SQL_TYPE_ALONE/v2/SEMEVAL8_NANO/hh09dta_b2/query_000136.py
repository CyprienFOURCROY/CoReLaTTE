def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    in_table = tables["ii_in"]
    se = tables["ii_se"]
    en = tables["ii_enriched"]
    se_en = tables["ii_se_enriched"]
    in_en = tables["ii_in_enriched"]
    
    # Filter households with positive amount directly from "Other Government Program" (in02a12)
    households_with_other_gov = in_en[in_en["in02a12"] > 0][["folio"]].drop_duplicates()

    # Merge with portad to get state info
    households_with_state = pd.merge(households_with_other_gov, portad[["folio", "ent"]], on="folio", how="left")
    
    # Count total households per state
    total_households_per_state = (
        households_with_state.groupby("ent")
        .size()
        .reset_index(name="total_households")
    )
    
    # Filter households that have at least 30 households with positive "Other Government Program" amount
    valid_states = total_households_per_state[total_households_per_state["total_households"] >= 30]
    
    # For these states, count households with positive "Other Government Program" (already filtered)
    # and count households that produced or sold dairy products in last 12 months (inr03a == 1)
    # Merge households with inr data
    households_inr = pd.merge(households_with_state, inr[["folio", "inr02a"]], on="folio", how="left")
    
    # Filter households that produced or sold dairy in last 12 months
    dairy_producers = households_inr[households_inr["inr02a"] == 1]
    
    # Count households per state that produced/sold dairy
    dairy_counts = (
        dairy_producers.groupby("ent")
        .size()
        .reset_index(name="dairy_households")
    )
    
    # Merge valid states with dairy counts
    result = pd.merge(valid_states, dairy_counts, on="ent", how="left")
    
    # Fill NaN dairy counts with 0
    result["dairy_households"] = result["dairy_households"].fillna(0).astype(int)
    
    # Rename 'ent' to 'state_code' for clarity
    result = result.rename(columns={"ent": "state_code"})
    
    # Select and order columns
    result = result[["state_code", "total_households", "dairy_households"]]
    
    return result