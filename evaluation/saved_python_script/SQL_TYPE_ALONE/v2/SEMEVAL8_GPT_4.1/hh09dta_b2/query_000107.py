def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Step 1: Find households with at least one member aged 65+
    aged_65plus = df_portad[df_portad["edad"] >= 65.0][["folio"]].drop_duplicates()

    # Step 2: Households that participated in 70 y más and received a positive direct payment
    # in01a11_1 == 1: Participates and received income
    # in02a11: Amount received directly 70 y más
    df_in_70ymas = df_in[
        (df_in["in01a11_1"] == 1.0) &
        (df_in["in02a11"].notna()) &
        (df_in["in02a11"] > 0)
    ][["folio", "in02a11", "in03a"]]

    # Step 3: Merge with aged_65plus to ensure at least one member 65+
    df_eligible = df_in_70ymas.merge(aged_65plus, on="folio", how="inner")

    # Step 4: Filter to those who received Liconsa milk in last 12 months (in03a == 1)
    df_liconsa = df_eligible[df_eligible["in03a"] == 1.0]

    # Step 5: Compute average 70 y más amount among those who received Liconsa milk
    avg_70ymas_liconsa = df_liconsa["in02a11"].mean()

    # Step 6: Select those with 70 y más amount > average, among those who received Liconsa milk
    df_above_avg = df_liconsa[df_liconsa["in02a11"] > avg_70ymas_liconsa]

    # Step 7: Prepare output: household IDs and amounts, sorted from highest to lowest
    result = df_above_avg[["folio", "in02a11"]].sort_values("in02a11", ascending=False).reset_index(drop=True)
    result = result.rename(columns={"folio": "household_id", "in02a11": "70ymas_amount"})
    return result