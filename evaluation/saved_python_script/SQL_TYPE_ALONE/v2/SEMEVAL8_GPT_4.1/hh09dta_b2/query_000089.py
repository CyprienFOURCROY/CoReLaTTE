def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_ah = tables["ii_ah"]

    # 1. Households that own a motor vehicle (ah03d == 1)
    df_ah_mv = df_ah[df_ah["ah03d"] == 1.0][["folio", "ls"]]

    # 2. Individuals aged 25 or older
    df_portad_25 = df_portad[df_portad["edad"] >= 25][["folio", "ls", "edad"]]

    # 3. Merge to get individuals aged 25+ in households that own a motor vehicle
    df_indiv = df_portad_25.merge(df_ah_mv, on=["folio", "ls"], how="inner")

    # 4. Merge with crh to get debt payment info (on folio)
    df_crh_pay = df_crh[["folio", "crh03_1", "crh03_2"]]
    df_indiv_crh = df_indiv.merge(df_crh_pay, on="folio", how="left")

    # 5. Compute overall average household amount paid (crh03_2) among households with a recorded value (>0)
    # Only consider rows where crh03_2 is not null and >0
    df_crh_valid = df_crh[(~df_crh["crh03_2"].isna()) & (df_crh["crh03_2"] > 0)]
    overall_avg_paid = df_crh_valid["crh03_2"].mean()

    # 6. For each individual, check if their household reported a positive amount paid on debts in the last 12 months (crh03_2 > 0)
    # and that amount exceeds the overall average
    mask_paid = (df_indiv_crh["crh03_2"] > overall_avg_paid)

    # 7. Compute average age for those individuals
    avg_age = df_indiv_crh.loc[mask_paid, "edad"].mean()

    return pd.DataFrame({"average_age": [avg_age]})