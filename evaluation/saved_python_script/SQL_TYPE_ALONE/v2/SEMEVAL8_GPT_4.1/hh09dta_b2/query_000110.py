def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_se = tables["ii_se"]
    df_in = tables["ii_in"]

    # 1. Households that use a plot/land for farming (su01 == 1)
    su_plot = df_su[df_su["su01"] == 1]

    # 2. Households that experienced a total crop loss in last 5 years (se01e == 1)
    se_crop_loss = df_se[df_se["se01e"] == 1]

    # 3. Households with NO members participating in any Other Government Program (in01a10_1 == 3 for all members in household)
    # First, for each household, check if all in01a10_1 == 3 (or nan, which means not participating)
    in_other_gov = df_in[["folio", "in01a10_1"]].copy()
    # Only keep rows where in01a10_1 is not nan
    in_other_gov_notna = in_other_gov[~in_other_gov["in01a10_1"].isna()]
    # For each household, check if all in01a10_1 == 3
    folios_all_3 = (
        in_other_gov_notna.groupby("folio")["in01a10_1"]
        .apply(lambda x: (x == 3).all())
    )
    # Also, if a household has no rows (all nan), treat as not participating (so include them)
    all_folios = set(df_in["folio"].unique())
    folios_with_rows = set(folios_all_3.index)
    folios_no_rows = all_folios - folios_with_rows
    # Combine folios where all == 3 and folios with no rows
    eligible_folios = set(folios_all_3[folios_all_3].index).union(folios_no_rows)

    # 4. Intersect all three conditions
    eligible_folios = eligible_folios & set(su_plot["folio"]) & set(se_crop_loss["folio"])

    # 5. For these households, get expense in chemical fertilizer (su231)
    su_filtered = su_plot[su_plot["folio"].isin(eligible_folios)]
    # Group by folio, sum su231 (in case of multiple rows per household)
    fert_expense = su_filtered.groupby("folio", as_index=False)["su231"].sum()

    # 6. For these households, count number of adults (age >= 18) from ii_portad
    portad_adults = df_portad[df_portad["edad"] >= 18]
    adults_count = portad_adults[portad_adults["folio"].isin(eligible_folios)].groupby("folio").size().reset_index(name="num_adults")

    # 7. Merge expense and adult count
    merged = fert_expense.merge(adults_count, on="folio", how="inner")

    # 8. Group by num_adults, calculate average expense and count of households
    result = (
        merged.groupby("num_adults")
        .agg(
            avg_expense_chemical_fertilizer=("su231", "mean"),
            household_count=("folio", "count")
        )
        .reset_index()
        .sort_values("num_adults")
    )

    return result