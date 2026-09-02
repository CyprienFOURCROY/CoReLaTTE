def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio", "edad"]]

    # 2. Households with at least one adult (edad >= 18)
    adults = oaxaca_households[oaxaca_households["edad"] >= 18]
    adult_folios = set(adults["folio"].unique())

    # 3. Households that own domestic appliances (ah03g == 1) but NOT a motor vehicle (ah03d != 1)
    # For each household, check if at least one member has ah03g == 1 and all members have ah03d != 1
    df_ah_oaxaca = df_ah[df_ah["folio"].isin(adult_folios)]

    # Group by folio: own domestic appliances if any member has ah03g == 1
    own_domestic_appliance = df_ah_oaxaca.groupby("folio")["ah03g"].apply(lambda x: (x == 1.0).any())
    # Group by folio: own motor vehicle if any member has ah03d == 1
    own_motor_vehicle = df_ah_oaxaca.groupby("folio")["ah03d"].apply(lambda x: (x == 1.0).any())

    # Households that own domestic appliances but not a motor vehicle
    eligible_folios = own_domestic_appliance[own_domestic_appliance].index.difference(
        own_motor_vehicle[own_motor_vehicle].index
    )

    # 4. Households that reported an amount paid (crh03_1 == 1 and crh03_2 not null)
    df_crh_eligible = df_crh[df_crh["folio"].isin(eligible_folios)]
    paid_mask = (df_crh_eligible["crh03_1"] == 1.0) & (~df_crh_eligible["crh03_2"].isna())
    paid_folios = df_crh_eligible[paid_mask][["folio", "crh03_2"]]

    # Since crh03 is at household level, but there may be multiple rows per folio, take the first per folio
    paid_folios = paid_folios.drop_duplicates(subset="folio")

    # 5. Compute average
    if len(paid_folios) == 0:
        avg_paid = np.nan
    else:
        avg_paid = paid_folios["crh03_2"].mean()

    return pd.DataFrame({"average_amount_paid": [avg_paid]})