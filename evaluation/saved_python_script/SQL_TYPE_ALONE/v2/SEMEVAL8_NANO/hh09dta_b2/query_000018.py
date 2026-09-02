def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    inr = tables["ii_inr"]
    
    # Filter households in Oaxaca (ent == 20) with at least one adult (edad >= 18)
    adults = portad[portad['edad'] >= 18]
    oaxaca_households = adults[adults['ent'] == 20]['folio'].unique()
    
    # Filter households that produced or sold eggs in the last 12 months (inr02d == 1)
    inr_eggs = inr[inr['folio'].isin(oaxaca_households)]
    households_with_eggs = inr_eggs[inr_eggs['inr02d'] == 1]['folio'].unique()
    
    # Filter households where a household member owns or shares a non-agricultural business (nna01 == 1)
    nna_owned = nna[nna['folio'].isin(oaxaca_households)]
    households_with_business = nna_owned[nna_owned['nna01'] == 1]['folio'].unique()
    
    # Find households that satisfy all conditions
    target_folios = set(households_with_eggs).intersection(set(households_with_business))
    
    # Filter inr data for these households
    inr_target = inr[inr['folio'].isin(target_folios)]
    
    # Calculate the average number of non-agricultural businesses owned or shared in the last 12 months
    # For each household, count the number of businesses (nna01 == 1)
    # Since nna01 indicates ownership/sharing, count per household
    # First, get household list again to ensure filtering
    # Count number of businesses per household
    business_counts = nna[nna['folio'].isin(target_folios)].groupby('folio')['nna01'].apply(lambda x: (x == 1).sum())
    # Merge counts with households that have eggs and business ownership
    # For each household, get the count
    counts_df = business_counts.reset_index().rename(columns={'nna01': 'business_count'})
    # Filter to only households in target_folios
    counts_df = counts_df[counts_df['folio'].isin(target_folios)]
    # Compute the mean
    avg_businesses = counts_df['business_count'].mean()
    
    return pd.DataFrame(
        {"average_non_agri_businesses": [avg_businesses]}
    )