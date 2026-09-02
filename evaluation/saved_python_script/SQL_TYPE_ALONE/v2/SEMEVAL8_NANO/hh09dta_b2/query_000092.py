def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_inr = tables["ii_inr"]
    df_nna = tables["ii_nna"]
    df_se = tables["ii_se"]
    
    # Compute overall average age
    overall_avg_age = df_portad['edad'].mean()

    # Filter households that both lost total crop in last 5 years and own/share non-ag business
    # 1. Households that lost total crop in last 5 years
    crop_loss = df_se[df_se['se01e'] == 1]['folio']
    # 2. Households that own/share non-ag business
    nna_yes = df_nna[df_nna['nna01'] == 1]['folio']
    # Intersection: households satisfying both conditions
    households_both = set(crop_loss).intersection(set(nna_yes))
    df_both = df_portad[df_portad['folio'].isin(households_both)]

    # Get states of these households
    households_states = df_both[['folio', 'ent']].drop_duplicates()

    # Compute mean age per state
    df_portad_state = df_portad[['folio', 'edad', 'ent']]
    state_avg_age = df_portad_state.groupby('ent')['edad'].mean()

    # Filter states where average age > overall average age
    states_higher_avg = state_avg_age[state_avg_age > overall_avg_age].index.tolist()

    # Filter households in these states
    households_in_states = df_portad[df_portad['ent'].isin(states_higher_avg)]
    households_in_states_set = set(households_in_states['folio'])

    # Final households: intersection of households_both and households_in_states
    final_households = set(households_both).intersection(households_in_states_set)

    # Count households
    count = len(final_households)

    return pd.DataFrame(
        {"count": [count]}
    )