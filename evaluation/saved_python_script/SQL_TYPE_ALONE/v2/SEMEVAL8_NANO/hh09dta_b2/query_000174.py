def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_se = tables["ii_se"]
    df_nna = tables["ii_nna"]
    
    # Filter households with at least one member aged 60 or older
    households_age_60_plus = df_portad[df_portad['edad'] >= 60]['folio'].unique()
    
    # Filter households with at least one member younger than 15
    households_under_15 = df_portad[df_portad['edad'] < 15]['folio'].unique()
    
    # Households with at least one member aged 60+ and one under 15
    households_both = set(households_age_60_plus).intersection(set(households_under_15))
    
    # Filter households with a reported household illness/accident/hospitalization in last five years
    households_with_health_issue = df_se[
        (df_se['se01a'] == 1) | 
        (df_se['se01b'] == 1) | 
        (df_se['se01c'] == 1) | 
        (df_se['se01d'] == 1) | 
        (df_se['se01e'] == 1) | 
        (df_se['se01f'] == 1)
    ]['folio'].unique()
    
    # Filter households that received income from an Other Government Program in last 12 months
    households_received_other_gov = df_in[
        (df_in['in01a10_1'] == 1) | (df_in['in01a10_2'].notna())
    ]['folio'].unique()
    
    # Final households satisfying all conditions
    final_households = set(households_both).intersection(set(households_with_health_issue)).intersection(set(households_received_other_gov))
    
    # Return count as DataFrame
    return pd.DataFrame({"household_count": [len(final_households)]})