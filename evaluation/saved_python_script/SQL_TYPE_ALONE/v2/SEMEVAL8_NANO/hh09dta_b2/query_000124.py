def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    su = tables["ii_su"]
    
    # Filter households with at least one adult (edad >= 18)
    adults = portad[portad['edad'] >= 18]
    households_with_adults = adults['folio'].unique()
    
    # Filter households with at least one minor (edad < 18)
    minors = portad[portad['edad'] < 18]
    households_with_minors = minors['folio'].unique()
    
    # Households with at least one adult and one minor
    households_both = set(households_with_adults) & set(households_with_minors)
    
    # Filter households where a household member owns/shares non-ag business (nna01 == 1)
    nna_owned = nna[nna['nna01'] == 1]
    households_with_nna = nna_owned['folio'].unique()
    
    # Filter households where a household member uses land for sowing/farming/vegetables (su01 == 1)
    su_use_land = su[su['su01'] == 1]
    households_with_su = su_use_land['folio'].unique()
    
    # Households satisfying all conditions
    target_households = set(households_both) & set(households_with_nna) & set(households_with_su)
    
    # Count the number of such households
    count = len(target_households)
    
    return pd.DataFrame({"households": [count]})