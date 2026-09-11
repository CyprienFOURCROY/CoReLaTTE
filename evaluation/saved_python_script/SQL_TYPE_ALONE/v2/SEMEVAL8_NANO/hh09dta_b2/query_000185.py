def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    su = tables["ii_su"]
    inr = tables["ii_inr"]
    
    # Filter households in Oaxaca (ent == 15) that produced or sold eggs (inr02d == 1)
    # and have at least one adult (edad >= 18)
    # Merge portad with inr on 'folio'
    merged = pd.merge(portad, inr, on='folio', how='inner')
    
    # Filter for Oaxaca
    oaxaca = merged[merged['ent'] == 15]
    
    # Filter households that produced or sold eggs in last 12 months (inr02d == 1)
    eggs_production = oaxaca[oaxaca['inr02d'] == 1]
    
    # Merge with portad to get ages
    # Already merged, so filter for adults (edad >= 18)
    adults = eggs_production[eggs_production['edad'] >= 18]
    
    # For each household, find the maximum age
    max_age_per_household = adults.groupby('folio')['edad'].max()
    
    # Calculate the average of these maximum ages
    average_age = max_age_per_household.mean()
    
    return pd.DataFrame(
        {"average_age": [average_age]}
    )