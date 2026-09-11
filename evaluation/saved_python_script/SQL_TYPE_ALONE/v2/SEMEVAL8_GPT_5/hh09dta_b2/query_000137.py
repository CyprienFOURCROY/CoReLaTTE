import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_crh = tables["ii_crh"][["folio", "crh02_1", "crh02_2"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh18a"]].copy()

    # Households that reported a pesos amount owed on credit/loans (explicit value provided)
    owed = df_crh[(df_crh["crh02_1"] == 1.0) & (df_crh["crh02_2"].notna())][["folio", "crh02_2"]]

    # Average incidents since 2005 among households with any such robberies (>0)
    with_any_robberies = df_vlh[df_vlh["vlh18a"] > 0]
    avg_incidents = with_any_robberies["vlh18a"].mean()

    # Merge and filter those with incidents greater than the computed average
    merged = owed.merge(df_vlh, on="folio", how="left")
    result = merged[(merged["vlh18a"].notna()) & (merged["vlh18a"] > avg_incidents)].copy()

    result = result[["folio", "vlh18a", "crh02_2"]].rename(
        columns={
            "folio": "Household ID",
            "vlh18a": "Incidents since 2005",
            "crh02_2": "Owed amount (pesos)"
        }
    ).reset_index(drop=True)

    return result