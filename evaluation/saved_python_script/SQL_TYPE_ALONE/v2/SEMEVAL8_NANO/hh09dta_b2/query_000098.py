def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_su = tables["ii_su"]

    # Filter for states: Oaxaca (20) and Puebla (21)
    df_portad_filtered = df_portad[df_portad["ent"].isin([20, 21])]

    # Filter households that use a plot/land for sowing/farming (su01 == 1)
    df_su_land = df_su[df_su["su01"] == 1]

    # Merge households with land use info
    households_with_land = pd.merge(
        df_portad_filtered,
        df_su_land[["folio"]],
        on="folio",
        how="inner"
    )

    # Filter households that have at least one adult (edad >= 18)
    # First, get all individuals in these households
    df_individuals = df_portad[df_portad["folio"].isin(households_with_land["folio"])]
    # Group by folio to check for at least one adult
    adults_in_household = df_individuals.groupby("folio")["edad"].max().reset_index()
    adults_in_household = adults_in_household[adults_in_household["edad"] >= 18]
    households_with_adults = adults_in_household["folio"]

    # Filter households with at least one member owning a motor vehicle (ah03d == 1)
    df_ah_filtered = df_ah[
        (df_ah["folio"].isin(households_with_land["folio"])) &
        (df_ah["ah03d"] == 1)
    ]
    households_with_vehicle = df_ah_filtered["folio"].unique()

    # Final households: in land use households, with at least one adult, and with at least one member owning a vehicle
    final_households = households_with_land[
        households_with_land["folio"].isin(households_with_adults)
    ]
    final_households = final_households[
        final_households["folio"].isin(households_with_vehicle)
    ]

    # Get land-using households in the final set
    final_folios = final_households["folio"].unique()

    # Filter land-using households
    df_land_households = df_su[
        df_su["folio"].isin(final_folios)
    ]

    # Compute overall average of fuel expenses (su239) among these households
    # Merge with households to get folio info
    df_fuel = df_land_households[["folio", "su239"]]
    # Drop NaNs
    df_fuel = df_fuel.dropna(subset=["su239"])
    if df_fuel.empty:
        return pd.DataFrame({"count": [0]})

    overall_avg_fuel = df_fuel["su239"].mean()

    # Select households reporting fuel expenses above the overall average
    households_above_avg = df_fuel[
        df_fuel["su239"] > overall_avg_fuel
    ]["folio"].unique()

    # Count households in the final set that report above average fuel expenses
    count = len(households_above_avg)

    return pd.DataFrame({"count": [count]})