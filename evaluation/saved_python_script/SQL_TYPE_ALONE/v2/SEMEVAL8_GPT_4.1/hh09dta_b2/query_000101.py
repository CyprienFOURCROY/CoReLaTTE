def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]

    # Households that own/share a non-ag business (nna01 == 1)
    df_nna_filt = df_nna[df_nna["nna01"] == 1]

    # Households that do NOT use any plot/land for farming (su01 == 3)
    df_su_filt = df_su[df_su["su01"] == 3]

    # Merge on folio to get intersection
    df_merge = df_nna_filt.merge(df_su_filt[["folio"]], on="folio", how="inner")

    # Merge with portad to get state info
    df_merge = df_merge.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Only keep rows with nna02 not null (number of non-ag businesses)
    df_merge = df_merge[~df_merge["nna02"].isna()]

    # Group by state, calculate average and count
    grouped = df_merge.groupby("ent").agg(
        avg_nna02=("nna02", "mean"),
        num_households=("folio", "nunique")
    ).reset_index()

    # Only states with average >= 1.5
    result = grouped[grouped["avg_nna02"] >= 1.5].copy()

    # Rename columns for clarity
    result = result.rename(columns={
        "ent": "state",
        "avg_nna02": "average_non_ag_businesses_last_12m",
        "num_households": "num_households"
    })

    # Sort by state for consistency
    result = result.sort_values("state").reset_index(drop=True)

    return result[["state", "average_non_ag_businesses_last_12m", "num_households"]]