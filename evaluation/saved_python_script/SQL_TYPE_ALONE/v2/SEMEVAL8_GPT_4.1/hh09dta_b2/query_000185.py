def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]

    # 1. Filter Oaxaca households (ent == 20)
    df_portad_oax = df_portad[df_portad["ent"] == 20.0]

    # 2. Filter adults (edad >= 18)
    df_portad_oax_adults = df_portad_oax[df_portad_oax["edad"] >= 18]

    # 3. Find households that reported producing/selling eggs in last 12 months (inr02d == 1)
    df_inr_eggs = df_inr[df_inr["inr02d"] == 1.0]

    # 4. Get Oaxaca households that are in both sets (by folio)
    # Only keep households with at least one adult
    oax_adult_folios = set(df_portad_oax_adults["folio"])
    eggs_folios = set(df_inr_eggs["folio"])
    target_folios = oax_adult_folios & eggs_folios

    if not target_folios:
        return pd.DataFrame({"average_age_oldest_member": [np.nan]})

    # 5. For each household, get the oldest member's age
    df_portad_oax_target = df_portad_oax[df_portad_oax["folio"].isin(target_folios)]
    oldest_ages = df_portad_oax_target.groupby("folio")["edad"].max()

    # 6. Only keep households with at least one adult (already filtered above)
    # 7. Compute the average of the oldest member's age
    avg_age = oldest_ages.mean()

    return pd.DataFrame({"average_age_oldest_member": [avg_age]})