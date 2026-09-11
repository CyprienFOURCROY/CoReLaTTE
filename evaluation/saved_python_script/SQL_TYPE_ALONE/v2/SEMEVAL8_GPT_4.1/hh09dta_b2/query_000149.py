def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]

    # Step 1: Households in Oaxaca (ent == 20) with at least one adult (edad >= 18)
    df_adults_oaxaca = df_portad[(df_portad["ent"] == 20) & (df_portad["edad"] >= 18)]
    oaxaca_adult_households = set(df_adults_oaxaca["folio"].unique())

    # Step 2: Households that received Liconsa milk in last 12 months (in03a == 1)
    df_liconsa = df_in[df_in["in03a"] == 1]
    liconsa_households = set(df_liconsa["folio"].unique())

    # Step 3: Intersection: Households in Oaxaca with at least one adult and received Liconsa milk
    eligible_households = oaxaca_adult_households & liconsa_households

    # Step 4: For these households, check if at least one member owns a motor vehicle (ah03d == 1)
    df_ah_eligible = df_ah[df_ah["folio"].isin(eligible_households)]
    owns_motor_vehicle = df_ah_eligible.groupby("folio")["ah03d"].apply(lambda x: (x == 1).any())
    # True: at least one member owns a motor vehicle, False: none own

    # Step 5: Count households by ownership status
    counts = owns_motor_vehicle.value_counts().rename_axis("owns_motor_vehicle").reset_index(name="num_households")
    # Convert boolean to "Yes"/"No" for clarity
    counts["owns_motor_vehicle"] = counts["owns_motor_vehicle"].map({True: "Yes", False: "No"})

    return counts