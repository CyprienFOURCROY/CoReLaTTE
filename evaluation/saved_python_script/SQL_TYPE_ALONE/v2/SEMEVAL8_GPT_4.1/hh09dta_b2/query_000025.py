def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]
    df_vlh = tables["ii_vlh"]

    # 1. Filter Oaxaca households
    oaxaca_ent = 20.0
    df_portad_oax = df_portad[df_portad["ent"] == oaxaca_ent]

    # 2. Merge with su to get worker expenses
    df_oax_su = df_portad_oax[["folio"]].merge(df_su[["folio", "su237"]], on="folio", how="left")

    # 3. Compute Oaxaca state average worker expense (exclude NaN)
    oax_worker_expenses = df_oax_su["su237"].dropna()
    if len(oax_worker_expenses) == 0:
        # No data, return empty DataFrame
        return pd.DataFrame(columns=["nna02", "knows_robbery", "avg_worker_expense", "households"])
    oax_worker_expense_avg = oax_worker_expenses.mean()

    # 4. Keep only households with worker expense above state average
    df_oax_su_above_avg = df_oax_su[df_oax_su["su237"] > oax_worker_expense_avg]

    # 5. Merge with ii_nna to get nna02 (number of non-ag businesses in last 12 months)
    df_above_avg_nna = df_oax_su_above_avg.merge(df_nna[["folio", "nna02"]], on="folio", how="left")

    # 6. Merge with ii_vlh to get "knows family/friend robbed in last 5 years" (vlh08a)
    df_above_avg_nna_vlh = df_above_avg_nna.merge(df_vlh[["folio", "vlh08a"]], on="folio", how="left")

    # 7. Prepare grouping columns
    # nna02: number of non-ag businesses (can be NaN)
    # knows_robbery: True if vlh08a==1.0, False if vlh08a==3.0, np.nan otherwise
    def knows_robbery_map(x):
        if x == 1.0:
            return True
        elif x == 3.0:
            return False
        else:
            return np.nan

    df_above_avg_nna_vlh["knows_robbery"] = df_above_avg_nna_vlh["vlh08a"].map(knows_robbery_map)

    # 8. Group by nna02 and knows_robbery, aggregate
    result = (
        df_above_avg_nna_vlh
        .groupby(["nna02", "knows_robbery"], dropna=False)
        .agg(
            avg_worker_expense=("su237", "mean"),
            households=("folio", "count")
        )
        .reset_index()
    )

    return result[["nna02", "knows_robbery", "avg_worker_expense", "households"]]