def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_su = tables["ii_su"]
    
    # Filter households that use a plot/land for sowing/farming (su01 == 1)
    households_with_plot = df_su[df_su["su01"] == 1]
    
    # Merge households with their crh data on 'folio'
    merged = pd.merge(households_with_plot, df_crh, on="folio", how="inner")
    
    # Filter households with reported total debts + interests (crh04_1 != nan and crh04_1 != 8)
    debt_reported = merged[merged["crh04_1"].notna() & (merged["crh04_1"] != 8)]
    
    # Calculate overall average total debts + interests in pesos
    overall_avg = debt_reported["crh04_2"].mean()
    
    # Group by state ('ent') and aggregate
    group = debt_reported.groupby("ent").agg(
        household_count=pd.NamedAgg(column="folio", aggfunc="count"),
        average_debt=pd.NamedAgg(column="crh04_2", aggfunc="mean")
    ).reset_index()
    
    # Filter states with at least 20 households and average debt above overall average
    qualifying = group[(group["household_count"] >= 20) & (group["average_debt"] > overall_avg)]
    
    # Merge with portad to get state names
    result = pd.merge(qualifying, df_portad[["ent"]], on="ent", how="left")
    
    # Sort by average debt descending
    result_sorted = result.sort_values(by="average_debt", ascending=False)
    
    # Select relevant columns
    final = result_sorted[["ent", "household_count", "average_debt"]]
    
    return final