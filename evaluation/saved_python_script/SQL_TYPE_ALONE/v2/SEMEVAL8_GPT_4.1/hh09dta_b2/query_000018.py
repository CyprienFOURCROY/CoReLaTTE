def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_inr = tables["ii_inr"]

    # 1. Households in Oaxaca (ent == 20)
    df_portad_oax = df_portad[df_portad["ent"] == 20.0]

    # 2. Households with at least one adult (edad >= 18)
    adults = df_portad_oax[df_portad_oax["edad"] >= 18]
    hh_with_adult = adults["folio"].unique()

    # 3. Households that produced/sold eggs in last 12 months (inr02d == 1)
    df_inr_eggs = df_inr[df_inr["inr02d"] == 1.0]
    hh_with_eggs = df_inr_eggs["folio"].unique()

    # 4. Households where a member owns/shares a non-ag business (nna01 == 1)
    df_nna_nonag = df_nna[df_nna["nna01"] == 1.0]
    hh_with_nonag = df_nna_nonag["folio"].unique()

    # 5. Intersection of all three conditions
    eligible_hh = set(hh_with_adult) & set(hh_with_eggs) & set(hh_with_nonag)

    # 6. For these households, get the average of nna02 (number of non-ag businesses owned/shared in last 12 months)
    df_nna_eligible = df_nna[df_nna["folio"].isin(eligible_hh)]

    # Only consider non-missing nna02
    avg_nna02 = df_nna_eligible["nna02"].dropna().mean()

    return pd.DataFrame({"average_nonag_businesses": [avg_nna02]})