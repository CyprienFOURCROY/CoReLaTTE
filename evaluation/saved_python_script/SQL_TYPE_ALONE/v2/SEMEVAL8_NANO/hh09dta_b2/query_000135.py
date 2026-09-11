def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    crh = tables["ii_crh"]
    ah = tables["ii_ah"]
    vlh = tables["ii_vlh"]
    su = tables["ii_su"]
    ah_enriched = tables["ii_ah_enriched"]
    vlh_enriched = tables["ii_vlh_enriched"]
    su_enriched = tables["ii_su_enriched"]

    # Merge portad with crh on 'folio'
    df = portad.merge(crh, on='folio', how='inner')
    # Merge with ah_enriched on 'folio' and 'ls'
    df = df.merge(ah_enriched, on=['folio', 'ls'], how='left')
    # Merge with vlh_enriched on 'folio'
    df = df.merge(vlh_enriched, on='folio', how='left')
    # Merge with su_enriched on 'folio'
    df = df.merge(su_enriched, on='folio', how='left')

    # Calculate overall average household size
    overall_avg_size = portad['ent'].mean()

    # Filter households larger than overall average
    df_large = df[df['ent'] > overall_avg_size]

    # Check for at least one member owning a motor vehicle
    # First, get all 'ls' per household
    # Merge with ah_enriched to get ownership info
    # For each household, check if any member owns a motor vehicle ('ah03d' == 1)
    ah_ownership = ah_enriched[['folio', 'ls', 'ah03d']]
    ah_ownership['owns_motor'] = ah_ownership['ah03d'] == 1
    household_motor = ah_ownership.groupby('folio')['owns_motor'].any().reset_index()

    # Merge with main df
    df_large = df_large.merge(household_motor, on='folio', how='left')

    # Filter households with at least one member owning a motor vehicle
    df_motor = df_large[df_large['owns_motor'] == True]

    # Filter households that report feeling very safe at home ('vlh04' == 1)
    # Merge with vlh_enriched to get 'vlh04'
    df_final = df_motor[df_motor['vlh04'] == 1]

    # For each household, get total debts plus interests in pesos ('crh04_2')
    # Merge with crh to get 'crh04_2'
    # Already merged, so just group by 'folio' and take the first non-null value
    debts = df_final.groupby('folio')['crh04_2'].first()

    # Compute the average total debt plus interest
    avg_debt = debts.mean()

    return pd.DataFrame(
        {"average_total_debt_in_pesos": [avg_debt]}
    )