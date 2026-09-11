def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_ah = tables["ii_ah"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]
    df_su_enriched = tables["ii_su_enriched"]
    df_ah_enriched = tables["ii_ah_enriched"]
    df_inr_enriched = tables["ii_inr_enriched"]
    
    # Filter households in Oaxaca (ent == 20) that use a plot for farming (su01 == 1)
    # Merge households with plot data
    households_with_plot = df_portad[df_portad["ent"] == 20]
    plot_data = df_su_enriched[df_su_enriched["su01"] == 1]
    households_in_oaxaca_with_plot = households_with_plot.merge(
        plot_data[["folio"]],
        on="folio",
        how="inner"
    )
    
    # Get households' total debt (crh) and total expense on workers (su237)
    crh_filtered = df_crh[df_crh["folio"].isin(households_in_oaxaca_with_plot["folio"])]
    ah_filtered = df_ah_enriched[df_ah_enriched["folio"].isin(households_in_oaxaca_with_plot["folio"])]
    su_filtered = df_su_enriched[df_su_enriched["folio"].isin(households_in_oaxaca_with_plot["folio"])]
    inr_filtered = df_inr_enriched[df_inr_enriched["folio"].isin(households_in_oaxaca_with_plot["folio"])]
    
    # Compute total debt per household
    crh_group = crh_filtered.groupby("folio")["crh02_2"].sum(min_count=1)
    total_debt = crh_group[crh_group > 0]
    
    # Compute total expense on workers (su237) per household
    su_group = su_filtered.groupby("folio")["su237"].sum(min_count=1)
    total_workers_expense = su_group
    
    # Filter households with positive total debt
    households_with_debt = total_debt.index
    
    # Calculate average expense on workers across all households in Oaxaca with plot
    avg_workers_expense = total_workers_expense.mean()
    
    # Filter households with total expense on workers above the average
    households_above_avg_workers = total_workers_expense[total_workers_expense > avg_workers_expense].index
    
    # Find households that have both positive total debt and above-average workers expense
    target_households = set(households_with_debt).intersection(households_above_avg_workers)
    
    # For these households, get their electronic device value (ah04e_2)
    ah_target = ah_filtered[ah_filtered["folio"].isin(target_households)]
    
    # Merge with household info to get 'ent' for filtering Oaxaca households
    ah_target = ah_target.merge(
        df_portad[["folio", "ent"]],
        on="folio",
        how="left"
    )
    
    # Filter for Oaxaca households
    ah_oaxaca = ah_target[ah_target["ent"] == 20]
    
    # Compute the average value of electronic devices
    avg_electronic_value = ah_oaxaca["ah04e_2"].mean()
    
    # Return as DataFrame
    return pd.DataFrame(
        {"average_electronic_device_value": [avg_electronic_value]}
    )