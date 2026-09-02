import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()
    df_ah = tables["ii_ah"].copy()

    # Households in Oaxaca
    folios_oax = df_portad.loc[df_portad["ent"] == 20, "folio"].dropna().unique()

    # Households in Oaxaca with at least one 25–54-year-old member
    mask_age = (df_portad["edad"] >= 25) & (df_portad["edad"] <= 54)
    folios_oax_age = df_portad.loc[(df_portad["ent"] == 20) & mask_age, "folio"].dropna().unique()

    # Households with at least one member owning financial assets/afores
    folios_fa = df_ah.loc[df_ah["ah03h"] == 1, "folio"].dropna().unique()
    folios_fa_oax = pd.Index(folios_fa).intersection(folios_oax)

    # Households with recorded total debts + interests
    df_crh_rd = df_crh.loc[(df_crh["crh04_1"] == 1) & (df_crh["crh04_2"].notna()), ["folio", "crh04_2"]].drop_duplicates(subset=["folio"])

    # Average among Oaxaca households with a 25–54-year-old and recorded debt values
    eligible_for_avg_folios = pd.Index(folios_oax_age).intersection(df_crh_rd["folio"])
    avg_value = df_crh_rd.loc[df_crh_rd["folio"].isin(eligible_for_avg_folios), "crh04_2"].mean()

    if pd.isna(avg_value):
        count = 0
    else:
        # Final households: Oaxaca, at least one 25–54-year-old, at least one member owning financial assets, recorded debt > average
        eligible_final = df_crh_rd[df_crh_rd["folio"].isin(pd.Index(folios_oax_age).intersection(folios_fa_oax))]
        count = int((eligible_final["crh04_2"] > avg_value).sum())

    return pd.DataFrame({"num_households": [count]})