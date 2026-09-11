def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_vlh = tables["ii_vlh"]

    # 1. Households in Oaxaca (ent == 20)
    df_oaxaca = df_portad[df_portad["ent"] == 20.0]

    # 2. Adults (edad >= 18)
    df_oaxaca_adults = df_oaxaca[df_oaxaca["edad"] >= 18]

    # 3. Merge with ii_in to get income from Other Government Program
    df_merged = pd.merge(
        df_oaxaca_adults[["folio", "ls"]],
        df_in[["folio", "in01a10_1", "in01a10_2", "in02a10"]],
        on="folio",
        how="left"
    )

    # 4. Keep only adults who received income from Other Government Program with positive direct amount
    # in01a10_1 == 1 means received income, in02a10 > 0 means positive direct amount
    df_income = df_merged[
        (df_merged["in01a10_1"] == 1.0) &
        (df_merged["in02a10"].notna()) &
        (df_merged["in02a10"] > 0)
    ]

    # 5. Get households (folio) with at least one such adult
    folios_with_income = df_income["folio"].unique()

    # 6. Compute average in02a10 among such households (use max per household in case of multiple adults)
    df_income_household = df_income.groupby("folio", as_index=False)["in02a10"].max()
    avg_income = df_income_household["in02a10"].mean()

    # 7. Households with in02a10 above average
    folios_above_avg = df_income_household[df_income_household["in02a10"] > avg_income]["folio"].unique()

    # 8. Merge with ii_vlh to get feeling of safety at home (vlh04: 1=Very safe, 2=Safe)
    df_vlh_oaxaca = df_vlh[df_vlh["folio"].isin(folios_above_avg)]
    df_vlh_safe = df_vlh_oaxaca[df_vlh_oaxaca["vlh04"].isin([1.0, 2.0])]

    # 9. Households whose members report feeling very safe or safe at home (at least one member)
    folios_final = df_vlh_safe["folio"].unique()

    # 10. Count number of such households
    result = len(folios_final)

    return pd.DataFrame({"num_households": [result]})