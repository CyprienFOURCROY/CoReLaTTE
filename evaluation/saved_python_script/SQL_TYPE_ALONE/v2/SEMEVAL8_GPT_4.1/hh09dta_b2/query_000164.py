def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]

    # 1. Filter for Oaxaca (ent == 20)
    df_portad_oax = df_portad[df_portad["ent"] == 20.0]

    # 2. Adult household heads: assume household head is ls == '01' (string, as in sample), adult is edad >= 18
    df_portad_oax_adult_head = df_portad_oax[(df_portad_oax["ls"] == '01') & (df_portad_oax["edad"] >= 18)]

    # 3. Merge with ii_ah on folio and ls
    df_ah = df_ah.copy()
    df_ah["ls"] = df_ah["ls"].astype(str).str.zfill(2)
    df_merged = df_portad_oax_adult_head.merge(df_ah, on=["folio", "ls"], how="inner")

    # 4. "No had entered force robbery in the household since 2005?" = ah04e_1 == 1 and ah04e_2 > 0
    # But the question is about "No" to "No had entered force robbery in the household since 2005?"
    # From metadata: ah04e_1 is "Value electronic device?" (not the robbery question)
    # The robbery question is in ii_vlh: vlh12a_c == 3 means "No had entered force rob in HH since 2005?"
    # So, need to merge with ii_vlh on folio, and filter vlh12a_c == 3

    df_vlh = tables["ii_vlh"]
    df_vlh = df_vlh[["folio", "vlh12a_c"]]
    df_merged = df_merged.merge(df_vlh, on="folio", how="left")

    # Only keep those with vlh12a_c == 3 (answered "No" to "No had entered force robbery in the household since 2005?")
    df_merged = df_merged[df_merged["vlh12a_c"] == 3.0]

    # 5. Only those with positive value for electronic devices: ah04e_2 > 0
    df_merged = df_merged[df_merged["ah04e_2"].notna() & (df_merged["ah04e_2"] > 0)]

    # 6. Compute overall average for ah04e_2 in this group
    avg_electronic_value = df_merged["ah04e_2"].mean()

    # 7. Find those with ah04e_2 > average
    df_above_avg = df_merged[df_merged["ah04e_2"] > avg_electronic_value]

    # 8. Count and average age
    count = len(df_above_avg)
    avg_age = df_above_avg["edad"].mean() if count > 0 else np.nan

    return pd.DataFrame({
        "num_above_average": [count],
        "average_age": [avg_age]
    })