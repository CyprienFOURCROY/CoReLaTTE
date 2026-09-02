def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]

    # 1. Filter Oaxaca households (ent == 20)
    df_portad_oax = df_portad[df_portad["ent"] == 20.0]

    # 2. Compute average adult age (edad >= 18) in Oaxaca
    df_adults_oax = df_portad_oax[df_portad_oax["edad"] >= 18]
    avg_adult_age = df_adults_oax["edad"].mean()

    # 3. For each household in Oaxaca, check if it has at least one member aged 18+ and older than Oaxaca's average adult age
    # Get folios with at least one such member
    folios_adult_older = df_adults_oax[df_adults_oax["edad"] > avg_adult_age]["folio"].unique()

    # 4. Households in Oaxaca that received a positive amount from "Other Government Program" (in02a10 > 0)
    df_in_oax = df_in[df_in["folio"].isin(df_portad_oax["folio"])]
    df_in_oax_prog = df_in_oax[df_in_oax["in02a10"] > 0]

    # 5. Intersection: households that satisfy both conditions
    eligible_folios = np.intersect1d(df_in_oax_prog["folio"].unique(), folios_adult_older)

    # 6. For these households, get average vlh04 and average in02a10
    df_vlh_eligible = df_vlh[df_vlh["folio"].isin(eligible_folios)]
    df_in_eligible = df_in[df_in["folio"].isin(eligible_folios)]

    avg_vlh04 = df_vlh_eligible["vlh04"].mean()
    avg_in02a10 = df_in_eligible["in02a10"].mean()
    n_households = len(eligible_folios)

    return pd.DataFrame({
        "avg_feel_safe_at_home": [avg_vlh04],
        "avg_amount_received_other_gov_prog": [avg_in02a10],
        "num_households": [n_households]
    })