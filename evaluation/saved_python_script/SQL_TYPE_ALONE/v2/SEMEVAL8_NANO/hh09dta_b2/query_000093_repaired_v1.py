def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]
    
    # Filter households in Oaxaca (ent == 15)
    oaxaca_households = df_portad[df_portad["ent"] == 15]
    
    # Filter households with at least one member aged 70 or older
    households_70_plus = oaxaca_households[oaxaca_households["edad"] >= 70]
    household_ids_70_plus = households_70_plus["folio"].unique()
    
    # Filter households that received income from "Other Government Program" in last 12 months
    in_filtered = df_in[
        (df_in["folio"].isin(household_ids_70_plus)) &
        (df_in["in01a10_1"] == 1)  # Participated and received income
    ]
    household_ids_in_income = in_filtered["folio"].unique()
    
    # Filter households that received credit/loans in last 12 months
    crh_filtered = df_crh[
        (df_crh["folio"].isin(household_ids_in_income)) &
        (df_crh["crh02_1"] == 1)  # Had debts in last 12 months
    ]
    
    # Get debts (total debts + interests) for these households
    debts = crh_filtered[["folio", "crh04_2"]].dropna(subset=["crh04_2"])
    
    # Calculate group average of total debts
    average_debt = debts["crh04_2"].mean()
    
    # Select households with debts above the group average
    above_avg_debts = debts[debts["crh04_2"] > average_debt]
    
    # Rank from highest to lowest
    ranked_debts = above_avg_debts.sort_values(by="crh04_2", ascending=False)
    
    # Prepare result DataFrame
    result = ranked_debts.rename(columns={"crh04_2": "debt_amount_pesos"})
    
    return result.reset_index(drop=True)