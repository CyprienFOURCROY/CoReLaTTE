def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    portad = tables["ii_portad"]
    vlh = tables["ii_vlh"]
    se = tables["ii_se"]
    ah = tables["ii_ah"]
    
    # Filter households in Oaxaca (ent == 15) with at least one adult (edad >= 18)
    # and with household member's death in last five years (se01a == 1)
    # Merge portad with se on 'folio'
    portad_oax = portad[portad["ent"] == 15]
    se_oax = se[se["se01a"] == 1]
    households_with_death = portad_oax.merge(se_oax[["folio"]], on="folio", how="inner")
    
    # Filter households where at least one adult (edad >= 18)
    # Since 'edad' is per individual, we need to identify households with at least one adult
    # Merge with portad to get 'folio' and 'edad'
    # Group by 'folio' to check if any 'edad' >= 18
    adults = portad[portad["folio"].isin(households_with_death["folio"])]
    adults_in_households = adults.groupby("folio")["edad"].max().reset_index()
    households_with_adult = adults_in_households[adults_in_households["edad"] >= 18]["folio"]
    
    # Final households: in Oaxaca, with at least one adult, and with household death in last 5 years
    final_households = households_with_death[households_with_death["folio"].isin(households_with_adult)]
    
    # Filter vlh for these households
    vlh_filtered = vlh[vlh["folio"].isin(final_households["folio"])]
    
    # For each household, determine if any member owns an electronic device (ah04e_1 == 1)
    ah_filtered = tables["ii_ah"]
    ah_households = ah_filtered[ah_filtered["folio"].isin(final_households["folio"])]
    ah_ownership = ah_households.groupby("folio")["ah04e_1"].max().reset_index()
    ah_ownership["has_electronic"] = ah_ownership["ah04e_1"] == 1
    
    # Merge with vlh to get 'vlh12a' (times robbed since 2005)
    vlh_merged = vlh_filtered.merge(ah_ownership[["folio", "has_electronic"]], on="folio", how="inner")
    
    # Compute overall average of 'vlh12a' for these households
    overall_avg = vlh_merged["vlh12a"].mean()
    
    # Group households by electronic ownership status
    group_electronic = vlh_merged[vlh_merged["has_electronic"]]
    group_none = vlh_merged[~vlh_merged["has_electronic"]]
    
    # Calculate mean 'vlh12a' for each group
    mean_electronic = group_electronic["vlh12a"].mean()
    mean_none = group_none["vlh12a"].mean()
    
    # Count households in each group
    count_electronic = group_electronic["folio"].nunique()
    count_none = group_none["folio"].nunique()
    
    # Determine which group has mean >= overall average
    result_group = None
    if mean_electronic >= overall_avg:
        result_group = ("Electronic", count_electronic)
    if mean_none >= overall_avg:
        # If both qualify, include both
        if result_group is None:
            result_group = ("None", count_none)
        else:
            # Both qualify, prepare both
            # But since the question asks for "which group" (singular), interpret as all qualifying groups
            # So prepare a DataFrame with both
            data = []
            if mean_electronic >= overall_avg:
                data.append({"group": "Electronic", "households": count_electronic})
            if mean_none >= overall_avg:
                data.append({"group": "None", "households": count_none})
            return pd.DataFrame(data)
    else:
        # Only one group qualifies
        if result_group is not None:
            return pd.DataFrame([{"group": result_group[0], "households": result_group[1]}])
        else:
            # No group qualifies
            return pd.DataFrame([{"group": "None", "households": 0}])
    
    # If only one group qualifies
    return pd.DataFrame([{"group": result_group[0], "households": result_group[1]}])