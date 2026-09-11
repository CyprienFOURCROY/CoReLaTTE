import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    # Determine Oaxaca households (ent == 20)
    portad_ent = df_portad.groupby("folio", as_index=False)["ent"].first()
    oaxaca_hh = portad_ent[portad_ent["ent"] == 20.0][["folio"]]

    # Households that use a plot for farming and their workers expense
    df_su = tables["ii_su"][["folio", "su01", "su237"]].copy()
    su_plot = df_su[df_su["su01"] == 1.0]

    # Merge to get Oaxaca plot-using households
    oaxaca_plot = oaxaca_hh.merge(su_plot, on="folio", how="inner")

    # Compute average expense on agricultural workers across Oaxaca plot-using households
    mean_workers_exp = oaxaca_plot["su237"].mean()

    # Keep households with workers expense above that average
    above_avg_workers = oaxaca_plot[oaxaca_plot["su237"] > mean_workers_exp][["folio"]]

    # Households with reported positive total debt
    df_crh = tables["ii_crh"][["folio", "crh04_2"]].copy()
    positive_debt = df_crh[df_crh["crh04_2"] > 0][["folio"]]

    # Electronic devices value per household
    df_ah = tables["ii_ah"][["folio", "ah04e_2"]].copy()
    ah_elec_val = df_ah.groupby("folio", as_index=False)["ah04e_2"].max()

    # Combine filters: Oaxaca + plot + above avg workers expense + positive debt
    eligible_hh = above_avg_workers.merge(positive_debt, on="folio", how="inner")

    # Merge with electronic devices value
    final = eligible_hh.merge(ah_elec_val, on="folio", how="left")

    avg_value = final["ah04e_2"].mean()

    return pd.DataFrame({"avg_value_electronic_devices_pesos": [avg_value]})