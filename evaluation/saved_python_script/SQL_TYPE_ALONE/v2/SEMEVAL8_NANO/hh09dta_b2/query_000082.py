def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    crh = tables["ii_crh"]
    # Merge portad with crh on 'folio' to get household info with debt info
    household_debt = portad[['folio', 'rel']].merge(crh[['folio', 'crh02_1']], on='folio', how='left')
    # Filter households that incurred debts in last 12 months (crh02_1 == 1)
    households_with_debt = household_debt[household_debt['crh02_1'] == 1]
    # Filter households that experienced at least one robbery/forced entry since 2005
    # 'vlh12a' indicates forced entry since 2005: 1 means yes
    household_robbery = tables["ii_vlh"][['folio', 'vlh12a']].dropna()
    households_robbery_since_2005 = household_robbery[household_robbery['vlh12a'] == 1]
    # Merge to find households that satisfy both conditions
    households_both = households_with_debt.merge(households_robbery_since_2005, on='folio', how='inner')
    # Merge with portad to get 'ent' (state) info
    households_both = households_both.merge(portad[['folio', 'ent']], on='folio', how='left')
    # Merge with inr to get 'ls' (individual ID) info
    households_both = households_both.merge(inr[['folio', 'ls']], on='folio', how='left')
    # Filter for individuals with 'rel' == 2 (respondent)
    respondents = households_both[households_both['rel'] == 2]
    # For these respondents, get their locality's 'vlh01t' (neighbors do favors) value
    # First, merge with 'ii_vlh' to get 'vlh01t' for each household
    household_favors = tables["ii_vlh"][['folio', 'vlh01t']].dropna()
    respondents = respondents.merge(household_favors, on='folio', how='left')
    # Calculate the average 'vlh01t' for households with both conditions
    avg_favors = respondents['vlh01t'].mean()
    # Now, get all households that incurred debts last 12 months
    all_households_debt = household_debt[household_debt['crh02_1'] == 1]
    # Merge with 'ii_vlh' to get 'vlh01t' for all these households
    all_households_debt = all_households_debt.merge(tables["ii_vlh"][['folio', 'vlh01t']], on='folio', how='left')
    # For households that did NOT incur debts, get their 'vlh01t'
    households_no_debt = household_debt[household_debt['crh02_1'] != 1]
    households_no_debt = households_no_debt.merge(tables["ii_vlh"][['folio', 'vlh01t']], on='folio', how='left')
    # Compute the average 'vlh01t' for households without debts
    avg_favors_no_debt = households_no_debt['vlh01t'].mean()
    # Count households with debts and 'vlh01t' > average of no-debt households
    count = all_households_debt[all_households_debt['vlh01t'] > avg_favors_no_debt].shape[0]
    return pd.DataFrame({"count": [count]})