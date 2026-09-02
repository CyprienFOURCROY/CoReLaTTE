def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20]
    
    # Households that use a plot of land for sowing/farming/vegetables (su01a == 1)
    households_with_plot = df_se[df_se["su01"] == 1]["folio"]
    
    # Households that reported a household member died in the last five years (se01a == 1)
    households_with_death = df_se[df_se["se01a"] == 1]["folio"]
    
    # Find intersection of households that satisfy both conditions
    households_both = pd.Series(
        list(set(households_with_plot) & set(households_with_death))
    )
    
    # Filter for Oaxaca households that meet both conditions
    result = oaxaca_households[oaxaca_households["folio"].isin(households_both)]
    
    # Count the number of such households
    count = len(result)
    
    return pd.DataFrame({"count": [count]})