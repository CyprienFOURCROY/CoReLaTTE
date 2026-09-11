def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_in = tables["ii_in"]
    df_enriched = tables["ii_inr_enriched"]
    df_portad_enriched = tables["ii_portad_enriched"]
    df_in_enriched = tables["ii_in_enriched"]
    
    # Merge portad with inr to get household info
    port_inr = pd.merge(df_portad, df_inr, on="folio", how="inner")
    # Merge with in to get info about last 12 months dairy production
    port_inr_in = pd.merge(port_inr, df_in, on="folio", how="inner")
    # Merge with enriched info for Liconsa milk
    port_inr_en = pd.merge(port_inr_in, df_enriched, on="folio", how="left")
    
    # Filter households where any member produce or sell dairy products last 12 months
    dairy_mask = port_inr_in["inr02a"] == 1
    households_with_dairy = port_inr_in[dairy_mask]
    
    # For each household, check if any member received Liconsa milk last 12 months
    # The relevant column is "in03a" in the enriched table
    # Merge again with enriched info for "in03a"
    households_with_dairy_en = pd.merge(households_with_dairy, df_in_enriched, on="folio", how="left")
    
    # Check if any household has "in03a" == 1 (received Liconsa milk)
    # Group by household (folio) and check if any member has in03a == 1
    household_group = households_with_dairy_en.groupby("folio")
    household_has_liconsa = household_group["in03a"].apply(lambda x: (x == 1).any())
    
    # Count total households with dairy production/sale per state
    # Merge with portad to get state info
    households_state = pd.merge(household_has_liconsa.reset_index(), df_portad[["folio", "ent"]], on="folio", how="left")
    # Count households with dairy per state
    result = (
        households_state
        .groupby("ent")
        .agg(
            households_with_dairy=("folio", "nunique"),
            households_with_liconsa=("folio", lambda x: x[household_has_liconsa.loc[x.index]].nunique())
        )
        .reset_index()
    )
    # Rename columns for clarity
    result = result.rename(columns={
        "ent": "state_code",
        "households_with_dairy": "households_with_dairy",
        "households_with_liconsa": "households_with_liconsa"
    })
    return result