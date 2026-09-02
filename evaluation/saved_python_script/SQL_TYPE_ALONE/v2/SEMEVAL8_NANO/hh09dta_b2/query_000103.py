def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    
    # Filter for Oaxaca (ent == 20)
    oaxaca_portad = portad[portad["ent"] == 20]
    
    # Merge portad with se on 'folio'
    merged = pd.merge(oaxaca_portad, se, on="folio", how="inner")
    
    # Filter households with at least one member aged 60 or older
    has_elderly = merged[merged["edad"] >= 60]
    households_with_elderly = has_elderly["folio"].unique()
    
    # Filter households that feel unsafe or very unsafe at home (vlh04 in 1 or 2)
    unsafe_mask = merged["vlh04"].isin([1, 2])
    households_unsafe = merged[unsafe_mask]["folio"].unique()
    
    # Filter households with reported death in last five years (se01a == 1)
    households_with_death = merged[merged["se01a"] == 1]["folio"].unique()
    
    # Find households satisfying all three conditions
    target_households = set(households_with_elderly) & set(households_unsafe) & set(households_with_death)
    
    # Count the number of such households
    count = len(target_households)
    
    return pd.DataFrame({"households": [count]})