import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh03_1", "crh03_2"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Average amount paid among households who feel unsafe or very unsafe and reported a value
    unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]
    unsafe_crh = unsafe.merge(df_crh, on="folio", how="left")
    unsafe_paid = unsafe_crh[(unsafe_crh["crh03_1"] == 1.0) & (unsafe_crh["crh03_2"].notna())]
    avg_paid_unsafe = unsafe_paid["crh03_2"].mean()

    # Oaxaca households (state code 20)
    df_portad_unique = df_portad.drop_duplicates(subset=["folio"])
    oaxaca_folios = set(df_portad_unique[df_portad_unique["ent"] == 20.0]["folio"])

    # Oaxaca households that reported a monetary amount paid in last 12 months and greater than the average
    crh_oaxaca = df_crh[df_crh["folio"].isin(oaxaca_folios)]
    crh_oaxaca_paid = crh_oaxaca[(crh_oaxaca["crh03_1"] == 1.0) & (crh_oaxaca["crh03_2"].notna())]

    if pd.isna(avg_paid_unsafe):
        result = crh_oaxaca_paid[["folio", "crh03_2"]].iloc[0:0].copy()
    else:
        result = crh_oaxaca_paid[crh_oaxaca_paid["crh03_2"] > avg_paid_unsafe][["folio", "crh03_2"]].copy()

    result = result.rename(columns={"crh03_2": "amount_paid_last_12_months"})
    result = result.drop_duplicates(subset=["folio", "amount_paid_last_12_months"])
    result = result.sort_values(by="amount_paid_last_12_months", ascending=False).reset_index(drop=True)
    return result