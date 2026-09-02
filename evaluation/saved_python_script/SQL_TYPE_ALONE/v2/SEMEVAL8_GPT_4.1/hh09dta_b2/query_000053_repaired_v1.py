def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]
    df_vlh = tables["ii_vlh"]

    # 1. Households that feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]]

    # 2. Households that have a member who owns/shares a non-ag business (nna01 == 1)
    df_nna_business = df_nna[df_nna["nna01"] == 1.0][["folio"]]

    # 3. Households that do NOT use a plot/land for sowing/farming (su01 == 3)
    df_su_no_plot = df_su[df_su["su01"] == 3.0][["folio"]]

    # 4. Merge all conditions on folio (household id)
    # Only keep folios that satisfy all three conditions
    folios_unsafe = set(df_vlh_unsafe["folio"])
    folios_business = set(df_nna_business["folio"])
    folios_no_plot = set(df_su_no_plot["folio"])
    folios_final = folios_unsafe & folios_business & folios_no_plot

    # 5. Get state for each folio
    df_portad_hh = df_portad[["folio", "ent"]].drop_duplicates()

    # Only keep folios that satisfy all conditions
    df_filtered = df_portad_hh[df_portad_hh["folio"].isin(folios_final)]

    # 6. Count number of such households per state
    state_counts = df_filtered.groupby("ent").size().reset_index(name="count")

    # 7. Compute average across all states
    avg_count = state_counts["count"].mean()

    # 8. Map state codes to names for Oaxaca (20) and Puebla (21)
    state_map = {20.0: "Oaxaca", 21.0: "Puebla"}

    # 9. For Oaxaca and Puebla, check if their count is below average
    result = []
    for state_code in [20.0, 21.0]:
        count = state_counts[state_counts["ent"] == state_code]["count"]
        if not count.empty and count.iloc[0] < avg_count:
            result.append({"state": state_map[state_code], "count": int(count.iloc[0])})

    return pd.DataFrame(result)