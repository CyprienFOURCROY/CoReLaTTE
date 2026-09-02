import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_crh = tables["ii_crh"]

    # Households in Oaxaca (ent == 20) with at least one adult (edad >= 18)
    adult_oax_folios = (
        df_portad.loc[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18), "folio"]
        .dropna()
        .unique()
    )

    # Households that did not receive Liconsa milk (in03a == 3)
    s1 = df_in.loc[
        df_in["folio"].isin(adult_oax_folios) & (df_in["in03a"] == 3.0),
        ["folio", "in02a10"]
    ].copy()

    s1_folios = s1["folio"].unique()

    # Debts info for these households
    crh_s1 = df_crh.loc[df_crh["folio"].isin(s1_folios), ["folio", "crh04_2"]].copy()

    # Average of reported total debts + interests among these households (ignore NaN)
    avg_debts = crh_s1.loc[crh_s1["crh04_2"].notna(), "crh04_2"].mean()

    # Households with positive debts exceeding the average
    folios_pos_gt_avg = crh_s1.loc[
        (crh_s1["crh04_2"] > 0) & (crh_s1["crh04_2"] > avg_debts), "folio"
    ].unique()

    # Households that directly received a positive amount from Other Government Program
    folios_other_prog_pos = s1.loc[s1["in02a10"] > 0, "folio"].unique()

    # Intersection of conditions
    final_folios = set(folios_pos_gt_avg).intersection(set(folios_other_prog_pos))

    return pd.DataFrame({"num_households": [len(final_folios)]})