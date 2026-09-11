def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    vlh = tables["ii_vlh"]
    nna = tables["ii_nna"]
    su = tables["ii_su"]
    
    # Filter households with at least one member aged 18-29
    households_age_18_29 = portad[portad['edad'].between(18, 29)]
    households_with_age_18_29 = households_age_18_29['folio'].unique()

    # Filter households that experienced any household shock in last 5 years
    shock_conditions = (
        (se['se01a'] == 1) |  # death
        (se['se01b'] == 1) |  # disease/accident/hospital
        (se['se01c'] == 1) |  # unemployment/failure
        (se['se01d'] == 1) |  # lost dwelling/disaster
        (se['se01e'] == 1) |  # total crop loss
        (se['se01f'] == 1)    # loss/robbery/death of animals
    )
    households_shock = se[shock_conditions]['folio'].unique()

    # Filter households with at least one break-in/robbery since 2005
    # Check 'vlh12a' since 2005 (values 1 or 2 indicate rob since 2005)
    rob_since_2005 = (
        (vlh['vlh12a'] == 1) |  # into current house
        (vlh['vlh12a_b'] == 2)  # into previous house
    )
    households_rob = vlh[rob_since_2005]['folio'].unique()

    # Find households satisfying all three conditions
    target_folios = set(households_with_age_18_29) & set(households_shock) & set(households_rob)

    # Filter 'nna' for these households
    nna_filtered = nna[nna['folio'].isin(target_folios)]

    # Calculate mean of 'nna01' (ownership/sharing of non-agricultural business)
    avg_nna01 = nna_filtered['nna01'].mean()

    return pd.DataFrame(
        {"average_non_ag_business": [avg_nna01]}
    )