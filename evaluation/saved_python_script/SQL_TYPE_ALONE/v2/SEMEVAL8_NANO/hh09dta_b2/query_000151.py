def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Filter households with at least one break-in/robbery since 2005
    # Conditions:
    # - vlh12a: entered force rob in HH since 2005? == 1
    # - or vlh12a_b: entered force rob in HH since 2005? == 2
    # - or vlh12a_c: no force rob since 2005? == 3
    # - or vlh12b: entered force rob in HH since 2005? == 2
    # - or vlh12c: no force rob since 2005? == 3
    # - or vlh14a: entered force rob in business since 2005? == 1
    # - or vlh16a: entered force rob parcel since 2005? == 1
    # - or vlh17a: number of times entered/rob parcel since 2005 > 0
    # - or vlh13a: number of times robbed in HH since 2005 > 0
    # - or vlh13: total times robbed in HH since 2005 > 0
    # - or vlh14: entered force rob in business since 2005? == 1
    # - or vlh16: entered force rob parcel since 2005? == 1
    # - or vlh17: number of times entered/rob parcel since 2005 > 0
    # - or vlh18a: total times entered rob house/business/parcel since 2005 > 0
    
    # Create a boolean mask for households with at least one incident since 2005
    incident_mask = (
        (vlh["vlh12a"] == 1) |
        (vlh["vlh12a_b"] == 2) |
        (vlh["vlh12a_c"] == 3) |
        (vlh["vlh12b"] == 2) |
        (vlh["vlh12c"] == 3) |
        (vlh["vlh14a"] == 1) |
        (vlh["vlh16a"] == 1) |
        (vlh["vlh17a"] > 0) |
        (vlh["vlh13a"] > 0) |
        (vlh["vlh13"] > 0) |
        (vlh["vlh14"] == 1) |
        (vlh["vlh16"] == 1) |
        (vlh["vlh17"] > 0) |
        (vlh["vlh18a"] > 0)
    )
    
    households_with_incidents = vlh[incident_mask][["folio"]].drop_duplicates()
    
    # Filter households with at least 30 such households
    if len(households_with_incidents) < 30:
        return pd.DataFrame(
            {"state": [], "average_incidents": [], "household_count": []}
        )
    
    # Merge with portad to get state info
    households_with_incidents = households_with_incidents.merge(portad, on="folio", how="left")
    
    # Filter households with at least 30 households per state
    state_counts = households_with_incidents.groupby("ent").size()
    valid_states = state_counts[state_counts >= 30].index
    households_valid_states = households_with_incidents[households_with_incidents["ent"].isin(valid_states)]
    
    # For each household, count number of incidents since 2005
    # Count incidents based on the same conditions
    incidents_counts = (
        (vlh.set_index("folio").loc[households_valid_states["folio"]]
         .assign(
             incident_count=lambda df: (
                 (df["vlh12a"] == 1).astype(int) +
                 (df["vlh12a_b"] == 2).astype(int) +
                 (df["vlh12a_c"] == 3).astype(int) +
                 (df["vlh12b"] == 2).astype(int) +
                 (df["vlh12c"] == 3).astype(int) +
                 (df["vlh14a"] == 1).astype(int) +
                 (df["vlh16a"] == 1).astype(int) +
                 (df["vlh17a"] > 0).astype(int) +
                 (df["vlh13a"] > 0).astype(int) +
                 (df["vlh13"] > 0).astype(int) +
                 (df["vlh14"] == 1).astype(int) +
                 (df["vlh16"] == 1).astype(int) +
                 (df["vlh17"] > 0).astype(int) +
                 (df["vlh18a"] > 0).astype(int)
             )
         )
        )["incident_count"]
    )
    
    # Aggregate by state
    incident_data = (
        households_valid_states
        .assign(
            incident_count=lambda df: (
                (vlh.set_index("folio").loc[df["folio"]]
                 .assign(
                     incident_count=lambda d: (
                         (d["vlh12a"] == 1).astype(int) +
                         (d["vlh12a_b"] == 2).astype(int) +
                         (d["vlh12a_c"] == 3).astype(int) +
                         (d["vlh12b"] == 2).astype(int) +
                         (d["vlh12c"] == 3).astype(int) +
                         (d["vlh14a"] == 1).astype(int) +
                         (d["vlh16a"] == 1).astype(int) +
                         (d["vlh17a"] > 0).astype(int) +
                         (d["vlh13a"] > 0).astype(int) +
                         (d["vlh13"] > 0).astype(int) +
                         (d["vlh14"] == 1).astype(int) +
                         (d["vlh16"] == 1).astype(int) +
                         (d["vlh17"] > 0).astype(int) +
                         (d["vlh18a"] > 0).astype(int)
                     )
                 )
                )["incident_count"]
            )
        )
        .groupby("ent")
        .agg(
            household_count=("folio", "nunique"),
            total_incidents=("incident_count", "sum")
        )
        .reset_index()
    )
    
    # Calculate average incidents per household
    incident_data["average_incidents"] = incident_data["total_incidents"] / incident_data["household_count"]
    
    # Get national average
    total_households = incident_data["household_count"].sum()
    total_incidents = incident_data["total_incidents"].sum()
    national_avg = total_incidents / total_households if total_households > 0 else 0
    
    # Filter states with average > national average
    result = incident_data[incident_data["average_incidents"] > national_avg]
    
    # Sort by average descending
    result = result.sort_values(by="average_incidents", ascending=False)
    
    # Select relevant columns
    result = result[["ent", "average_incidents", "household_count"]]
    
    # Map state codes to labels if needed (optional, not required)
    # For clarity, include state code as 'state'
    result = result.rename(columns={"ent": "state"})
    
    return result