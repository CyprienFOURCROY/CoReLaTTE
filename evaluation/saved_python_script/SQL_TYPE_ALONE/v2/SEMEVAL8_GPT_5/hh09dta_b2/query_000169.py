import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()

    # Determine Oaxaca households and age composition per household
    grp = df_portad.groupby("folio", as_index=True)
    ent_20 = grp["ent"].apply(lambda x: (x == 20).any())
    has60 = grp["edad"].apply(lambda s: (s >= 60).any())
    hasU30 = grp["edad"].apply(lambda s: (s < 30).any())
    perhh = pd.DataFrame({"ent_20": ent_20, "has60": has60, "hasU30": hasU30}).reset_index()

    # Oaxaca-wide average total debts + interests among indebted households
    oax_folios = perhh.loc[perhh["ent_20"], "folio"]
    crh_oax = df_crh[df_crh["folio"].isin(oax_folios)]
    crh_oax_indebted = crh_oax[(crh_oax["crh04_1"] == 1) & (crh_oax["crh04_2"].notna())]
    oax_avg_debt = crh_oax_indebted["crh04_2"].mean()

    # Eligible households: Oaxaca with at least one member >=60 and at least one <30
    eligible_folios = perhh.loc[perhh["ent_20"] & perhh["has60"] & perhh["hasU30"], "folio"]
    crh_eligible = df_crh[df_crh["folio"].isin(eligible_folios)]

    # Among eligible, keep those with debt value and >= Oaxaca-wide average
    filt = (crh_eligible["crh04_1"] == 1) & (crh_eligible["crh04_2"].notna())
    if pd.notna(oax_avg_debt):
        filt = filt & (crh_eligible["crh04_2"] >= oax_avg_debt)
    else:
        # If Oaxaca avg is NaN, no household can meet >= NaN
        crh_eligible = crh_eligible.iloc[0:0]  # empty
        avg_result = float("nan")
        return pd.DataFrame({"average_total_debt_pesos": [avg_result]})

    selected = crh_eligible[filt]
    avg_result = selected["crh04_2"].mean()

    return pd.DataFrame({"average_total_debt_pesos": [avg_result]})