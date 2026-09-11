def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]

    # 1. Filter Oaxaca households (ent == 20)
    df_oax = df_portad[df_portad["ent"] == 20]

    # 2. Find households with at least one member aged 60+ and at least one member <30
    hh_60plus = set(df_oax[df_oax["edad"] >= 60]["folio"])
    hh_under30 = set(df_oax[df_oax["edad"] < 30]["folio"])
    hh_both = hh_60plus & hh_under30

    # 3. Get crh04_2 (total debts + interests in pesos) for these households
    df_crh_oax = df_crh[df_crh["folio"].isin(hh_both)]

    # 4. Only consider households with a valid debt value (crh04_1 == 1 and crh04_2 not null)
    df_crh_oax_debt = df_crh_oax[(df_crh_oax["crh04_1"] == 1) & (~df_crh_oax["crh04_2"].isna())]

    # 5. Compute Oaxaca-wide average among indebted households (ent == 20, crh04_1 == 1, crh04_2 not null)
    df_crh_oax_all = df_crh.merge(df_portad[["folio", "ent"]], on="folio", how="left")
    df_crh_oax_all_debt = df_crh_oax_all[(df_crh_oax_all["ent"] == 20) & (df_crh_oax_all["crh04_1"] == 1) & (~df_crh_oax_all["crh04_2"].isna())]
    oax_debt_avg = df_crh_oax_all_debt["crh04_2"].mean()

    # 6. Filter to those with debt >= Oaxaca-wide average
    df_crh_oax_debt_ge_avg = df_crh_oax_debt[df_crh_oax_debt["crh04_2"] >= oax_debt_avg]

    # 7. Compute average total debts + interests (in pesos) for these households
    avg_total_debt = df_crh_oax_debt_ge_avg["crh04_2"].mean()

    return pd.DataFrame({"average_total_debts_plus_interests": [avg_total_debt]})