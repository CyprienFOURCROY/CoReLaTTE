import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"].copy()
    df_crh = tables["ii_crh"].copy()

    # Households in Oaxaca (ent == 20) with at least one adult (edad >= 18)
    tmp = df_portad.loc[df_portad["ent"] == 20, ["folio", "edad"]].copy()
    tmp["is_adult"] = tmp["edad"] >= 18
    hh_adult_oax = tmp.groupby("folio")["is_adult"].any().reset_index()
    hh_adult_oax = hh_adult_oax[hh_adult_oax["is_adult"]]

    # Households that use a plot of land for farming (su01 == 1)
    su_users = df_su.loc[df_su["su01"] == 1, ["folio"]].drop_duplicates()

    eligible = hh_adult_oax.merge(su_users, on="folio", how="inner")[["folio"]]

    # Households with numeric values for both amount paid (crh03_2) and total debts + interest (crh04_2)
    crh_cols = ["folio", "crh03_1", "crh03_2", "crh04_1", "crh04_2"]
    df_crh_sub = df_crh[crh_cols].copy()
    cond_paid = (df_crh_sub["crh03_1"] == 1) & (df_crh_sub["crh03_2"].notna())
    cond_total = (df_crh_sub["crh04_1"] == 1) & (df_crh_sub["crh04_2"].notna())
    df_crh_valid = df_crh_sub.loc[cond_paid & cond_total, ["folio", "crh04_2"]]

    final = eligible.merge(df_crh_valid, on="folio", how="inner")

    if final.empty:
        return pd.DataFrame(columns=["folio", "total_debts_plus_interest"])

    avg_total = final["crh04_2"].mean()
    above_avg = final[final["crh04_2"] > avg_total].copy()
    above_avg = above_avg.sort_values(by="crh04_2", ascending=False)

    result = above_avg.rename(columns={"crh04_2": "total_debts_plus_interest"})[["folio", "total_debts_plus_interest"]].reset_index(drop=True)
    return result