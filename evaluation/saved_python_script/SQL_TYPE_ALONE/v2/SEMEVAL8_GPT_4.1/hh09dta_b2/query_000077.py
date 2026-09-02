def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # 1. Get Oaxaca households
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"].unique()

    # 2. Get households who feel unsafe or very unsafe at home
    # vlh04: 3 = Unsafe, 4 = Very unsafe
    unsafe_folios = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]["folio"].unique()

    # 3. For those, get their crh03_2 (amount paid in last 12 months)
    df_crh_unsafe = df_crh[df_crh["folio"].isin(unsafe_folios)]
    # Only consider those with a valid amount
    df_crh_unsafe_valid = df_crh_unsafe[~df_crh_unsafe["crh03_2"].isna()]

    # 4. Compute the overall average paid by these households
    avg_paid_unsafe = df_crh_unsafe_valid["crh03_2"].mean()

    # 5. For Oaxaca households, get those with a valid crh03_2 and amount > avg_paid_unsafe
    df_crh_oaxaca = df_crh[df_crh["folio"].isin(oaxaca_folios)]
    df_crh_oaxaca_valid = df_crh_oaxaca[~df_crh_oaxaca["crh03_2"].isna()]
    df_crh_oaxaca_above_avg = df_crh_oaxaca_valid[df_crh_oaxaca_valid["crh03_2"] > avg_paid_unsafe]

    # 6. Select Household IDs and amounts, sort from highest to lowest
    result = df_crh_oaxaca_above_avg[["folio", "crh03_2"]].sort_values("crh03_2", ascending=False).reset_index(drop=True)

    return result