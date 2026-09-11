def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_vlh = tables["ii_vlh"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20]

    # 2. Households with at least one adult (edad >= 18)
    adults = oaxaca_portad[oaxaca_portad["edad"] >= 18]
    hh_with_adult = adults["folio"].unique()

    # 3. Households that own/share a non-ag business (nna01 == 1)
    nna_oaxaca = df_nna[df_nna["folio"].isin(hh_with_adult)]
    nna_business = nna_oaxaca[nna_oaxaca["nna01"] == 1]
    hh_with_business = nna_business["folio"].unique()

    # 4. For these households, get vlh18a (total times entered rob house/business/parcel since 2005)
    vlh_oaxaca = df_vlh[df_vlh["folio"].isin(hh_with_business)]
    # Only keep one row per household (since folio is household id)
    vlh_oaxaca = vlh_oaxaca[["folio", "vlh18a"]].drop_duplicates("folio")

    # 5. Compute Oaxaca statewide average for vlh18a among households that own/share a non-ag business and have at least one adult
    # (i.e., among hh_with_business)
    # Exclude missing values (nan) for the average
    oaxaca_vlh18a = vlh_oaxaca["vlh18a"]
    statewide_avg = oaxaca_vlh18a.dropna().mean()

    # 6. Only consider households whose vlh18a >= statewide average (and not null)
    eligible = vlh_oaxaca[vlh_oaxaca["vlh18a"].notnull() & (vlh_oaxaca["vlh18a"] >= statewide_avg)]

    # 7. Compute the average number of times (vlh18a) for these households
    if not eligible.empty:
        avg_robbed = eligible["vlh18a"].mean()
    else:
        avg_robbed = np.nan

    return pd.DataFrame({"average_robberies_since_2005": [avg_robbed]})