def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]
    df_su = tables["ii_su"]

    # 1. Households in Oaxaca (ent == 20)
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"].unique()

    # 2. Households that use a plot of land for farming (su01 == 1)
    su_oaxaca = df_su[(df_su["folio"].isin(oaxaca_folios)) & (df_su["su01"] == 1.0)]
    folios_farming = su_oaxaca["folio"].unique()

    # 3. Merge with ah for asset values (ah04f_2: Value wash machine/stove)
    # Only keep one record per household (since asset is household-level)
    ah_farming = df_ah[df_ah["folio"].isin(folios_farming)]
    # For each household, get the max value of ah04f_2 (in case of multiple individuals)
    ah_farming = ah_farming.groupby("folio", as_index=False)["ah04f_2"].max()

    # 4. Merge with se for crop loss in last 5 years (se01e: lost total crop, 1=Yes, 3=No)
    se_farming = df_se[df_se["folio"].isin(folios_farming)][["folio", "se01e"]]

    # Merge all together
    merged = ah_farming.merge(se_farming, on="folio", how="left")

    # 5. Split into two groups: lost crop (se01e==1), did not lose crop (se01e==3)
    lost_crop = merged[merged["se01e"] == 1.0]
    not_lost_crop = merged[merged["se01e"] == 3.0]

    # 6. Compute average value of washing machine/stove among those that DID lose crop
    avg_lost_crop = lost_crop["ah04f_2"].dropna().mean()

    # 7. Among those that did NOT lose crop, keep only those with value > avg_lost_crop
    filtered = not_lost_crop[not_lost_crop["ah04f_2"] > avg_lost_crop]

    # 8. Compute average value for this group
    avg_value = filtered["ah04f_2"].dropna().mean()

    return pd.DataFrame({"average_wash_machine_stove_value": [avg_value]})