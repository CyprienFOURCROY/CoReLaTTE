def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    in_table = tables["ii_in"]
    nna = tables["ii_nna"]
    
    # Filter households in Oaxaca (ent == 20)
    oaxaca_households = portad[portad["ent"] == 20]
    
    # Filter households that own or share a non-agricultural business (nna01 == 1)
    nna_owned = nna[nna["nna01"] == 1]
    
    # Merge to get households in Oaxaca with non-ag business owners/sharers
    households_with_nna = pd.merge(
        oaxaca_households,
        nna_owned,
        on="folio",
        how="inner"
    )
    
    # Get the list of relevant household folios
    relevant_folios = households_with_nna["folio"].unique()
    
    # Filter in_table for these households
    in_filtered = in_table[in_table["folio"].isin(relevant_folios)]
    
    # Filter for individuals with Result Interview == 20
    individuals_A = in_filtered[in_filtered["rel"] == 20]
    
    # Calculate overall average age of individuals with rel == 20 in these households
    overall_avg_age = individuals_A["edad"].mean()
    
    # For individuals B: in the same households, age > overall_avg_age
    individuals_B = in_filtered[
        (in_filtered["folio"].isin(relevant_folios)) &
        (in_filtered["edad"] > overall_avg_age)
    ]
    
    # Count pairs (A, B) where A's rel == 20 and B's age > overall average
    count_pairs = len(individuals_A) * len(individuals_B)
    
    # Return the count as a DataFrame
    return pd.DataFrame({"pair_count": [count_pairs]})