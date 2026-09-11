def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    se = tables["ii_se"]
    nna = tables["ii_nna"]
    crh = tables["ii_crh"]
    
    # Filter households that reported a death in last 5 years and provided a value for total debts+interests
    # Conditions:
    # - se01a == 1 (household had a death in last 5 years)
    # - crh04_1 != 8 (has a value for total debts + interests)
    # - crh04_1 is not null
    # - crh04_2 is not null
    
    # Filter se for households with death
    se_death = se[se["se01a"] == 1]
    
    # Filter crh for households with debt info
    crh_debt = crh[(crh["crh04_1"] != 8) & (crh["crh04_1"].notnull()) & (crh["crh04_2"].notnull())]
    
    # Merge to get households with death and debt info
    households = pd.merge(se_death[["folio"]], crh_debt[["folio"]], on="folio", how="inner")
    
    # Merge with portad to get state info
    households = pd.merge(households, portad[["folio", "ent"]], on="folio", how="left")
    
    # Merge with portad to get individual ages
    # First, get all individuals in these households
    individuals = pd.merge(portad[["folio", "ls", "edad"]], households, on="folio", how="inner")
    
    # Filter individuals aged 60 or older
    seniors = individuals[individuals["edad"] >= 60]
    
    # For each household, check if at least one senior exists
    household_seniors = seniors.groupby("folio").size().reset_index(name="senior_count")
    households_with_senior = pd.merge(households, household_seniors[["folio"]], on="folio", how="left")
    households_with_senior["has_senior"] = households_with_senior["folio"].isin(household_seniors["folio"])
    
    # Merge with ent to get state info
    households_with_senior = pd.merge(households_with_senior, portad[["folio", "ent"]], on="folio", how="left")
    
    # Group by state and compute counts
    result = (
        households_with_senior
        .groupby("ent")
        .agg(
            households_with_senior_count=pd.NamedAgg(column="folio", aggfunc="nunique"),
            households_with_senior_with_age=pd.NamedAgg(column="has_senior", aggfunc=lambda x: x.sum())
        )
        .reset_index()
    )
    
    # Rename columns for clarity
    result = result.rename(columns={
        "ent": "state_code",
        "households_with_senior_count": "total_households",
        "households_with_senior_with_age": "households_with_age_60_or_older"
    })
    
    return result