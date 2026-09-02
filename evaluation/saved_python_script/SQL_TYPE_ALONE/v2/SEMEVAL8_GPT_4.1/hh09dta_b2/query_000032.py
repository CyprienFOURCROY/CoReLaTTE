def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # 1. Oaxaca households: ent == 20
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # 2. Merge with df_vlh to get 'feel unsafe or very unsafe at home'
    # vlh04: 3 = Unsafe, 4 = Very unsafe
    df_vlh_ox = df_vlh.merge(oaxaca_households, on="folio", how="inner")
    unsafe_folios = df_vlh_ox[df_vlh_ox["vlh04"].isin([3.0, 4.0])][["folio"]]

    # 3. Merge with df_crh to get debts+interest (crh04_2)
    df_crh_ox = df_crh.merge(oaxaca_households, on="folio", how="inner")

    # 4. Compute average crh04_2 among unsafe/very unsafe Oaxaca households
    df_crh_unsafe = df_crh_ox.merge(unsafe_folios, on="folio", how="inner")
    avg_debt = df_crh_unsafe["crh04_2"].dropna().mean()

    # 5. Find all Oaxaca households with crh04_2 > avg_debt
    df_crh_ox_debt = df_crh_ox[~df_crh_ox["crh04_2"].isna()]
    df_above_avg = df_crh_ox_debt[df_crh_ox_debt["crh04_2"] > avg_debt][["folio", "crh04_2"]]

    # 6. Order from highest to lowest
    df_above_avg = df_above_avg.sort_values("crh04_2", ascending=False).reset_index(drop=True)

    return df_above_avg.rename(columns={"crh04_2": "total_debts_plus_interest_pesos"})