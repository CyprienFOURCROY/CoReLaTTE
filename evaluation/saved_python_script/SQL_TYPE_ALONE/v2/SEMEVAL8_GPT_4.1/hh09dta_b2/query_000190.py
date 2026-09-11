def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]

    # Step 1: Get Oaxaca households (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20.0].copy()

    # Step 2: Compute household average age for Oaxaca
    oaxaca_portad["edad"] = oaxaca_portad["edad"].astype(float)
    hh_avg_age = oaxaca_portad.groupby("folio")["edad"].mean().reset_index()
    hh_avg_age.columns = ["folio", "hh_avg_age"]

    # Step 3: Compute overall Oaxaca household average age
    overall_oaxaca_avg_age = hh_avg_age["hh_avg_age"].mean()

    # Step 4: Keep only households with avg age > overall Oaxaca avg
    hh_above_avg = hh_avg_age[hh_avg_age["hh_avg_age"] > overall_oaxaca_avg_age]

    # Step 5: Households in Oaxaca with Liconsa milk in last 12 months (in03a == 1)
    oaxaca_in = df_in[df_in["folio"].isin(hh_above_avg["folio"])]
    liconsa_hh = oaxaca_in[oaxaca_in["in03a"] == 1.0]["folio"].unique()

    # Step 6: For these households, get total value of electronic devices (ah04e_2)
    # Need to sum across all members in the household
    ah_oaxaca = df_ah[df_ah["folio"].isin(liconsa_hh)]
    # Only count values where ah04e_2 is not null
    ah_oaxaca_valid = ah_oaxaca[~ah_oaxaca["ah04e_2"].isnull()]
    # Sum per household
    hh_electronic_value = ah_oaxaca_valid.groupby("folio")["ah04e_2"].sum().reset_index()
    hh_electronic_value.columns = ["folio", "total_electronic_value"]

    # Step 7: Number of households meeting all criteria
    n_households = hh_electronic_value["folio"].nunique()

    # Step 8: Average total value of electronic devices
    if n_households > 0:
        avg_electronic_value = hh_electronic_value["total_electronic_value"].mean()
    else:
        avg_electronic_value = np.nan

    return pd.DataFrame({
        "average_total_electronic_value": [avg_electronic_value],
        "num_households": [n_households]
    })