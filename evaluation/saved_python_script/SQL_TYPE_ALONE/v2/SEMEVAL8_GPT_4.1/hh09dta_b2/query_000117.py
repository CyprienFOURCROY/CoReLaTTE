def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]

    # Households where at least one member owns/shares a non-ag business (nna01 == 1)
    nna_yes_folios = df_nna[df_nna["nna01"] == 1.0]["folio"].unique()
    # Households where at least one member does NOT own/share a non-ag business (nna01 == 2)
    nna_no_folios = df_nna[df_nna["nna01"] == 2.0]["folio"].unique()

    # Get individuals in households where at least one member does NOT own/share a non-ag business
    df_no = df_portad[df_portad["folio"].isin(nna_no_folios)]
    avg_age_no = df_no["edad"].mean()

    # Get individuals in households where at least one member owns/shares a non-ag business
    df_yes = df_portad[df_portad["folio"].isin(nna_yes_folios)]

    # Select those individuals older than the average age in "no" households
    df_result = df_yes[df_yes["edad"] > avg_age_no][["folio", "ls", "edad"]].reset_index(drop=True)

    return df_result