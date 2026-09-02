def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    inr = tables["ii_inr"]
    crh = tables["ii_crh"]
    vlh = tables["ii_vlh"]
    
    # Filter households with zero break-ins since 2005
    # Break-ins are indicated by vlh12a, vlh12a_b, vlh12a_c
    # Zero break-ins if all are not equal to 1 or 2 (i.e., no break-in into current or previous house)
    break_in_mask = (
        (vlh["vlh12a"] != 1) & (vlh["vlh12a_b"] != 1) & (vlh["vlh12a_c"] != 1)
    )
    households_no_breakins = vlh[break_in_mask][["folio"]]
    
    # Filter individuals who report knowing a family/friend robbed in last 12 months
    # 'vlh10a' == 1 indicates 'Yes'
    known_rob_mask = vlh["vlh10a"] == 1
    households_known_rob = vlh[known_rob_mask][["folio"]]
    
    # Merge to get individuals who meet both conditions
    households_both = pd.merge(households_no_breakins, households_known_rob, on="folio", how="inner")
    
    # Get individuals in these households
    individuals_in_households = pd.merge(
        portad,
        households_both[["folio"]],
        on="folio",
        how="inner"
    )
    
    # Filter individuals older than overall average age in these households
    # First, compute overall average age among these individuals
    avg_age = individuals_in_households["edad"].mean()
    
    # Select individuals older than this average
    older_individuals = individuals_in_households[individuals_in_households["edad"] > avg_age]
    
    # For each individual, get household ID, state, age, and total incident count (vlh18a)
    result = older_individuals[["folio", "ent", "edad", "vlh18a"]]
    
    # Merge to get 'ent' (state) from portad
    result = pd.merge(result, portad[["folio", "ent"]], on="folio", how="left")
    
    # Rename columns for clarity
    result = result.rename(columns={"ent": "state", "edad": "age", "vlh18a": "incident_count"})
    
    # Sort from oldest to youngest
    result = result.sort_values(by="age", ascending=False).reset_index(drop=True)
    
    return result