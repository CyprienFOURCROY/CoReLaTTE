import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]

    # Household-state mapping (Oaxaca = 20)
    hh_ent = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])
    oax_households = set(hh_ent.loc[hh_ent["ent"] == 20, "folio"])

    # Average total household debt (including interest) among indebted households in Oaxaca
    crh_cols = ["folio", "crh04_1", "crh04_2"]
    df_crh_oax = df_crh[crh_cols].merge(hh_ent, on="folio", how="left")
    indebted_oax = (df_crh_oax["ent"] == 20) & (df_crh_oax["crh04_1"] == 1) & (df_crh_oax["crh04_2"].notna())
    avg_debt = df_crh_oax.loc[indebted_oax, "crh04_2"].mean()

    # Households with debt above the average (only meaningful if avg_debt is not NaN)
    if np.isnan(avg_debt):
        above_avg_debt_households = set()
    else:
        above_avg_cond = (df_crh_oax["ent"] == 20) & (df_crh_oax["crh04_1"] == 1) & (df_crh_oax["crh04_2"].notna()) & (df_crh_oax["crh04_2"] > avg_debt)
        above_avg_debt_households = set(df_crh_oax.loc[above_avg_cond, "folio"])

    # Disease/accident/hospitalization event in last 5 years
    disease_households = set(df_se.loc[df_se["se01b"] == 1, "folio"])

    # At least one member owns an electronic device
    df_ah["has_elec_row"] = df_ah["ah03e"] == 1
    elec_by_hh = df_ah.groupby("folio", as_index=False)["has_elec_row"].any().rename(columns={"has_elec_row": "has_elec"})
    elec_households = set(elec_by_hh.loc[elec_by_hh["has_elec"], "folio"])

    # At least one member owns or shares a non-agricultural business
    nna_households = set(df_nna.loc[df_nna["nna01"] == 1, "folio"])

    # Intersection of all household-level conditions restricted to Oaxaca
    target_households = oax_households & disease_households & elec_households & nna_households & above_avg_debt_households

    # Count adults (age 18+) in Oaxaca living in these households
    adults_mask = (df_portad["ent"] == 20) & (df_portad["edad"] >= 18) & (df_portad["folio"].isin(list(target_households)))
    adult_count = int(df_portad.loc[adults_mask].shape[0])

    return pd.DataFrame({"adults_count": [adult_count]})