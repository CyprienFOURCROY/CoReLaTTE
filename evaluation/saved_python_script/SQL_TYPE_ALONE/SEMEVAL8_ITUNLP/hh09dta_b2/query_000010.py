import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_crh = tables["ii_crh"]

    # Households in Oaxaca and their sizes
    df_portad_oax = df_portad[df_portad["ent"] == 20.0][["folio", "ls"]]
    hh_size = df_portad_oax.groupby("folio", as_index=False).agg(household_size=("ls", "count"))

    # Households with at least one member who owns/shares a non-ag business
    nna_has_business = (
        df_nna.assign(has_business=(df_nna["nna01"] == 1.0))
        .groupby("folio", as_index=False)["has_business"]
        .max()
    )
    nna_yes = nna_has_business[nna_has_business["has_business"]][["folio"]]

    # Reported total debts + interests (value provided)
    crh_valid = df_crh[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())][["folio", "crh04_2"]]
    crh_agg = crh_valid.groupby("folio", as_index=False).agg(crh04_2=("crh04_2", "max"))

    # Combine filters: Oaxaca households with non-ag business and valid debt value
    result = (
        hh_size
        .merge(nna_yes, on="folio", how="inner")
        .merge(crh_agg, on="folio", how="inner")
        .sort_values(by="crh04_2", ascending=False)
        .head(10)
        .reset_index(drop=True)
        .rename(columns={"crh04_2": "total_debts_plus_interest_pesos"})
    )

    return result[["folio", "total_debts_plus_interest_pesos", "household_size"]]