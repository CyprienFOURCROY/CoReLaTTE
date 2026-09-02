def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_se = tables["ii_se"]

    # Step 1: Identify households with at least one adult (edad >= 18)
    adults = df_portad[df_portad["edad"] >= 18]
    hh_with_adult = set(adults["folio"].unique())

    # Step 2: Households with positive reported value for electronic devices
    # ah04e_2: Value electronic device (float, can be nan)
    # ah04e_1: 1=Yes, 8=DK (we want only 1)
    df_ah_elec = df_ah[(df_ah["ah04e_1"] == 1) & (df_ah["ah04e_2"].notna()) & (df_ah["ah04e_2"] > 0)]

    # Step 3: Restrict to households with at least one adult
    df_ah_elec = df_ah_elec[df_ah_elec["folio"].isin(hh_with_adult)]

    # Step 4: For each household, get the maximum reported value for electronic devices
    max_elec_by_hh = df_ah_elec.groupby("folio")["ah04e_2"].max().reset_index()

    # Step 5: Identify households that reported a household member’s death in the last five years
    # se01a: 1=Yes, 3=No
    hh_death = set(df_se[df_se["se01a"] == 1]["folio"].unique())

    # Step 6: For households with max_elec_by_hh, mark if they reported a death
    max_elec_by_hh["death"] = max_elec_by_hh["folio"].isin(hh_death)

    # Step 7: Compute averages
    avg_all = max_elec_by_hh["ah04e_2"].mean()
    avg_death = max_elec_by_hh[max_elec_by_hh["death"]]["ah04e_2"].mean()

    # Step 8: Compare
    result = avg_death > avg_all

    return pd.DataFrame({
        "avg_death": [avg_death],
        "avg_all": [avg_all],
        "is_avg_death_higher": [result]
    })