def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    su = tables["ii_su"]
    crh = tables["ii_crh"]
    nna = tables["ii_nna"]
    # Filter households that use land for farming/vegetables
    land_use_mask = su["su01"] == 1
    # Filter households that did not produce or sell meat in last 12 months
    # inr columns for produce/sell meat: inr02c (produce), inr03c (sell quantity), inr04c (sell last month)
    # We consider produce/sell meat if inr02c == 1 (produce) or inr03c > 0 or inr04c > 0
    # But since inr03c and inr04c are quantities, check for > 0
    produce_meat_mask = (
        (inr["inr02c"] == 3) |  # produce meat: No
        ((inr["inr03c"] > 0) | (inr["inr04c"] > 0))
    )
    # Get household IDs satisfying both conditions
    households_land = portad[land_use_mask]
    households_meat = inr[produce_meat_mask]
    households = pd.merge(households_land, households_meat, on="folio", how="inner")
    # For these households, compute maximum amount paid on debts/loans in last 12 months
    # crh columns for amount paid: crh03b (more $1000), crh03c (more $5000), crh03d (more $10000)
    # crh03_2: amount in pesos
    # We consider only households with crh03_1 indicating they paid in last 12 months (value=1)
    # and crh03b, crh03c, crh03d indicating amounts above thresholds
    relevant_crh = tables["ii_crh"]
    # Filter households with last 12 months payment
    crh_paid_mask = relevant_crh["crh03_1"] == 1
    crh_paid = relevant_crh[crh_paid_mask]
    # Merge with households to get only relevant households
    households_crh = pd.merge(households[["folio"]], crh_paid, on="folio", how="inner")
    # For each household, find maximum amount paid in last 12 months
    # We consider the maximum among crh03b, crh03c, crh03d (which are binary indicators for above thresholds)
    # and crh03_2 for the amount
    # First, filter rows where crh03b, crh03c, crh03d indicate above thresholds
    amount_mask = (
        (households_crh["crh03b"] == 2) |
        (households_crh["crh03c"] == 2) |
        (households_crh["crh03d"] == 2)
    )
    households_with_amounts = households_crh[amount_mask]
    # Group by folio and get max amount
    max_amounts = households_with_amounts.groupby("folio")["crh03_2"].max()
    # Compute overall average of these maxima
    overall_avg_max = max_amounts.mean()
    # For each state, count households with at least 25 such households and max amount > overall average
    # Merge households with portad to get state info
    households_full = pd.merge(households, portad[["folio", "ent"]], on="folio", how="left")
    # Filter households with max amount > overall average
    qualifying = max_amounts[max_amounts > overall_avg_max]
    qualifying_folios = qualifying.index
    qualifying_households = households_full[households_full["folio"].isin(qualifying_folios)]
    # Count households per state
    counts = qualifying_households.groupby("ent").size()
    # Filter states with at least 25 households
    states_filtered = counts[counts >= 25]
    # For these states, get the maximum amount paid
    result_rows = []
    for state_code, count in states_filtered.items():
        max_amount = qualifying[max_amounts.index.get_level_values(0).map(lambda f: f if f in qualifying_folios else None)]
        # Get maximum amount for this state
        folios_in_state = qualifying_households[qualifying_households["ent"] == state_code]["folio"]
        max_amount_state = max_amount[max_amounts.index.isin(folios_in_state)].max()
        result_rows.append({
            "state": state_code,
            "household_count": count,
            "max_amount": max_amount_state
        })
    # Create DataFrame
    result_df = pd.DataFrame(result_rows)
    # Map state codes to state names if needed (not specified), else keep code
    # Return as per instructions
    return result_df[['state', 'household_count', 'max_amount']]