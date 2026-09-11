def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # 1. Households in Oaxaca (ent==20) with at least one member aged 18+
    df_oax = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)]
    oax_folios = df_oax["folio"].unique()

    # 2. Households with numeric value for total debts + interests (crh04_2 not null)
    df_crh_debt = df_crh[df_crh["crh04_2"].notnull() & (df_crh["folio"].isin(oax_folios))]

    # 3. Merge with su01 (use plot/land for sowing/farming/vegetables)
    df_su_oax = df_su[df_su["folio"].isin(df_crh_debt["folio"])]
    df_merge = df_crh_debt[["folio", "crh04_2"]].merge(
        df_su_oax[["folio", "su01"]], on="folio", how="left"
    )

    # 4. Only keep su01 == 1 (Yes) or 3 (No)
    df_merge = df_merge[df_merge["su01"].isin([1.0, 3.0])]

    # 5. Compute overall average
    overall_avg = df_merge["crh04_2"].mean()

    # 6. Compute group averages
    group_avg = (
        df_merge.groupby("su01", as_index=False)["crh04_2"]
        .mean()
        .rename(columns={"crh04_2": "average_total_debt"})
    )

    # 7. Map su01 to label
    su01_map = {1.0: "Yes", 3.0: "No"}
    group_avg["use_plot_land"] = group_avg["su01"].map(su01_map)

    # 8. Only keep groups above overall average
    group_avg = group_avg[group_avg["average_total_debt"] > overall_avg]

    # 9. Sort from highest to lowest average debt
    group_avg = group_avg.sort_values("average_total_debt", ascending=False)

    # 10. Return only required columns
    return group_avg[["use_plot_land", "average_total_debt"]].reset_index(drop=True)