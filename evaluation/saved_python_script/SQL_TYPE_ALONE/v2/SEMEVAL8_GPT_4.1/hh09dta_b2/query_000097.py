def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_vlh = tables["ii_vlh"]

    # Households in Oaxaca (ent==20) with at least one member who owns a motor vehicle (ah03d==1)
    df_ah_mv = df_ah[df_ah["ah03d"] == 1.0]
    oaxaca_folios = df_portad[df_portad["ent"] == 20.0]["folio"].unique()
    oaxaca_mv_folios = np.intersect1d(df_ah_mv["folio"].unique(), oaxaca_folios)

    # Households outside Oaxaca with at least one member who owns a motor vehicle
    non_oaxaca_folios = df_portad[df_portad["ent"] != 20.0]["folio"].unique()
    non_oaxaca_mv_folios = np.intersect1d(df_ah_mv["folio"].unique(), non_oaxaca_folios)

    # For each household, get their vlh04 (feel safe at home) score
    # Only keep one row per household (since vlh is at household level)
    df_vlh_mv = df_vlh[df_vlh["folio"].isin(np.concatenate([oaxaca_mv_folios, non_oaxaca_mv_folios]))][["folio", "vlh04"]].drop_duplicates("folio")
    # Remove missing vlh04
    df_vlh_mv = df_vlh_mv[~df_vlh_mv["vlh04"].isna()]

    # Compute average vlh04 among non-Oaxaca, motor vehicle households
    avg_non_oaxaca = df_vlh_mv[df_vlh_mv["folio"].isin(non_oaxaca_mv_folios)]["vlh04"].mean()

    # Oaxaca, motor vehicle households with vlh04 > avg_non_oaxaca
    df_oaxaca_mv = df_vlh_mv[
        (df_vlh_mv["folio"].isin(oaxaca_mv_folios)) &
        (df_vlh_mv["vlh04"] > avg_non_oaxaca)
    ].copy()

    # Sort from most to least unsafe (highest to lowest vlh04)
    df_oaxaca_mv = df_oaxaca_mv.sort_values("vlh04", ascending=False)

    # Return folio and vlh04
    return df_oaxaca_mv[["folio", "vlh04"]].reset_index(drop=True)