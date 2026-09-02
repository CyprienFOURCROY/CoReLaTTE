def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Households that own a motor vehicle (ah03d == 1)
    df_ah_mv = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Households that reported a value for total debts (crh04_1 == 1 and crh04_2 not null)
    df_crh_debt = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notnull())][["folio", "crh04_2"]]

    # Merge to get only households that satisfy both conditions
    df_mv_debt = df_ah_mv.merge(df_crh_debt, on="folio", how="inner")

    # Merge with portad to get state
    df_mv_debt = df_mv_debt.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Compute overall average debt
    overall_avg_debt = df_mv_debt["crh04_2"].mean()

    # Filter households with debt above the overall average
    df_above_avg = df_mv_debt[df_mv_debt["crh04_2"] > overall_avg_debt]

    # Count by state
    result = df_above_avg.groupby("ent").size().reset_index(name="households_above_avg_debt")

    # Sort by count descending, then by state code ascending
    result = result.sort_values(["households_above_avg_debt", "ent"], ascending=[False, True]).reset_index(drop=True)

    return result