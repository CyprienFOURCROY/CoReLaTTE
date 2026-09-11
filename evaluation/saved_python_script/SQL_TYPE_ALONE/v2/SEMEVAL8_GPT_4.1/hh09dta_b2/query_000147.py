def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]

    # Households that use a plot/land for farming (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1.0][["folio", "su231", "su233"]]

    # Households that do NOT use a plot/land for farming (su01 != 1)
    su_no_plot = df_su[df_su["su01"] != 1.0][["folio", "su233"]]

    # Households that own/share a non-ag business (nna01 == 1)
    nna_nonag = df_nna[df_nna["nna01"] == 1.0][["folio"]]

    # Merge to get households that use a plot and own/share a non-ag business
    merged = su_plot.merge(nna_nonag, on="folio", how="inner")

    # Calculate average pesticide expense (su233) for households that do NOT use a plot
    avg_pesticide_no_plot = su_no_plot["su233"].mean(skipna=True)

    # Filter: chemical fertilizer expense (su231) > avg_pesticide_no_plot
    filtered = merged[(merged["su231"] > avg_pesticide_no_plot) & (~merged["su231"].isna())]

    # Sort by fertilizer expense descending
    filtered_sorted = filtered.sort_values("su231", ascending=False)

    # Return only Household ID and fertilizer expense
    result = filtered_sorted[["folio", "su231"]].rename(columns={"su231": "fertilizer_expense"})

    return result.reset_index(drop=True)