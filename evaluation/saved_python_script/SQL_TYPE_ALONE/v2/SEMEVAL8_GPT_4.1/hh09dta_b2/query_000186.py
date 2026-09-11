def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_su = tables["ii_su"]

    # 1. Households that use a plot/land for sowing/farming (su01 == 1)
    df_su_plot = df_su[df_su["su01"] == 1.0][["folio"]]

    # 2. Households with reported total debts + interests (crh04_1 == 1 and crh04_2 not null)
    df_crh_debt = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notnull())][["folio", "crh04_2"]]

    # 3. Merge to get only households that satisfy both conditions
    df_merge = pd.merge(df_su_plot, df_crh_debt, on="folio", how="inner")

    # 4. Add state info
    df_merge = pd.merge(df_merge, df_portad[["folio", "ent"]], on="folio", how="left")

    # 5. Remove rows with missing state
    df_merge = df_merge[df_merge["ent"].notnull()]

    # 6. Compute overall average debt
    overall_avg = df_merge["crh04_2"].mean()

    # 7. Group by state, count households, compute average debt
    df_group = (
        df_merge.groupby("ent")
        .agg(
            num_households=("folio", "count"),
            avg_debt=("crh04_2", "mean")
        )
        .reset_index()
    )

    # 8. Filter: at least 20 households and avg_debt > overall_avg
    df_result = df_group[(df_group["num_households"] >= 20) & (df_group["avg_debt"] > overall_avg)]

    # 9. Sort by avg_debt descending
    df_result = df_result.sort_values("avg_debt", ascending=False)

    # 10. Rename columns for clarity
    df_result = df_result.rename(columns={"ent": "state"})

    # 11. Reset index for clean output
    df_result = df_result.reset_index(drop=True)

    return df_result[["state", "num_households", "avg_debt"]]