def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Adults only
    df_adults = df_portad[df_portad["edad"] >= 18]

    # Households that use a plot/land for farming (su01 == 1)
    df_su_farm = df_su[df_su["su01"] == 1]

    # Households with positive total debt (crh04_2 > 0)
    df_crh_debt = df_crh[(df_crh["crh04_2"].notna()) & (df_crh["crh04_2"] > 0)]

    # Merge: adults with farming households
    df1 = df_adults.merge(df_su_farm[["folio"]], on="folio", how="inner")

    # Merge: with households with positive debt
    df2 = df1.merge(df_crh_debt[["folio", "crh04_2"]], on="folio", how="inner")

    # Group by state, aggregate average household debt and count of adult records
    result = (
        df2.groupby("ent")
        .agg(
            average_household_debt=("crh04_2", "mean"),
            num_adult_records=("folio", "count")
        )
        .reset_index()
    )

    # Get top 10 states by average household debt
    result = result.sort_values("average_household_debt", ascending=False).head(10)

    # Convert ent to int for clarity
    result["ent"] = result["ent"].astype(int)

    # Reorder columns
    result = result[["ent", "average_household_debt", "num_adult_records"]]

    return result