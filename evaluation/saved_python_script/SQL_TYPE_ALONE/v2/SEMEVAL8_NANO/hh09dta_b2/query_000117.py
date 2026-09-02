def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    
    # Merge portad and nna on 'folio'
    merged = pd.merge(portad, nna, on='folio', how='left')
    
    # Identify households with at least one member owning/sharing a non-agricultural business (nna01 == 1)
    households_with_business = merged[merged['nna01'] == 1]['folio'].unique()
    
    # Identify households where no member owns/shares a non-agricultural business (nna01 == 2)
    households_without_business = merged[merged['nna01'] == 2]['folio'].unique()
    
    # Calculate average age in households without such members
    ages_in_no_business_households = merged[merged['folio'].isin(households_without_business)]['edad']
    average_age_no_business = ages_in_no_business_households.mean()
    
    # Filter individuals in households with at least one member owning/sharing a non-agricultural business
    individuals_in_business_households = merged[merged['folio'].isin(households_with_business)]
    
    # Select individuals older than the average age of the other group
    older_individuals = individuals_in_business_households[individuals_in_business_households['edad'] > average_age_no_business]
    
    # Select required columns
    result = older_individuals[['folio', 'ls', 'edad']]
    
    return result