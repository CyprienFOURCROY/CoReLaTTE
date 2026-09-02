def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    # Extract tables
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad['ent'] == 20]
    # Filter households with at least one adult (edad >= 18)
    # Since 'edad' is per individual, get households with any adult
    adults = oaxaca_households[oaxaca_households['edad'] >= 18]
    households_with_adults = adults['folio'].unique()
    # Filter households in the above list
    df_oaxaca = oaxaca_households[df_portad['folio'].isin(households_with_adults)]
    # Filter households that did NOT receive Liconsa milk in last 12 months (in03a != 1)
    in_oaxaca = df_in[df_in['folio'].isin(df_portad['folio'])]
    in_oaxaca = in_oaxaca[~in_oaxaca['folio'].isin(df_in[df_in['in03a'] == 1]['folio'])]
    # Merge to keep only households in Oaxaca with adults and not received Liconsa
    df_filtered = df_oaxaca[df_oaxaca['folio'].isin(in_oaxaca['folio'])]
    # Merge with crh to get debts info
    df_crh_filtered = df_crh[df_crh['folio'].isin(df_filtered['folio'])]
    # Filter households with total debts + interests (crh04_1) > 0
    households_with_debt = df_crh_filtered[
        (df_crh_filtered['crh04_1'] == 1) & (df_crh_filtered['crh04_2'] > 0)
    ]['folio']
    # Calculate average debts for these households
    debts = df_crh_filtered[
        (df_crh_filtered['folio'].isin(households_with_debt))
        & (df_crh_filtered['crh04_1'] == 1)
    ]['crh04_2']
    if len(debts) == 0:
        avg_debt = 0
    else:
        avg_debt = debts.mean()
    # Households with debts exceeding the average
    households_exceeding_debt = df_crh_filtered[
        (df_crh_filtered['folio'].isin(households_with_debt))
        & (df_crh_filtered['crh04_2'] > avg_debt)
    ]['folio']
    # Filter households that directly received a positive amount from the Other Government Program (in02a10 > 0)
    in_direct = df_in[
        (df_in['folio'].isin(households_exceeding_debt))
        & (df_in['in02a10'] > 0)
    ]['folio']
    # Final households: in all conditions
    final_households = df_in[
        (df_in['folio'].isin(in_direct))
    ]['folio'].unique()
    # Count households
    count = len(final_households)
    return pd.DataFrame({"household_count": [count]})