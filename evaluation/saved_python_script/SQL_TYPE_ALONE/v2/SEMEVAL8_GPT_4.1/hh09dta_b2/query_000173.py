def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]

    # 1. Households that reported a household member’s death in the last five years
    # se01a == 1 means Yes
    hh_death = df_se[df_se["se01a"] == 1.0]["folio"].unique()

    # 2. For each household, check if at least one adult (age 18+) exists
    adults = df_portad[df_portad["edad"] >= 18]
    adults_in_hh = adults[adults["folio"].isin(hh_death)].groupby("folio").size().reset_index(name="n_adults")
    adults_in_hh = adults_in_hh[adults_in_hh["n_adults"] > 0]["folio"].unique()

    # 3. For each household, check if at least one member owns a domestic appliance (ah03g == 1)
    owns_domestic = df_ah[(df_ah["ah03g"] == 1.0) & (df_ah["folio"].isin(hh_death))]
    owns_domestic_hh = owns_domestic["folio"].unique()

    # 4. Households that satisfy both: at least one adult and at least one member owns a domestic appliance
    hh_both = set(adults_in_hh) & set(owns_domestic_hh)

    # 5. For each state, count:
    #    - total households with a death in last 5 years
    #    - households with a death, at least one adult, and at least one member owns a domestic appliance

    # Get state for each household (use first occurrence in ii_portad)
    hh_state = df_portad.drop_duplicates("folio")[["folio", "ent"]].set_index("folio")["ent"]

    # Only consider households that reported a death
    hh_death_states = hh_state.loc[hh_death].dropna().astype(int)
    # Only consider households that satisfy both conditions
    hh_both_states = hh_state.loc[list(hh_both)].dropna().astype(int)

    # Count per state
    total_death = hh_death_states.value_counts().sort_index()
    total_both = hh_both_states.value_counts().sort_index()

    # Prepare DataFrame
    states = sorted(set(total_death.index) | set(total_both.index))
    result = pd.DataFrame({
        "state": states,
        "households_with_death_and_adult_and_domestic_appliance": [total_both.get(s, 0) for s in states],
        "households_with_death": [total_death.get(s, 0) for s in states]
    })

    return result