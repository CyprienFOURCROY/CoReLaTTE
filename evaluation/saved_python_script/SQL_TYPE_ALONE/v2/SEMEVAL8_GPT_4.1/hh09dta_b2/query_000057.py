def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]

    # 1. Households that use land for farming: su01 == 1
    farming = df_su[df_su["su01"] == 1]

    # 2. Households that own a motor vehicle: ah03d == 1
    motor_vehicle = df_ah[df_ah["ah03d"] == 1]

    # 3. Merge on folio to get households that satisfy both
    merged = farming.merge(motor_vehicle[["folio"]], on="folio", how="inner")

    # 4. Only keep those with positive seed expenses (su234 > 0)
    merged = merged[merged["su234"].notna() & (merged["su234"] > 0)]

    # 5. Compute overall average seed expense among all farming households with positive seed expenses
    farming_positive_seed = farming[farming["su234"].notna() & (farming["su234"] > 0)]
    avg_seed_expense = farming_positive_seed["su234"].mean()

    # 6. Filter merged for those with seed expense below the average
    result = merged[merged["su234"] < avg_seed_expense]

    # 7. Return Household IDs and their seed expense
    return result[["folio", "su234"]].reset_index(drop=True)