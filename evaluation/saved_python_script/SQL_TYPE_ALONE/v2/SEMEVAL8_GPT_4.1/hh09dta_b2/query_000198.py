def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # 2. Households with at least one member who owns an electronic device (ah03e == 1)
    # Merge to get only Oaxaca individuals
    df_ah_oaxaca = df_ah.merge(oaxaca_households, on="folio", how="inner")
    owns_electronic = df_ah_oaxaca[df_ah_oaxaca["ah03e"] == 1.0][["folio"]].drop_duplicates()

    # 3. For these households, get non-ag business ownership (nna01: 1=Yes, 2=No)
    # There may be multiple rows per household in ii_nna, but nna01 is at household level
    nna_oaxaca = df_nna.merge(owns_electronic, on="folio", how="inner")

    # For each household, take the first non-null nna01 (should be the same for all rows per household)
    nna_status = nna_oaxaca.groupby("folio")["nna01"].first().reset_index()

    # Count households by nna01 (1=Yes, 2=No)
    counts = nna_status["nna01"].value_counts(dropna=False).sort_index()

    # Prepare output: map 1.0->"Owns/shares non-ag business", 2.0->"Does not own/share non-ag business"
    mapping = {1.0: "Owns/shares non-ag business", 2.0: "Does not own/share non-ag business"}
    result = (
        counts.rename(index=mapping)
        .reset_index()
        .rename(columns={"index": "non_ag_business_ownership", "nna01": "num_households"})
    )

    return result