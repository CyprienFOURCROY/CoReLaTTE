def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]

    # 1. Households in Oaxaca (ent == 20)
    df_oax = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one adult (edad >= 18) and at least one minor (edad < 18)
    adults = df_oax[df_oax["edad"] >= 18].groupby("folio").size().rename("n_adults")
    minors = df_oax[df_oax["edad"] < 18].groupby("folio").size().rename("n_minors")
    hh_adults = set(adults[adults > 0].index)
    hh_minors = set(minors[minors > 0].index)
    hh_adult_minor = hh_adults & hh_minors

    # 3. Households where a member owns/shares a non-ag business (nna01 == 1)
    df_nna_oax = df_nna[df_nna["folio"].isin(df_oax["folio"])]
    hh_nonag = set(df_nna_oax[df_nna_oax["nna01"] == 1.0]["folio"])

    # 4. Households where a member uses a plot/land for sowing/farming/vegetable (su01 == 1)
    df_su_oax = df_su[df_su["folio"].isin(df_oax["folio"])]
    hh_plot = set(df_su_oax[df_su_oax["su01"] == 1.0]["folio"])

    # 5. Intersection of all conditions
    hh_final = hh_adult_minor & hh_nonag & hh_plot

    result = pd.DataFrame({"households": [len(hh_final)]})
    return result