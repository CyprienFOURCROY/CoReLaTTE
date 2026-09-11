def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # Households with a pesos amount owed on credit/loans in the last 12 months
    # crh02_1 == 1 means "Value", and crh02_2 is the amount (not null)
    df_crh_amt = df_crh[(df_crh["crh02_1"] == 1) & (df_crh["crh02_2"].notnull())]

    # Households with any robberies since 2005 (vlh18a > 0)
    df_vlh_rob = df_vlh[df_vlh["vlh18a"].notnull() & (df_vlh["vlh18a"] > 0)]

    # Compute average number of robberies since 2005 among households with any such robberies
    avg_robberies = df_vlh_rob["vlh18a"].mean()

    # Merge to get only households that meet both criteria
    merged = df_crh_amt.merge(df_vlh, on="folio", how="inner")

    # Filter: vlh18a > avg_robberies
    result = merged[(merged["vlh18a"].notnull()) & (merged["vlh18a"] > avg_robberies)]

    # Select required columns
    out = result[["folio", "vlh18a", "crh02_2"]].rename(
        columns={"folio": "Household ID", "vlh18a": "incident_count", "crh02_2": "owed_amount"}
    ).reset_index(drop=True)

    return out