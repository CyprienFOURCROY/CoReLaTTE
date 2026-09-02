def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"].unique()

    # 2. Households that reported disease/accident/hospitalization in last 5 years (se01b == 1)
    se_disease = df_se[(df_se["se01b"] == 1.0) & (df_se["folio"].isin(oaxaca_folios))]
    folios_disease = se_disease["folio"].unique()

    # 3. Households with a recorded motor vehicle value (ah04d_1 == 1 and ah04d_2 not null)
    ah_motor = df_ah[
        (df_ah["folio"].isin(folios_disease)) &
        (df_ah["ah04d_1"] == 1.0) &
        (~df_ah["ah04d_2"].isnull())
    ]
    # Aggregate motor vehicle value per household (sum in case of multiple individuals)
    motor_value_per_folio = ah_motor.groupby("folio")["ah04d_2"].sum().reset_index()

    # 4. Merge with crh for total debts + interests (crh04_1 == 1, crh04_2 not null)
    crh_debts = df_crh[
        (df_crh["folio"].isin(motor_value_per_folio["folio"])) &
        (df_crh["crh04_1"] == 1.0) &
        (~df_crh["crh04_2"].isnull())
    ][["folio", "crh04_2"]]

    # Merge motor value and debts
    merged = motor_value_per_folio.merge(crh_debts, on="folio", how="inner")

    # 5. Only those whose total motor vehicle value is below the average among these households
    avg_motor_value = merged["ah04d_2"].mean()
    filtered = merged[merged["ah04d_2"] < avg_motor_value]

    # 6. Average total debts + interest (crh04_2) among these
    if len(filtered) == 0:
        avg_debt = np.nan
    else:
        avg_debt = filtered["crh04_2"].mean()

    return pd.DataFrame({"average_total_debts_plus_interest": [avg_debt]})