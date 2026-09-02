def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    nna = tables["ii_nna"]
    ah = tables["ii_ah"]
    
    # Filter households where at least one member owns electronic device and washing machine/stove
    ah_filtered = ah[
        (ah["ah04e_1"] == 1) | (ah["ah04e_2"] == 1)
    ].copy()
    ah_filtered = ah_filtered[
        (ah_filtered["ah04f_1"] == 1) | (ah_filtered["ah04f_2"] == 1)
    ]
    
    # Get household IDs with at least one member owning electronic device and washing machine/stove
    households_with_electro_and_wash = ah_filtered["folio"].unique()
    
    # Filter households where at least one member owns or shares a non-agricultural business
    nna_filtered = nna[
        (nna["nna01"] == 1)
    ]["folio"].unique()
    
    # Find households satisfying all conditions
    households_meet_conditions = set(households_with_electro_and_wash).intersection(nna_filtered)
    
    # Filter portad for these households
    portad_filtered = portad[portad["folio"].isin(households_meet_conditions)]
    
    # Filter for adults (edad >= 18)
    adults = portad_filtered[portad_filtered["edad"] >= 18]
    
    # Group by ent (state) and compute mean age and count
    result = (
        adults.groupby("ent")
        .agg(
            average_age=pd.NamedAgg(column="edad", aggfunc="mean"),
            adults_count=pd.NamedAgg(column="folio", aggfunc="count")
        )
        .reset_index()
    )
    
    # Map state codes to state names (optional, not required for output)
    # Select top 10 states with highest average age
    top10 = (
        result.sort_values(by="average_age", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    
    return top10