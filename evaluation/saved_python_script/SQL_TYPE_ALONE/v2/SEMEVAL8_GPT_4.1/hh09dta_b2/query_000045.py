def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]

    # 1. Households with at least one member aged 60 or older
    hh_with_60plus = df_portad[df_portad["edad"] >= 60]["folio"].unique()

    # 2. Households that reported a household member’s death in the last five years
    # se01a == 1 means "Yes" to "dead HHM in last 5 years"
    hh_with_death = df_se[df_se["se01a"] == 1]["folio"].unique()

    # 3. For each household, sum the value of washing machine/stove assets (ah04f_2) across all members
    # Only consider ah04f_1 == 1 (knows value)
    df_ah_valid = df_ah[df_ah["ah04f_1"] == 1]
    hh_washstove_sum = df_ah_valid.groupby("folio")["ah04f_2"].sum(min_count=1)

    # 4. Compute the overall average of total household washing machine/stove asset value
    overall_avg = hh_washstove_sum.mean()

    # 5. Households with total value above the overall average
    hh_above_avg = hh_washstove_sum[hh_washstove_sum > overall_avg].index

    # 6. Intersection: households meeting all three criteria
    eligible_hh = set(hh_with_60plus) & set(hh_with_death) & set(hh_above_avg)

    # 7. Return the count as a one-row DataFrame
    return pd.DataFrame({"household_count": [len(eligible_hh)]})