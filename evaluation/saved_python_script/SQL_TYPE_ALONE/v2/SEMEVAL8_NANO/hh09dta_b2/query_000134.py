def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Filter households that reported owing money in the last 12 months
    # crh['crh02_1'] == 1 indicates they have debts
    debt_households = crh[crh['crh02_1'] == 1]['folio'].unique()
    
    # Filter portad for these households
    portad_debt = portad[portad['folio'].isin(debt_households)]
    
    # Determine which portad households have at least one adult (age >= 18)
    adults = portad_debt[portad_debt['edad'] >= 18]
    households_with_adults = adults['folio'].unique()
    
    # Determine which portad households have at least one child (age < 18)
    children = portad_debt[portad_debt['edad'] < 18]
    households_with_children = children['folio'].unique()
    
    # Find households that have both at least one adult and one child
    households_both = set(households_with_adults).intersection(set(households_with_children))
    
    # Count how many households meet both conditions
    count = len(households_both)
    
    return pd.DataFrame({"households_with_both": [count]})