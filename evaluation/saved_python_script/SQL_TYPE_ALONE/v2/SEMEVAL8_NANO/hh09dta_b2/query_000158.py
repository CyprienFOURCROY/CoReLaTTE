def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    in_table = tables["ii_in"]
    vlh = tables["ii_vlh"]
    inr = tables["ii_inr"]
    
    # Filter households with at least one adult (edad >= 18)
    adults = portad[portad["edad"] >= 18]
    households_with_adults = adults["folio"].unique()
    
    # Filter households that have at least one member reporting feeling very safe or safe at home
    safe_mask = vlh[vlh["vlh04"].isin([1, 2])]
    safe_households = safe_mask["folio"].unique()
    
    # Filter households that have at least one member with positive income from "Other Government Program"
    # "in01a10_1" indicates participation and receipt, "in02a10" indicates direct amount received
    in_participation = in_table[
        (in_table["in01a10_1"].isin([1, 2])) &  # Participates in last 12 months
        (in_table["in02a10"] > 0)  # Positive amount received
    ]
    households_with_income = in_participation["folio"].unique()
    
    # Find households that satisfy all three conditions
    target_households = set(households_with_adults) & set(safe_households) & set(households_with_income)
    
    # Count the number of such households
    count = len(target_households)
    
    return pd.DataFrame({"households_count": [count]})