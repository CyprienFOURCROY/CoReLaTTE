def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_in = tables["ii_in"]
    df_su = tables["ii_su"]

    # Filter households that use a plot/land for farming
    households_with_plot = df_su[df_su["su01"] == 1]["folio"]

    # Filter households that own/share a non-agricultural business
    nna_shares = df_nna[df_nna["nna01"] == 1]["folio"]

    # Households that satisfy both conditions
    households_farming_and_business = pd.Series(
        list(set(households_with_plot) & set(nna_shares))
    )

    # Filter households that have chemical fertilizer expenses (su231)
    df_fertilizer = df_su[
        df_su["folio"].isin(households_farming_and_business)
    ][["folio", "su231"]]

    # Filter households that do NOT use a plot (for pesticide comparison)
    households_no_plot = df_su[df_su["su01"] != 1]["folio"]
    df_no_plot = df_su[
        df_su["folio"].isin(households_no_plot)
    ][["folio", "su233"]]

    # Calculate average pesticide expense among households that do not use a plot
    avg_pesticide_expense = df_no_plot["su233"].mean()

    # Filter households with fertilizer expense exceeding the average pesticide expense
    df_result = df_fertilizer[
        df_fertilizer["su231"] > avg_pesticide_expense
    ][["folio", "su231"]]

    # Sort by fertilizer expense descending
    df_result_sorted = df_result.sort_values(by="su231", ascending=False).reset_index(drop=True)

    return df_result_sorted