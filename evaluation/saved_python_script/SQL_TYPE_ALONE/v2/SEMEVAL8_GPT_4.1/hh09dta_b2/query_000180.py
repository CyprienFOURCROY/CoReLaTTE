def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"].unique()

    # 2. Households that own a motor vehicle (ah03d == 1)
    df_ah_mv = df_ah[(df_ah["ah03d"] == 1.0)]

    # 3. Households that reported a value for their total debts and interests (crh04_2 not null)
    df_crh_debt = df_crh[df_crh["crh04_2"].notnull()]

    # 4. Merge to get folios that satisfy all conditions
    folios_mv = set(df_ah_mv["folio"])
    folios_debt = set(df_crh_debt["folio"])
    folios_oaxaca = set(oaxaca_folios)
    folios_final = folios_mv & folios_debt & folios_oaxaca

    # 5. For these folios, get the reported value of motor vehicles (ah04d_2)
    df_ah_mv_val = df_ah_mv[df_ah_mv["folio"].isin(folios_final)]

    # Only consider rows where ah04d_2 is not null
    df_ah_mv_val = df_ah_mv_val[df_ah_mv_val["ah04d_2"].notnull()]

    # Compute the average
    avg_value = df_ah_mv_val["ah04d_2"].mean()

    return pd.DataFrame({"average_motor_vehicle_value": [avg_value]})