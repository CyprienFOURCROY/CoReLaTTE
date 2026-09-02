def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    vlh = tables["ii_vlh"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Filter for Oaxaca (ent == 20)
    oaxaca_portad = portad[portad["ent"] == 20]
    
    # Merge portad with ah, vlh, nna, crh on 'folio' and 'ls' where applicable
    merged = oaxaca_portad.merge(ah, on=["folio", "ls"], how="left")
    merged = merged.merge(vlh, on="folio", how="left")
    merged = merged.merge(nna, on="folio", how="left")
    merged = merged.merge(crh, on="folio", how="left")
    
    # Filter households with at least one member aged 60 or older
    has_senior = merged["edad"] >= 60
    
    # Filter households where at least one member reports feeling unsafe or very unsafe at home
    unsafe_mask = merged["vlh04"].isin([1, 2])  # 1: Very safe, 2: Safe, so exclude these
    # Correction: feeling unsafe or very unsafe means vlh04 in [3,4]
    unsafe_mask = merged["vlh04"].isin([3, 4])
    
    # Filter households that have incurred credit/loan debt in last 12 months with amount
    # crh02_1: 1=Value, 2=Did not incur debts, 8=DK
    # crh02_2: amount in pesos
    debt_mask = (merged["crh02_1"] == 1) & (merged["crh02_2"].notna())
    
    # Combine all conditions
    final_mask = has_senior & unsafe_mask & debt_mask
    
    # Get unique household IDs that meet all criteria
    households = merged[final_mask]["folio"].drop_duplicates()
    
    # Count households
    count = len(households)
    
    return pd.DataFrame({"households_with_conditions": [count]})