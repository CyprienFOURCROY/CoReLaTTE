def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # Households that incurred debts in the last 12 months: crh02_1 == 1
    # Households that did NOT incur debts in the last 12 months: crh02_1 == 2
    # Experienced at least one robbery/forced entry since 2005: 
    # (vlh12a_a == 1) or (vlh12a_b == 2) or (vlh14a == 1) or (vlh16a == 1)
    # (any of these columns == their respective value)

    # Merge on folio
    df = pd.merge(df_crh, df_vlh, on="folio", how="inner")

    # Robbery/forced entry since 2005
    rob_mask = (
        (df["vlh12a_a"] == 1) |
        (df["vlh12a_b"] == 2) |
        (df["vlh14a"] == 1) |
        (df["vlh16a"] == 1)
    )

    # Households that incurred debts in the last 12 months and experienced robbery/forced entry since 2005
    mask_debt_rob = (df["crh02_1"] == 1) & rob_mask

    # Households that did NOT incur debts in the last 12 months
    mask_no_debt = (df["crh02_1"] == 2)

    # "People in their locality do favors for each other": vlh01t
    # 1: Never, 2: Rarely, 3: Frequently, 4: Always, 8: DK
    # Exclude DK (8)
    df_valid = df[df["vlh01t"].isin([1,2,3,4])]

    # Average for households that did NOT incur debts in the last 12 months
    avg_no_debt = df_valid[mask_no_debt]["vlh01t"].mean()

    # Households that incurred debts in the last 12 months and experienced robbery/forced entry since 2005
    df_debt_rob = df_valid[mask_debt_rob]

    # Households in this group that report vlh01t > avg_no_debt
    count = (df_debt_rob["vlh01t"] > avg_no_debt).sum()

    return pd.DataFrame({"households_above_avg": [int(count)]})