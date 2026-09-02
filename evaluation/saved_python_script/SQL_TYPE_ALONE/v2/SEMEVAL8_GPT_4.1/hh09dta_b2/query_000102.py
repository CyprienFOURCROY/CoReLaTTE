def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]
    df_in = tables["ii_in"]

    # 1. Filter Oaxaca (20) or Puebla (21)
    df_portad_sub = df_portad[df_portad["ent"].isin([20.0, 21.0])][["folio", "ent"]]

    # 2. Households that use a plot/land for farming (su01 == 1)
    df_su_sub = df_su[df_su["su01"] == 1.0][["folio"]]

    # 3. Households that own/share a non-ag business (nna01 == 1)
    df_nna_sub = df_nna[df_nna["nna01"] == 1.0][["folio"]]

    # 4. Merge to get eligible households
    eligible = (
        df_portad_sub
        .merge(df_su_sub, on="folio")
        .merge(df_nna_sub, on="folio")
    )

    # 5. Get direct payment from "Other Government Program" (in02a10)
    df_in_sub = df_in[["folio", "in02a10"]]

    # 6. Merge eligible with payments
    eligible = eligible.merge(df_in_sub, on="folio")

    # 7. Only positive direct payments
    eligible = eligible[eligible["in02a10"].notna() & (eligible["in02a10"] > 0)]

    # 8. Compute average in02a10 for land-using households in Oaxaca/Puebla
    #    (regardless of business ownership)
    land_users = (
        df_portad_sub
        .merge(df_su_sub, on="folio")
        .merge(df_in_sub, on="folio")
    )
    land_users = land_users[land_users["in02a10"].notna() & (land_users["in02a10"] > 0)]
    avg_payment = land_users["in02a10"].mean()

    # 9. Filter for above average
    eligible = eligible[eligible["in02a10"] > avg_payment]

    # 10. Sort by payment descending
    eligible = eligible.sort_values("in02a10", ascending=False)

    # 11. Return folio and amount received
    return eligible[["folio", "in02a10"]].reset_index(drop=True)