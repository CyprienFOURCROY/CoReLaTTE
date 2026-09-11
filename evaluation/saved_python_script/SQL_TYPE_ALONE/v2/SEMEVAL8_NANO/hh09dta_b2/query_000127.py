def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    vlh = tables["ii_vlh"]
    nna = tables["ii_nna"]
    nna_enriched = tables["ii_nna_enriched"]
    vlh_enriched = tables["ii_vlh_enriched"]
    inr = tables["ii_inr"]
    inr_enriched = tables["ii_inr_enriched"]
    
    # Define shock indicators based on 'se' table
    shocks = se[['folio']].copy()
    shocks['shock'] = (
        (se['se01a'] == 1) |  # death of HHM
        (se['se01b'] == 1) |  # disease/accident/hospital
        (se['se01c'] == 1) |  # unemployment/failure
        (se['se01d'] == 1) |  # lost dwelling/disaster
        (se['se01e'] == 1) |  # crop loss
        (se['se01f'] == 1)    # loss/robbery/death animals
    )
    
    # Get households with any shocks
    households_with_shocks = shocks[shocks['shock']]['folio'].unique()
    households_no_shocks = shocks[~shocks['shock']]['folio'].unique()
    
    # Compute average total break-ins/robberies since 2005 for households with no shocks
    vlh_no_shocks = vlh[vlh['folio'].isin(households_no_shocks)]
    avg_breakins_no_shocks = vlh_no_shocks['vlh18a'].mean()
    
    # Filter households with shocks
    vlh_shocks = vlh[vlh['folio'].isin(households_with_shocks)]
    # Select households with total break-ins > average of no-shock households
    result = vlh_shocks[vlh_shocks['vlh18a'] > avg_breakins_no_shocks][['folio', 'vlh18a']]
    
    return result.reset_index(drop=True)