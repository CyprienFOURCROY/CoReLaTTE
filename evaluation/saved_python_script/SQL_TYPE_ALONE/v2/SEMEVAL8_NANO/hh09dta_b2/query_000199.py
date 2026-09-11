def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]

    # Merge portad and in on 'folio' to get household info with household-level data
    merged = pd.merge(df_portad, df_in, on='folio', how='inner')
    # Merge with ah on 'folio' and 'ls' to get household assets info per individual
    merged = pd.merge(merged, df_ah, on=['folio', 'ls'], how='inner')

    # Filter households with at least one member aged 60 or older
    households_with_60_plus = merged[merged['edad'] >= 60]['folio'].unique()

    # Filter merged data to only include these households
    filtered = merged[merged['folio'].isin(households_with_60_plus)]

    # Conditions:
    # 1. Household has at least one member aged 60 or older (already filtered)
    # 2. Report owning electronic devices with positive stated value
    #    - 'ah04e_1' == 1 (Yes), 'ah04e_2' > 0
    # 3. Received a positive direct amount from an Other Government Program
    #    - 'in02a12' > 0

    # Filter for electronic devices owned with positive value
    electronic_mask = (
        (filtered['ah04e_1'] == 1) &
        (filtered['ah04e_2'] > 0)
    )

    # Filter for positive amount received from 'Other Government Program'
    income_mask = filtered['in02a12'] > 0

    # Combine masks
    final_mask = electronic_mask & income_mask

    # Get unique households satisfying all conditions
    households_meet_criteria = filtered[final_mask]['folio'].unique()

    # For these households, compute the maximum reported value of electronic devices per household
    # We need to find the maximum 'ah04e_2' per household
    household_max_values = (
        filtered[filtered['folio'].isin(households_meet_criteria)]
        .groupby('folio')['ah04e_2']
        .max()
        .dropna()
    )

    # Calculate the average of these maximum values
    if len(household_max_values) > 0:
        avg_max_value = household_max_values.mean()
        count_households = len(household_max_values)
    else:
        avg_max_value = float('nan')
        count_households = 0

    result_df = pd.DataFrame(
        {
            "average_max_electronic_value": [avg_max_value],
            "household_count": [count_households]
        }
    )

    return result_df