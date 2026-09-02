def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]

    # 1. Oaxaca households (ent == 20)
    oaxaca_hh = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # 2. At least one adult (edad >= 18)
    adults = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)]
    hh_with_adult = adults["folio"].unique()

    # 3. At least one member owns/shares non-ag business (nna01 == 1)
    nna_oaxaca = df_nna[df_nna["folio"].isin(oaxaca_hh["folio"])]
    hh_with_nonag = nna_oaxaca[nna_oaxaca["nna01"] == 1.0]["folio"].unique()

    # 4. Households with both at least one adult and a member with non-ag business
    eligible_hh = set(hh_with_adult) & set(hh_with_nonag)

    # 5. Credit/loans in last 12 months: owed AND paid
    crh = df_crh[df_crh["folio"].isin(eligible_hh)].copy()
    # Owed: crh02_1 == 1 (has value, i.e., incurred debts)
    # Paid: crh03_1 == 1 (has value, i.e., paid something)
    crh = crh[(crh["crh02_1"] == 1.0) & (crh["crh03_1"] == 1.0)]
    # Amounts
    crh = crh[["folio", "crh02_2", "crh03_2"]].copy()
    crh = crh.rename(columns={"crh02_2": "amount_owed", "crh03_2": "amount_paid"})
    # Remove rows with missing amounts
    crh = crh[(~crh["amount_owed"].isna()) & (~crh["amount_paid"].isna())]

    # 6. Compute average amount paid for this group
    avg_paid = crh["amount_paid"].mean()

    # 7. Filter to those who paid more than the average
    result = crh[crh["amount_paid"] > avg_paid].copy()

    # 8. Sort by amount_paid descending
    result = result.sort_values("amount_paid", ascending=False)

    # 9. Only required columns
    result = result[["folio", "amount_owed", "amount_paid"]].reset_index(drop=True)

    return result