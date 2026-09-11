def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_nna = tables["ii_nna"]

    # Step 1: Filter Oaxaca households (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20.0][["folio"]]

    # Step 2: Merge with ii_in to get direct amount from Other Government Program (in02a10)
    oaxaca_in = oaxaca_portad.merge(df_in[["folio", "in02a10"]], on="folio", how="left")

    # Step 3: Keep only households with positive direct amount from Other Government Program
    oaxaca_in_pos = oaxaca_in[(oaxaca_in["in02a10"].notna()) & (oaxaca_in["in02a10"] > 0)]

    # Step 4: Compute Oaxaca average among such recipients
    oaxaca_avg = oaxaca_in_pos["in02a10"].mean()

    # Step 5: Keep only those whose amount exceeds the Oaxaca average
    oaxaca_in_above_avg = oaxaca_in_pos[oaxaca_in_pos["in02a10"] > oaxaca_avg]

    # Step 6: Get folios of these households
    folios_above_avg = oaxaca_in_above_avg["folio"].unique()

    # Step 7: For these folios, get household size from ii_portad (count of rows per folio)
    hh_size = (
        df_portad[df_portad["folio"].isin(folios_above_avg)]
        .groupby("folio")
        .size()
        .rename("hh_size")
        .reset_index()
    )

    # Step 8: For these folios, get non-ag business ownership from ii_nna (nna01)
    # Use the first occurrence per folio (since nna01 is per household)
    nna_status = (
        df_nna[df_nna["folio"].isin(folios_above_avg)]
        .drop_duplicates("folio")
        .set_index("folio")["nna01"]
    )

    # Step 9: Merge household size and nna01
    merged = hh_size.set_index("folio").join(nna_status).reset_index()

    # Step 10: Classify as owns/shares non-ag business (nna01 == 1.0) or not (nna01 == 2.0)
    # Exclude missing nna01
    merged = merged[merged["nna01"].isin([1.0, 2.0])]

    # Step 11: Compute average household size for each group
    result = (
        merged.groupby("nna01")["hh_size"]
        .mean()
        .rename({1.0: "owns_nonag_business", 2.0: "does_not_own_nonag_business"})
        .rename_axis("group")
        .reset_index()
        .rename(columns={"hh_size": "average_household_size"})
    )

    # Map group codes to labels
    group_map = {1.0: "owns_nonag_business", 2.0: "does_not_own_nonag_business"}
    result["group"] = result["group"].map(group_map)

    return result[["group", "average_household_size"]]