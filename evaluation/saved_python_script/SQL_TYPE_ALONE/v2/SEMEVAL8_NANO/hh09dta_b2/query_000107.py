def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_su = tables["ii_su"]

    # Filter households with at least one member aged 65+ who participated in "70 y más" program and received positive direct payment
    # Step 1: Filter in_in for "in01a11_1" == 1 (participated and received income) and "in03b" == 1 (received Pronjag)
    in_70_plus = df_in[(df_in["in01a11_1"] == 1) & (df_in["in03b"] == 1)]
    households_70_plus = in_70_plus["folio"].unique()

    # Step 2: Filter portad for these households
    portad_filtered = df_portad[df_portad["folio"].isin(households_70_plus)]

    # Step 3: For these households, check if any member aged 65+ participated in "70 y más" program and received income
    # Since "rel" indicates result interview, and "edad" is age, filter for age >=65
    portad_65_plus = portad_filtered[portad_filtered["edad"] >= 65]

    # Get household IDs with at least one member aged 65+ in portad_65_plus
    households_with_65_plus = portad_65_plus["folio"].unique()

    # Filter in_in for these households
    in_filtered = df_in[df_in["folio"].isin(households_with_65_plus)]

    # Step 4: Filter for those who participated in "70 y más" and received income (in01a11_1 == 1)
    households_70_plus_participated = in_filtered[in_filtered["in01a11_1"] == 1]["folio"].unique()

    # Step 5: Among these, find households with positive "in02a11" (amount received directly for 70 y más)
    households_positive_70_mas = in_filtered[
        (in_filtered["folio"].isin(households_70_plus_participated)) &
        (in_filtered["in02a11"] > 0)
    ][["folio", "in02a11"]]

    # Step 6: Compute average "in02a11" among households that also received Liconsa milk ("in03a" == 1)
    in_liconsa = in_filtered[in_filtered["in03a"] == 1]
    # For households with "in02a11" > 0
    in_liconsa_positive = in_liconsa[in_liconsa["in02a11"] > 0]
    avg_in02a11_liconsa = in_liconsa_positive["in02a11"].mean()

    # Step 7: Filter households with "in02a11" > average among those that received Liconsa
    households_exceed_avg = households_positive_70_mas[
        households_positive_70_mas["in02a11"] > avg_in02a11_liconsa
    ]

    # Step 8: Sort by "in02a11" descending
    result = households_exceed_avg.sort_values(by="in02a11", ascending=False)

    # Return DataFrame with household ID and amount
    return result.reset_index(drop=True)