def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]
    df_su = tables["ii_su"]
    df_su_enriched = tables["ii_su_enriched"]
    df_se_enriched = tables["ii_se_enriched"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad['ent'] == 20]
    
    # Merge households with land use info
    land_df = pd.merge(
        oaxaca_households[['folio']],
        df_su_enriched[['folio', 'su01']],
        on='folio',
        how='inner'
    )
    
    # Filter households that use a plot of land for farming (su01 == 1)
    households_with_land = land_df[land_df['su01'] == 1]
    
    # Merge with household info to get 'folio' for all relevant tables
    household_folios = households_with_land['folio']
    
    # Get household info from ii_ah
    ah_df = df_ah[df_ah['folio'].isin(household_folios)]
    
    # Merge with household info from ii_se
    se_df = df_se[df_se['folio'].isin(household_folios)]
    
    # Merge with household info from ii_su
    su_df = df_su[df_su['folio'].isin(household_folios)]
    
    # Merge with household info from ii_su_enriched
    su_enriched_df = df_su_enriched[df_su_enriched['folio'].isin(household_folios)]
    
    # Merge with household info from ii_se_enriched
    se_enriched_df = df_se_enriched[df_se_enriched['folio'].isin(household_folios)]
    
    # Filter households that did NOT lose their total crop in the last five years (se01e == 3)
    households_no_crop_loss = se_enriched_df[se_enriched_df['se01e'] == 3]
    
    # Get the 'folio' list for these households
    folios_no_crop_loss = households_no_crop_loss['folio']
    
    # Filter households that lost total crop (se01e == 1)
    households_crop_loss = se_enriched_df[se_enriched_df['se01e'] == 1]
    
    # Calculate average value of washing machines/stoves (ah04f_1 and ah04f_2) among households that lost total crop
    ah_crop_loss = ah_df[ah_df['folio'].isin(households_crop_loss['folio'])]
    # Filter out NaNs
    ah_crop_loss_valid = ah_crop_loss[ah_crop_loss['ah04f_1'].notna() & ah_crop_loss['ah04f_2'].notna()]
    # Compute total household value for washing machines/stoves
    ah_crop_loss_valid['total_value'] = ah_crop_loss_valid['ah04f_1'] + ah_crop_loss_valid['ah04f_2']
    # Calculate mean
    mean_value = ah_crop_loss_valid['total_value'].mean()
    
    # Filter households that did NOT lose total crop and have washing machine/stove value exceeding the mean
    ah_no_crop_loss = ah_df[ah_df['folio'].isin(folios_no_crop_loss)]
    # Filter out NaNs
    ah_no_crop_loss_valid = ah_no_crop_loss[ah_no_crop_loss['ah04f_1'].notna() & ah_no_crop_loss['ah04f_2'].notna()]
    # Calculate total household value
    ah_no_crop_loss_valid['total_value'] = ah_no_crop_loss_valid['ah04f_1'] + ah_no_crop_loss_valid['ah04f_2']
    # Select households exceeding the mean
    households_exceed_mean = ah_no_crop_loss_valid[ah_no_crop_loss_valid['total_value'] > mean_value]
    
    # Calculate the average total household value of washing machines/stoves for these households
    if not households_exceed_mean.empty:
        avg_value = households_exceed_mean['total_value'].mean()
    else:
        avg_value = float('nan')
    
    return pd.DataFrame({"average_total_value": [avg_value]})