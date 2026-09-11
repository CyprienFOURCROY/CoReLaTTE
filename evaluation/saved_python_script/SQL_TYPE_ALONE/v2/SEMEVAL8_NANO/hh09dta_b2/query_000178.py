def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    su = tables["ii_su"]
    nna = tables["ii_nna"]
    vlh = tables["ii_vlh"]
    
    # Filter households in Oaxaca (ent == 15) with at least one adult (edad >= 18)
    oaxaca_households = portad[
        (portad["ent"] == 15) & (portad["edad"] >= 18)
    ][["folio"]].drop_duplicates()

    # Filter households that own or share a non-agricultural business (nna01 == 1)
    nna_owned = nna[nna["nna01"] == 1][["folio"]]
    
    # Merge to get households in Oaxaca with non-ag business ownership
    oaxaca_nna = pd.merge(oaxaca_households, nna_owned, on="folio", how="inner")
    
    # Merge with vlh to get data on robberies/entries since 2005
    vlh_filtered = pd.merge(oaxaca_nna, vlh, on="folio", how="inner")
    
    # Filter households where total times robbed/entered since 2005 (vlh18a) is at or above the Oaxaca average
    # First, compute the Oaxaca statewide average of vlh18a
    oaxaca_avg = vlh_filtered["vlh18a"].mean()
    
    # Keep households with vlh18a >= Oaxaca average
    households_above_avg = vlh_filtered[vlh_filtered["vlh18a"] >= oaxaca_avg]
    
    # Compute the average number of times since 2005 that their house, business, or parcel was entered or robbed (vlh18a)
    result_value = households_above_avg["vlh18a"].mean()
    
    # Return as DataFrame
    return pd.DataFrame(
        {"average_times_since_2005": [result_value]}
    )