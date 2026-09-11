import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]

    # Households in Oaxaca (ent == 20) with at least one adult (>=18) and one minor (<18)
    people_oax = df_portad[df_portad["ent"] == 20.0]
    hh_age_flags = (
        people_oax.groupby("folio")["edad"]
        .agg(has_adult=lambda s: (s >= 18).any(), has_minor=lambda s: (s < 18).any())
        .reset_index()
    )
    hh_adult_minor = hh_age_flags[(hh_age_flags["has_adult"]) & (hh_age_flags["has_minor"])][["folio"]]

    # Households with non-ag business owned/shared
    nna_yes = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()

    # Households where a member uses a plot of land for sowing/farming/vegetables
    su_yes = df_su[df_su["su01"] == 1.0][["folio"]].drop_duplicates()

    # Intersection of all conditions
    final_hh = (
        hh_adult_minor.merge(nna_yes, on="folio", how="inner")
        .merge(su_yes, on="folio", how="inner")
        .drop_duplicates()
    )

    count = final_hh["folio"].nunique()
    return pd.DataFrame({"households_count": [int(count)]})