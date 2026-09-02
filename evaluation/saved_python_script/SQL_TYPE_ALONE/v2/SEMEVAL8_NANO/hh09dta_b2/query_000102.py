def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_in = tables["ii_in"]
    df_su = tables["ii_su"]
    df_inr = tables["ii_inr"]
    df_su_enriched = tables["ii_su_enriched"]
    df_inr_enriched = tables["ii_inr_enriched"]
    df_portad_enriched = tables.get("ii_portad_enriched")  # Not used here, but included if needed

    # Filter for Oaxaca (15) or Puebla (21)
    states_of_interest = [15, 21]
    portad_states = df_portad[df_portad['ent'].isin(states_of_interest)]

    # Filter households that use a plot of land for farming
    land_use = df_su[df_su['su01'] == 1]
    land_use_households = land_use[['folio']]

    # Filter households that own/share a non-agricultural business
    nna = df_nna[df_nna['nna01'] == 1]
    nna_households = nna[['folio']]

    # Merge to get households that satisfy both land use and non-ag business ownership
    households = pd.merge(land_use_households, nna_households, on='folio', how='inner')

    # Merge with portad to get state info
    households = pd.merge(households, portad_states[['folio', 'ent']], on='folio', how='inner')

    # Filter for households in the relevant states
    households = households[households['ent'].isin(states_of_interest)]

    # Merge with ii_in to get direct payments from "Other Government Program"
    in_data = df_in[['folio', 'in02a10']]  # Amount received directly from "Other Government Program"
    households_in = pd.merge(households, in_data, on='folio', how='left')

    # Replace NaN with 0 for amount received
    households_in['in02a10'] = households_in['in02a10'].fillna(0)

    # Calculate the average amount received from "Other Government Program" for land-using households
    avg_payment = households_in['in02a10'].mean()

    # Filter households that received a positive amount above the average
    result = households_in[
        (households_in['in02a10'] > 0) & (households_in['in02a10'] > avg_payment)
    ]

    # Select relevant columns and sort by amount received descending
    result = result[['folio', 'ent', 'in02a10']]
    result = result.sort_values(by='in02a10', ascending=False).reset_index(drop=True)

    return result