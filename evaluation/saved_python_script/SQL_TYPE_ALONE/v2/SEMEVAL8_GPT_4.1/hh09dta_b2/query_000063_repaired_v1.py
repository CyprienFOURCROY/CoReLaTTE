def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_in = tables["ii_in"]

    # 1. Adults (18+) in Oaxaca (ent==20)
    adults_oaxaca = df_portad[(df_portad["edad"] >= 18) & (df_portad["ent"] == 20)]

    # 2. Households that own/share a non-ag business (nna01==1)
    nna_own = df_nna[df_nna["nna01"] == 1.0]

    # 3. Merge to get adults in such households
    adults_oaxaca_nna = adults_oaxaca.merge(nna_own[["folio"]], on="folio", how="inner")

    # 4. Households that received a positive amount directly from an Other Government Program (in02a10 > 0)
    df_in_pos = df_in[df_in["in02a10"].notna() & (df_in["in02a10"] > 0)]

    # 5. Merge to get only those adults in such households
    adults_final = adults_oaxaca_nna.merge(df_in_pos[["folio"]], on="folio", how="inner")

    # 6. Compute average age of these adults
    avg_age = adults_final["edad"].mean()

    # 7. Select those older than the average
    adults_older = adults_final[adults_final["edad"] > avg_age]

    # 8. Return the count
    return pd.DataFrame({"count": [adults_older.shape[0]]})