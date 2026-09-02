def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_in = tables["ii_in"]

    # Step 1: Filter Oaxaca households
    oaxaca_ent = 20.0
    df_oaxaca = df_portad[df_portad["ent"] == oaxaca_ent][["folio"]]

    # Step 2: Merge with crh to get debts+interests (crh04_2)
    df_oaxaca_crh = pd.merge(df_oaxaca, df_crh[["folio", "crh04_2"]], on="folio", how="left")

    # Step 3: Keep only households with a reported value for crh04_2 (not null)
    df_oaxaca_crh_valid = df_oaxaca_crh[df_oaxaca_crh["crh04_2"].notnull()]

    # Step 4: Compute Oaxaca average (among those with reported values)
    oaxaca_avg_debt = df_oaxaca_crh_valid["crh04_2"].mean()

    # Step 5: Keep only those above the average
    df_above_avg = df_oaxaca_crh_valid[df_oaxaca_crh_valid["crh04_2"] > oaxaca_avg_debt][["folio"]]

    # Step 6: Merge with ii_in to get in02a10 (amount received directly from Other Government Program)
    df_above_avg_in = pd.merge(df_above_avg, df_in[["folio", "in02a10"]], on="folio", how="left")

    # Step 7: Keep only those with a positive amount in in02a10
    df_final = df_above_avg_in[df_above_avg_in["in02a10"].notnull() & (df_above_avg_in["in02a10"] > 0)]

    # Step 8: Count number of households
    count = df_final["folio"].nunique()

    return pd.DataFrame({"households": [count]})