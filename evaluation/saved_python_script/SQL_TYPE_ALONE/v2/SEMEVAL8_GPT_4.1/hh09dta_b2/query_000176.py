def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_su = tables["ii_su"]

    # Households that use a plot/land for farming: su01 == 1
    df_su_farm = df_su[df_su["su01"] == 1]

    # Households with a recorded total debt (debts + interests): crh04_1 == 1 and crh04_2 not null
    df_crh_debt = df_crh[(df_crh["crh04_1"] == 1) & (df_crh["crh04_2"].notnull())]

    # Merge on folio to get only those households that satisfy both conditions
    df_merge = pd.merge(df_su_farm[["folio"]], df_crh_debt[["folio", "crh04_2"]], on="folio", how="inner")

    # Merge with portad to get state info
    df_merge = pd.merge(df_merge, df_portad[["folio", "ent"]], on="folio", how="left")

    # Compute overall average total debt
    overall_avg = df_merge["crh04_2"].mean()

    # Filter to only those households whose debt exceeds the overall average
    df_above_avg = df_merge[df_merge["crh04_2"] > overall_avg]

    # Group by state and compute average household total debt
    df_state_avg = df_above_avg.groupby("ent", as_index=False)["crh04_2"].mean()

    # Filter states with average > 10,000 pesos
    df_result = df_state_avg[df_state_avg["crh04_2"] > 10000].copy()

    # Rename columns for clarity
    df_result = df_result.rename(columns={"ent": "state", "crh04_2": "average_total_debt"})

    return df_result.reset_index(drop=True)