def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20.0]

    # 2. Households that report feeling unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]

    # 3. Merge to get only Oaxaca households that feel unsafe/very unsafe
    oaxaca_unsafe = oaxaca_portad.merge(df_vlh_unsafe[["folio", "vlh04"]], on="folio", how="inner")

    # 4. Get the set of folios (households) that match
    unsafe_folios = oaxaca_unsafe["folio"].unique()

    # 5. For these households, check if at least one adult member (edad >= 18)
    oaxaca_adults = oaxaca_portad[
        (oaxaca_portad["folio"].isin(unsafe_folios)) & (oaxaca_portad["edad"] >= 18)
    ]
    folios_with_adult = set(oaxaca_adults["folio"].unique())

    # 6. For these households, check if at least one member owns a motor vehicle (ah03d == 1)
    ah_motor_vehicle = df_ah[
        (df_ah["folio"].isin(unsafe_folios)) & (df_ah["ah03d"] == 1.0)
    ]
    folios_with_motor_vehicle = set(ah_motor_vehicle["folio"].unique())

    # 7. Households that have both at least one adult and at least one member who owns a motor vehicle
    folios_with_both = folios_with_adult & folios_with_motor_vehicle

    # 8. Results
    total_unsafe_households = len(unsafe_folios)
    total_with_both = len(folios_with_both)

    return pd.DataFrame({
        "unsafe_households_in_oaxaca": [total_unsafe_households],
        "unsafe_households_with_adult_and_motor_vehicle_owner": [total_with_both]
    })