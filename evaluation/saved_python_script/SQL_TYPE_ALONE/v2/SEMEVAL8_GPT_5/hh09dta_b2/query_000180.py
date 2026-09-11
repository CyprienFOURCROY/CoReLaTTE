import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_crh = tables["ii_crh"]

    # Households in Oaxaca (ent == 20)
    oax_folios = df_portad.loc[df_portad["ent"] == 20.0, ["folio"]].drop_duplicates()

    # Households that own a motor vehicle and reported its value
    ah_mask = (df_ah["ah03d"] == 1.0) & (df_ah["ah04d_1"] == 1.0) & (df_ah["ah04d_2"].notna())
    df_mv = df_ah.loc[ah_mask, ["folio", "ah04d_2"]].groupby("folio", as_index=False)["ah04d_2"].max()

    # Households that reported a value for total debts and interests
    crh_mask = (df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())
    df_debts = df_crh.loc[crh_mask, ["folio"]].drop_duplicates()

    # Merge filters: Oaxaca + Motor vehicle with value + Debts value reported
    eligible = oax_folios.merge(df_mv, on="folio", how="inner").merge(df_debts, on="folio", how="inner")

    avg_value = eligible["ah04d_2"].mean()

    return pd.DataFrame({"average_motor_vehicle_value": [avg_value]})