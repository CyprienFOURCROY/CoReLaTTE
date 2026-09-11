def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]
    df_su = tables["ii_su"]

    # 1. Households in Oaxaca (ent==20)
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"].unique()

    # 2. Households that use a plot for farming (su01==1)
    df_su_oax = df_su[df_su["folio"].isin(oaxaca_folios)]
    plot_farming_folios = df_su_oax[df_su_oax["su01"] == 1.0]["folio"].unique()

    # 3. For these, get total expense on agricultural workers (su237)
    df_su_plot = df_su_oax[df_su_oax["folio"].isin(plot_farming_folios)]
    # Some households may have multiple rows, sum su237 per household
    workers_expense = df_su_plot.groupby("folio", as_index=False)["su237"].sum(min_count=1)
    # Compute average across Oaxaca plot-using households
    avg_workers_expense = workers_expense["su237"].mean()

    # 4. Households with total expense on workers > average
    high_workers_folios = workers_expense[workers_expense["su237"] > avg_workers_expense]["folio"].unique()

    # 5. Households with positive total debt (crh04_2 > 0)
    df_crh_oax = df_crh[df_crh["folio"].isin(oaxaca_folios)]
    df_crh_debt = df_crh_oax[df_crh_oax["crh04_2"].notna() & (df_crh_oax["crh04_2"] > 0)]
    debt_folios = df_crh_debt["folio"].unique()

    # 6. Intersection: folios in Oaxaca, use plot, high worker expense, positive debt
    eligible_folios = set(plot_farming_folios) & set(high_workers_folios) & set(debt_folios)

    # 7. For these folios, get value of electronic devices (ah04e_2) from ii_ah
    df_ah_oax = df_ah[df_ah["folio"].isin(eligible_folios)]
    # Only consider rows where ah04e_2 is not null and positive
    df_ah_electronics = df_ah_oax[df_ah_oax["ah04e_2"].notna() & (df_ah_oax["ah04e_2"] > 0)]

    # 8. Average value in pesos
    if len(df_ah_electronics) == 0:
        avg_value = np.nan
    else:
        avg_value = df_ah_electronics["ah04e_2"].mean()

    return pd.DataFrame({"average_electronic_device_value": [avg_value]})