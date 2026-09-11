def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]
    df_inr = tables["ii_inr"]
    df_inr_enriched = tables["ii_inr_enriched"]
    df_ah_enriched = tables["ii_ah_enriched"]
    df_vlh_enriched = tables["ii_vlh_enriched"]
    
    # Merge portad with in to get household info
    port_in = pd.merge(df_portad, df_in, on="folio", how="inner")
    
    # Filter households with positive amount from 'in02a10' (Other Government Program)
    households_with_other_gov = port_in[
        port_in["in02a10"] > 0
    ]["folio"]
    
    # Merge with ah to get ownership of motor vehicle
    households_with_ah = pd.merge(
        households_with_other_gov.to_frame(),
        df_ah[["folio", "ah03d"]],
        on="folio",
        how="left"
    )
    
    # Merge with portad to get 'ent' (state)
    households_full = pd.merge(
        households_with_ah,
        df_portad[["folio", "ent"]],
        on="folio",
        how="left"
    )
    
    # Filter households that feel unsafe or very unsafe at home
    households_full = pd.merge(
        households_full,
        df_vlh[["folio", "vlh04"]],
        on="folio",
        how="left"
    )
    households_full = households_full[
        households_full["vlh04"].isin([3, 4])
    ]
    
    # Filter households that own a motor vehicle ('ah03d' == 1)
    households_full = households_full[
        households_full["ah03d"] == 1
    ]
    
    # Count households per state
    result = (
        households_full.groupby("ent")
        .size()
        .reset_index(name="household_count")
    )
    
    # Calculate average number of households with these conditions
    avg_count = result["household_count"].mean()
    
    # Filter states with above-average households
    above_avg_states = result[result["household_count"] > avg_count]
    
    # Return result with state codes and counts
    return above_avg_states[['ent', 'household_count']]