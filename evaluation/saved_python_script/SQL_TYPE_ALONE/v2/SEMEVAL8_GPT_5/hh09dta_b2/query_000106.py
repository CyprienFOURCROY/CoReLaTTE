import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_2"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Households in Oaxaca (ent == 20)
    oax_folios = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()

    # Reported total debts + interests for Oaxaca households
    crh_oax = df_crh.merge(oax_folios, on="folio", how="inner")
    crh_oax_reported = crh_oax[crh_oax["crh04_2"].notna()].copy()

    if crh_oax_reported.empty:
        return pd.DataFrame({"count_households": [0]})

    # Oaxaca average among reported values
    oax_avg = crh_oax_reported["crh04_2"].mean()

    # Above Oaxaca average
    oax_above_avg = crh_oax_reported[crh_oax_reported["crh04_2"] > oax_avg][["folio"]].drop_duplicates()

    # Positive amount directly from Other Government Program
    pos_other_gov = df_in[(df_in["in02a10"].notna()) & (df_in["in02a10"] > 0)][["folio"]].drop_duplicates()

    # Intersection
    result = oax_above_avg.merge(pos_other_gov, on="folio", how="inner")

    count = result["folio"].nunique()

    return pd.DataFrame({"count_households": [count]})